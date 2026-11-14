#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check bounded public release metadata without changing installed pins."""

import argparse
import fcntl
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
SCRIPT_ROOT = Path(__file__).resolve().parent
# Execute the declared source itself: -B would still accept unchecked sibling pyc.
METADATA_SOURCE = SCRIPT_ROOT / "ada_mcp/update_notice.py"
if not METADATA_SOURCE.is_file():
    METADATA_SOURCE = SCRIPT_ROOT.parent / "src/ada_mcp/update_notice.py"
metadata: dict[str, Any] = {
    "__name__": "_ada_mcp_update_notice",
    "__file__": str(METADATA_SOURCE),
}
_verified: dict[Path, bytes] = globals().get("__verified_sources__", {})
_metadata_bytes = _verified.get(METADATA_SOURCE)
if _metadata_bytes is None:
    _metadata_bytes = METADATA_SOURCE.read_bytes()
exec(compile(_metadata_bytes, str(METADATA_SOURCE), "exec"), metadata)
RELEASES: str = metadata["RELEASES"]
newer: Callable[[str, str], bool] = metadata["newer"]
parse_version: Callable[[object], tuple[object, tuple[str, ...] | None]] = metadata["parse_version"]

JSON = dict[str, Any]
API_URL = "https://api.github.com/repos/abuild-project/ada-mcp-server/releases?per_page=100"
DAY = 86400
MAX_FEED = 1024 * 1024
MAX_STATE = 16 * 1024
BUDGET = 2.0
MAX_RETRY_SECONDS = 10**12


class NoRedirects(urllib.request.HTTPRedirectHandler):
    """Keep metadata on the exact fixed HTTPS endpoint, without redirects."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def retry_deadline(retry_after: str, rate_reset: str, now: int) -> int | None:
    """Retain actual provider deadlines separately from our automatic daily TTL."""
    deadlines = []
    for value, relative in [(retry_after, True), (rate_reset, False)]:
        if len(value) > 128:
            continue
        try:
            if value.isascii() and value.isdigit() and len(value) <= 12:
                deadline = int(value) + (now if relative else 0)
            elif relative:
                date = parsedate_to_datetime(value)
                if date.tzinfo is None:
                    continue
                deadline = int(date.timestamp())
            else:
                continue
            if now < deadline <= now + MAX_RETRY_SECONDS:
                deadlines.append(deadline)
        except (ValueError, TypeError, OverflowError):
            continue
    return max(deadlines) if deadlines else None


def fetch_feed() -> JSON:
    """Read one bounded anonymous GitHub page; discard all release prose/assets."""
    request = urllib.request.Request(
        API_URL, headers={"Accept": "application/vnd.github+json", "User-Agent": "ada-mcp-updates"}
    )
    try:
        with urllib.request.build_opener(NoRedirects()).open(request, timeout=1.5) as response:
            if response.geturl() != API_URL:
                raise ValueError("unexpected metadata URL")
            data = response.read(MAX_FEED + 1)
            if len(data) > MAX_FEED:
                raise ValueError("release feed exceeds limit")
            entries = json.loads(data)
            if not isinstance(entries, list) or len(entries) > 100:
                raise ValueError("invalid release list")
            complete = len(entries) < 100 and 'rel="next"' not in response.headers.get("Link", "")
            versions = []
            for entry in entries:
                if not isinstance(entry, dict):
                    complete = False
                    continue
                if entry.get("draft") is True:
                    continue
                tag = entry.get("tag_name")
                try:
                    if not isinstance(tag, str) or not tag.startswith("v"):
                        raise ValueError("noncanonical tag")
                    _, prerelease = parse_version(tag[1:])
                    if (
                        entry.get("draft") is not False
                        or type(entry.get("prerelease")) is not bool
                        or entry["prerelease"] != (prerelease is not None)
                    ):
                        raise ValueError("inconsistent release metadata")
                except ValueError:
                    complete = False
                    continue
                versions.append(tag[1:])
            return {"status": "ok", "versions": versions, "complete": complete}
    except urllib.error.HTTPError as error:
        failure: JSON = {
            "status": "rate_limited" if error.code in {403, 429} else "offline",
        }
        if error.headers is not None:
            deadline = retry_deadline(
                error.headers.get("Retry-After", ""),
                error.headers.get("X-RateLimit-Reset", ""),
                int(time.time()),
            )
            if deadline is not None:
                failure["retry_until"] = deadline
        return failure
    except Exception:
        return {"status": "offline"}


def bounded_fetch() -> JSON:
    """Kill and reap the synchronous checker on a total DNS/connect/read deadline."""
    try:
        result = subprocess.run(
            [sys.executable, "-I", str(Path(__file__).resolve()), "fetch"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=BUDGET,
            check=True,
        )
        if len(result.stdout) > MAX_STATE:
            raise ValueError("oversized checker response")
        response: JSON = json.loads(result.stdout)
        if not isinstance(response, dict) or response.get("status") not in {
            "ok",
            "offline",
            "rate_limited",
        }:
            raise ValueError("invalid checker response")
        return response
    except Exception:
        return {"status": "offline"}


def private_file(path: Path, flags: int) -> int:
    """Open only an owner-private regular cache entry, refusing symbolic links."""
    descriptor = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    metadata = os.fstat(descriptor)
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or stat.S_IMODE(metadata.st_mode) & 0o077
    ):
        os.close(descriptor)
        raise ValueError("cache file is not private")
    return descriptor


def read_state(path: Path, channel: str, now: int) -> JSON:
    """Read a bounded channel-specific cache without trusting stored notices."""
    try:
        with os.fdopen(private_file(path, os.O_RDONLY), "rb") as stream:
            data = stream.read(MAX_STATE + 1)
        if len(data) > MAX_STATE:
            return {}
        state: JSON = json.loads(data)
        if (
            not isinstance(state, dict)
            or state.get("schema") != 1
            or state.get("channel") != channel
            or type(state.get("attempted_at")) is not int
            or not 0 <= state["attempted_at"] <= now
        ):
            return {}
        provider = state.get("provider_retry_until")
        if provider is not None and (
            type(provider) is not int
            or not 0 <= provider - state["attempted_at"] <= MAX_RETRY_SECONDS
        ):
            return {}
        if provider is None:
            state.pop("provider_retry_until", None)
        if state.get("checked_at") is not None:
            if (
                type(state["checked_at"]) is not int
                or not 0 <= state["checked_at"] <= state["attempted_at"]
                or type(state.get("complete")) is not bool
            ):
                return {}
            if state.get("candidate") is not None:
                _, prerelease = parse_version(state["candidate"])
                if channel == "stable" and prerelease is not None:
                    return {}
            if now - state["checked_at"] > 7 * DAY:
                state.pop("candidate", None)
                state.update(checked_at=None, complete=False)
        if state.get("last_status") not in {"ok", "offline", "rate_limited"}:
            return {}
        if type(state.get("next_check_at")) is not int or not state["attempted_at"] + DAY <= state[
            "next_check_at"
        ] <= max(state["attempted_at"] + 7 * DAY, provider or 0):
            return {}
        return state
    except (OSError, ValueError, TypeError):
        return {}


def write_state(path: Path, state: JSON) -> None:
    """Atomically replace only app cache state; never rewrite runtime/binding pins."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def summarize(state: JSON, installed: str, channel: str, now: int) -> JSON:
    """Distinguish advisory availability from unknown, offline and current states."""
    result: JSON = {"status": "unknown", "current_version": installed, "channel": channel}
    if not state:
        return result
    result["last_check"] = state["last_status"]
    result["checked_at"] = state.get("checked_at")
    result["next_check_at"] = state["next_check_at"]
    if state.get("provider_retry_until", 0) > now:
        result["blocked_until"] = state["provider_retry_until"]
    fresh = (
        state["last_status"] == "ok"
        and state.get("checked_at") is not None
        and now - state["attempted_at"] < DAY
    )
    result["freshness"] = "fresh" if fresh else "stale"
    candidate = state.get("candidate")
    if candidate and newer(candidate, installed):
        result["status"] = "available"
        result["update_notice"] = {
            "schema": 1,
            "current_version": installed,
            "available_version": candidate,
            "channel": channel,
            "checked_at": state["checked_at"],
            "freshness": result["freshness"],
            "release_url": RELEASES + candidate,
        }
    elif fresh and state.get("complete") is True:
        result["status"] = "up_to_date"
    elif state["last_status"] != "ok":
        result["status"] = state["last_status"]
    return result


def cached_result(
    state: JSON,
    installed: str,
    channel: str,
    now: int,
    *,
    refresh: bool,
    manual: bool,
    provider_until: int,
) -> JSON | None:
    """Manual requests bypass only local cooldowns, never a provider deadline."""
    result = summarize(state, installed, channel, now)
    if manual:
        result["check_performed"] = False
    if not refresh:
        return result
    if provider_until > now:
        result["blocked_until"] = provider_until
        if manual:
            result.update(status="blocked", reason="provider_retry_deadline")
        return result
    if not manual and state and now < state["next_check_at"]:
        return result
    return None


def provider_limit(cache: Path, now: int) -> int:
    """A deadline from this endpoint applies across both cached channels."""
    return max(
        int(read_state(cache / (channel + ".json"), channel, now).get("provider_retry_until", 0))
        for channel in ["stable", "prerelease"]
    )


def check_updates(
    installed: str, channel: str, cache: Path, *, refresh: bool = True, manual: bool = False
) -> JSON:
    """Cache automatic checks daily; allow one bounded explicit fresh request."""
    attempted = False
    try:
        _, prerelease = parse_version(installed)
        if channel == "auto":
            channel = "prerelease" if prerelease else "stable"
        if channel == "off":
            return {
                "status": "disabled",
                "current_version": installed,
                **({"check_performed": False} if manual else {}),
            }
        if channel not in {"stable", "prerelease"} or not cache.is_absolute():
            raise ValueError("invalid update policy")
        if not refresh and not cache.exists():
            return {"status": "unknown", "current_version": installed, "channel": channel}
        cache.mkdir(mode=0o700, parents=True, exist_ok=True)
        metadata = cache.lstat()
        if (
            not stat.S_ISDIR(metadata.st_mode)
            or metadata.st_uid != os.getuid()
            or stat.S_IMODE(metadata.st_mode) & 0o077
        ):
            raise ValueError("cache directory is not private")
        path = cache / (channel + ".json")
        now = int(time.time())
        state = read_state(path, channel, now)
        cached = cached_result(
            state,
            installed,
            channel,
            now,
            refresh=refresh,
            manual=manual,
            provider_until=provider_limit(cache, now),
        )
        if cached is not None:
            return cached
        descriptor = private_file(cache / "releases.lock", os.O_CREAT | os.O_RDWR)
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                result = summarize(state, installed, channel, now)
                if manual:
                    result.update(
                        status="unknown", reason="check_in_progress", check_performed=False
                    )
                return result
            state = read_state(path, channel, now)
            cached = cached_result(
                state,
                installed,
                channel,
                now,
                refresh=refresh,
                manual=manual,
                provider_until=provider_limit(cache, now),
            )
            if cached is not None:
                return cached
            attempted = True
            response = bounded_fetch()
            state.update(
                schema=1, channel=channel, attempted_at=now, last_status=response["status"]
            )
            state.pop("provider_retry_until", None)
            deadline = response.get("retry_until")
            if type(deadline) is int and now < deadline <= now + MAX_RETRY_SECONDS:
                state["provider_retry_until"] = deadline
            state["next_check_at"] = max(now + DAY, state.get("provider_retry_until", 0))
            if response["status"] == "ok":
                candidate = None
                for version in response["versions"]:
                    _, pre = parse_version(version)
                    if channel == "stable" and pre is not None:
                        continue
                    if candidate is None or newer(version, candidate):
                        candidate = version
                state.update(candidate=candidate, checked_at=now, complete=response["complete"])
            write_state(path, state)
            result = summarize(state, installed, channel, now)
            if manual:
                result["check_performed"] = True
            return result
        finally:
            os.close(descriptor)
    except Exception:
        return {
            "status": "unknown",
            "current_version": installed,
            "reason": "check_unavailable",
            **({"check_performed": attempted} if manual else {}),
        }


def main() -> None:
    """Print JSON status or a notice-only launcher snapshot, never protocol prose."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["fetch", "check", "status", "snapshot"])
    parser.add_argument("--manifest", type=Path, default=SCRIPT_ROOT / "runtime-manifest.json")
    parser.add_argument(
        "--channel",
        default=None,
        choices=["auto", "stable", "prerelease", "off"],
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=os.environ.get("ADA_MCP_UPDATE_CACHE", str(Path.home() / ".cache/ada-mcp")),
    )
    options = parser.parse_args()
    if options.mode == "fetch":
        print(json.dumps(fetch_feed()))
        return
    result: JSON = {"status": "unknown", "reason": "runtime_metadata_unavailable"}
    try:
        with options.manifest.open("rb") as stream:
            data = stream.read(256 * 1024 + 1)
        if len(data) > 256 * 1024:
            raise ValueError("oversized runtime metadata")
        installed = json.loads(data)["project_version"]
        result = check_updates(
            installed,
            options.channel
            or (
                "auto"
                if options.mode == "check"
                else os.environ.get("ADA_MCP_UPDATE_CHANNEL", "auto")
            ),
            options.cache,
            refresh=options.mode != "status",
            manual=options.mode == "check",
        )
    except Exception:
        pass
    if options.mode == "snapshot":
        if result.get("update_notice"):
            print(json.dumps(result["update_notice"], separators=(",", ":")))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

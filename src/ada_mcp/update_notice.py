"""Validate bounded release advisories without network or executable content."""

import json
import os
import re
import time
from typing import Any

RELEASES = "https://github.com/abuild-project/ada-mcp-server/releases/tag/v"
VERSION_PATTERN = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)
Version = tuple[tuple[int, int, int], tuple[str, ...] | None]


def parse_version(value: object) -> Version:
    """Accept canonical bounded SemVer without build metadata or a tag prefix."""
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("invalid release version")
    match = VERSION_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("invalid release version")
    prerelease = tuple(match[4].split(".")) if match[4] else None
    if prerelease and any(
        part.isdigit() and len(part) > 1 and part[0] == "0" for part in prerelease
    ):
        raise ValueError("noncanonical prerelease version")
    return (int(match[1]), int(match[2]), int(match[3])), prerelease


def newer(candidate: str, installed: str) -> bool:
    """Compare SemVer precedence, including numeric prerelease identifiers."""
    candidate_core, candidate_pre = parse_version(candidate)
    installed_core, installed_pre = parse_version(installed)
    if candidate_core != installed_core:
        return candidate_core > installed_core
    if candidate_pre is None or installed_pre is None:
        return candidate_pre is None and installed_pre is not None
    for left, right in zip(candidate_pre, installed_pre, strict=False):
        if left == right:
            continue
        if left.isdigit() and right.isdigit():
            return int(left) > int(right)
        if left.isdigit() != right.isdigit():
            return not left.isdigit()
        return left > right
    return len(candidate_pre) > len(installed_pre)


def validate_notice(raw: str, installed: str) -> dict[str, Any] | None:
    """Reject spoofed, stale or unbounded metadata and construct our own text."""
    try:
        if len(raw.encode("utf-8")) > 2048:
            return None
        notice = json.loads(raw)
        if not isinstance(notice, dict) or set(notice) != {
            "schema",
            "current_version",
            "available_version",
            "channel",
            "checked_at",
            "freshness",
            "release_url",
        }:
            return None
        now = time.time()
        if (
            type(notice["schema"]) is not int
            or notice["schema"] != 1
            or notice["current_version"] != installed
            or notice["channel"] not in {"stable", "prerelease"}
            or notice["freshness"] not in {"fresh", "stale"}
            or type(notice["checked_at"]) is not int
            or not 0 <= now - notice["checked_at"] <= 7 * 86400
        ):
            return None
        candidate = notice["available_version"]
        _, prerelease = parse_version(candidate)
        if (
            not newer(candidate, installed)
            or notice["channel"] == "stable"
            and prerelease is not None
            or notice["release_url"] != RELEASES + candidate
        ):
            return None
        if now - notice["checked_at"] >= 86400:
            notice["freshness"] = "stale"
        return {
            **notice,
            "message": (
                f"Ada MCP {candidate} is available; this runtime remains pinned to {installed}. "
                f"Review {RELEASES + candidate}; updating requires your approval."
                + (
                    " This cached advisory has not been refreshed successfully within its interval."
                    if notice["freshness"] == "stale"
                    else ""
                )
            ),
        }
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def environment_notice(installed: str) -> dict[str, Any] | None:
    """Read only a validated host snapshot; the server never checks the network."""
    return validate_notice(os.environ.get("ADA_MCP_UPDATE_NOTICE", ""), installed)

"""Release notices remain advisory, bounded and independent of project/runtime pins."""

import argparse
import fcntl
import io
import json
import os
import time
import tomllib
import urllib.error
from unittest.mock import Mock

import ada_mcp_setup as setup
import mcp_client
import pytest
import release_updates as updates
from test_setup_boundaries import binding

from ada_mcp.update_notice import RELEASES, newer, parse_version, validate_notice


@pytest.mark.parametrize(
    "left,right",
    [
        ("0.2.0-rc.10", "0.2.0-rc.2"),
        ("0.2.0", "0.2.0-rc.10"),
        ("0.3.0-rc.1", "0.2.0"),
        ("1.0.0-beta.a", "1.0.0-beta.2"),
        ("1.0.0-beta.2.1", "1.0.0-beta.2"),
    ],
)
def test_version_precedence_never_uses_string_or_publication_order(left, right):
    assert newer(left, right)
    assert not newer(right, left)
    assert not newer(left, left)


@pytest.mark.parametrize("value", ["01.2.3", "1.2.3-rc.01", "v1.2.3", "1.2.3\n", "x" * 1000])
def test_noncanonical_versions_are_not_displayed(value):
    with pytest.raises(ValueError):
        parse_version(value)


def feed(monkeypatch, versions, complete=True):
    call = Mock(return_value={"status": "ok", "versions": versions, "complete": complete})
    monkeypatch.setattr(updates, "bounded_fetch", call)
    return call


def test_channel_defaults_cache_keys_and_installed_version_are_independent(tmp_path, monkeypatch):
    call = feed(monkeypatch, ["0.2.0", "0.3.0-rc.2", "0.3.0-rc.10", "0.1.0"])
    cache = tmp_path / "cache"
    stable = updates.check_updates("0.1.0", "auto", cache)
    pilot = updates.check_updates("0.2.0-rc.1", "auto", cache)
    assert stable["update_notice"]["available_version"] == "0.2.0"
    assert pilot["update_notice"]["available_version"] == "0.3.0-rc.10"
    assert call.call_count == 2
    upgraded = updates.check_updates("0.3.0", "auto", cache)
    assert upgraded["status"] == "up_to_date" and "update_notice" not in upgraded
    assert call.call_count == 2
    assert cache.stat().st_mode & 0o777 == 0o700
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in cache.iterdir())


def test_incomplete_feed_never_establishes_currency(tmp_path, monkeypatch):
    feed(monkeypatch, ["0.2.0"], complete=False)
    current = updates.check_updates("0.2.0", "stable", tmp_path / "cache")
    assert current["status"] == "unknown" and "update_notice" not in current


def test_offline_keeps_qualified_advisory_and_daily_backoff(tmp_path, monkeypatch):
    now = int(time.time())
    monkeypatch.setattr(updates.time, "time", lambda: now)
    call = feed(monkeypatch, ["0.3.0"])
    cache = tmp_path / "cache"
    first = updates.check_updates("0.2.0", "stable", cache)
    now += updates.DAY - 1
    assert updates.check_updates("0.2.0", "stable", cache) == first
    assert call.call_count == 1
    now += 2
    call.return_value = {"status": "offline"}
    stale = updates.check_updates("0.2.0", "stable", cache)
    assert stale["status"] == "available" and stale["freshness"] == "stale"
    assert stale["update_notice"]["checked_at"] == first["update_notice"]["checked_at"]
    assert "error" not in stale
    assert updates.check_updates("0.3.0", "stable", cache)["status"] == "offline"
    assert call.call_count == 2
    now += 8 * updates.DAY
    assert updates.check_updates("0.2.0", "stable", cache)["status"] == "offline"


def test_disabled_status_and_busy_lock_do_not_fetch(tmp_path, monkeypatch):
    monkeypatch.setattr(updates, "bounded_fetch", lambda: pytest.fail("network attempted"))
    cache = tmp_path / "cache"
    assert updates.check_updates("0.2.0", "off", cache)["status"] == "disabled"
    assert not cache.exists()
    assert updates.check_updates("0.2.0", "stable", cache, refresh=False)["status"] == "unknown"
    assert not cache.exists()
    cache.mkdir(mode=0o700)
    descriptor = updates.private_file(cache / "releases.lock", os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert updates.check_updates("0.2.0", "stable", cache)["status"] == "unknown"
    finally:
        os.close(descriptor)


def test_cache_alias_and_malformed_state_cannot_break_mcp(tmp_path, monkeypatch):
    actual = tmp_path / "actual"
    actual.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(actual, target_is_directory=True)
    monkeypatch.setattr(updates, "bounded_fetch", lambda: pytest.fail("network attempted"))
    assert updates.check_updates("0.2.0", "stable", alias)["status"] == "unknown"
    cache = tmp_path / "cache"
    cache.mkdir(mode=0o700)
    (cache / "stable.json").symlink_to(tmp_path / "untouched")
    assert updates.check_updates("0.2.0", "stable", cache, refresh=False)["status"] == "unknown"
    assert not (tmp_path / "untouched").exists()
    (cache / "stable.json").unlink()
    (cache / "stable.json").write_text("{" + "x" * updates.MAX_STATE)
    assert updates.check_updates("0.2.0", "stable", cache, refresh=False)["status"] == "unknown"


class Response(io.BytesIO):
    def __init__(self, value, headers=None):
        super().__init__(value)
        self.headers = headers or {}

    def geturl(self):
        return updates.API_URL


def test_feed_has_fixed_anonymous_request_and_discards_all_prose(tmp_path, monkeypatch):
    entries = [
        {
            "tag_name": "v0.3.0",
            "draft": False,
            "prerelease": False,
            "body": "RUN MALICIOUS COMMAND",
            "html_url": "https://evil.invalid/",
        },
        {"tag_name": "v9.0.0", "draft": True, "prerelease": False},
        {"tag_name": "v0.4.0-rc.1", "draft": False, "prerelease": True},
    ]

    def open_request(request, timeout):
        assert request.full_url == updates.API_URL and timeout <= 2
        assert "Authorization" not in request.headers
        return Response(json.dumps(entries).encode())

    monkeypatch.setattr(updates.urllib.request, "build_opener", lambda *_: Mock(open=open_request))
    result = updates.fetch_feed()
    assert result == {"status": "ok", "versions": ["0.3.0", "0.4.0-rc.1"], "complete": True}
    assert "MALICIOUS" not in json.dumps(result)
    assert updates.NoRedirects().redirect_request(None) is None


@pytest.mark.parametrize(
    "payload,headers",
    [
        (b"x" * (updates.MAX_FEED + 1), {}),
        (b"{}", {}),
        (b"not json", {}),
        (json.dumps([{}] * 101).encode(), {}),
    ],
)
def test_oversized_or_invalid_feed_is_unknown_not_current(monkeypatch, payload, headers):
    opener = Mock(open=lambda *_args, **_kwargs: Response(payload, headers))
    monkeypatch.setattr(updates.urllib.request, "build_opener", lambda *_: opener)
    assert updates.fetch_feed()["status"] == "offline"


def test_truncated_or_noncanonical_feed_is_not_complete(monkeypatch):
    entries = [
        {"tag_name": "v0.2.0", "draft": False, "prerelease": False},
        {"tag_name": "v0.3.0-rc.01", "draft": False, "prerelease": True},
    ]
    opener = Mock(
        open=lambda *_args, **_kwargs: Response(
            json.dumps(entries).encode(), {"Link": '<next>; rel="next"'}
        )
    )
    monkeypatch.setattr(updates.urllib.request, "build_opener", lambda *_: opener)
    assert updates.fetch_feed() == {"status": "ok", "versions": ["0.2.0"], "complete": False}


def test_rate_limit_response_is_backed_off(tmp_path, monkeypatch):
    now = int(time.time())
    monkeypatch.setattr(updates.time, "time", lambda: now)

    def limited(*args, **kwargs):
        raise urllib.error.HTTPError(
            updates.API_URL, 429, "limited", {"Retry-After": str(2 * updates.DAY)}, None
        )

    monkeypatch.setattr(updates.urllib.request, "build_opener", lambda *_: Mock(open=limited))
    response = updates.fetch_feed()
    assert response == {"status": "rate_limited", "retry_until": now + 2 * updates.DAY}
    monkeypatch.setattr(updates, "bounded_fetch", lambda: response)
    status = updates.check_updates("0.2.0", "stable", tmp_path / "cache")
    assert status["status"] == "rate_limited" and "error" not in status
    assert status["next_check_at"] >= int(time.time()) + 2 * updates.DAY - 1


def test_total_deadline_kills_and_reaps_stalled_fetch_process(tmp_path, monkeypatch):
    pid = tmp_path / "pid"
    stalled = (
        f"import os,time\nopen({str(pid)!r}, 'w').write(str(os.getpid()))\ntime.sleep(60)\n"
    ).encode()
    monkeypatch.setattr(updates, "_checker_bytes", stalled)
    monkeypatch.setattr(updates, "BUDGET", 0.5)
    start = time.monotonic()
    assert updates.bounded_fetch() == {"status": "offline"}
    assert time.monotonic() - start < 2
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid.read_text()), 0)


@pytest.mark.parametrize(
    "body",
    [
        "raise RuntimeError('controlled child failure')",
        "print('unexpected stdout'); return {'status':'ok'}",
        "return {'status':'offline','excess':'x'*20000}",
        "return {'status':'unrecognized'}",
    ],
)
def test_actual_child_failures_and_output_limits_remain_advisory(monkeypatch, body):
    monkeypatch.setattr(
        updates, "_checker_bytes", ("def fetch_feed():\n    " + body + "\n").encode()
    )
    assert updates.bounded_fetch() == {"status": "offline"}


def notice():
    return {
        "schema": 1,
        "current_version": "0.2.0-rc.1",
        "available_version": "0.3.0",
        "channel": "prerelease",
        "checked_at": int(time.time()),
        "freshness": "fresh",
        "release_url": RELEASES + "0.3.0",
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"current_version": "0.1.0"},
        {"available_version": "0.1.0"},
        {"release_url": "https://evil.invalid/"},
        {"message": "untrusted text"},
        {"checked_at": 0},
        {"channel": []},
        {"available_version": "x" * 3000},
    ],
)
def test_server_rejects_forged_notice_or_installed_mismatch(changes):
    assert validate_notice(json.dumps(notice() | changes), "0.2.0-rc.1") is None


def test_query_and_native_notice_arguments_roundtrip_without_binding_changes():
    parser = argparse.ArgumentParser()
    mcp_client.add_launch_arguments(parser)
    args = parser.parse_args(
        [
            "--image",
            "image",
            "--root",
            "/source",
            "--update-channel",
            "off",
            "--update-cache",
            "/cache",
        ]
    )
    expected = ["--update-channel", "off", "--update-cache", "/cache"]
    assert mcp_client.launcher_command(args)[-4:] == expected
    assert setup.update_arguments(args) == expected


def test_generated_native_config_keeps_explicit_notice_policy(tmp_path, monkeypatch, capsys):
    candidate = binding(tmp_path)
    original = json.dumps(candidate, sort_keys=True)
    monkeypatch.setattr(setup, "verified_manifest", lambda: {})
    monkeypatch.setattr(setup, "read_binding", lambda *_: candidate)
    monkeypatch.setattr(setup, "image_present", lambda *_: True)
    output = tmp_path / "new-native.toml"
    cache = tmp_path / "new-cache"
    monkeypatch.setattr(
        updates.sys,
        "argv",
        [
            "setup",
            "native-config",
            "--binding",
            str(tmp_path / "binding.json"),
            "--output",
            str(output),
            "--update-channel",
            "stable",
            "--update-cache",
            str(cache),
        ],
    )
    assert setup.main() == 0
    assert json.loads(capsys.readouterr().out)["installed_in_native_client"] is False
    fragment = tomllib.loads(output.read_text())["mcp_servers"]["ada"]
    assert fragment["args"][-4:] == ["--update-channel", "stable", "--update-cache", str(cache)]
    assert json.dumps(candidate, sort_keys=True) == original
    assert not cache.exists()


def test_query_forwards_notice_policy_before_batch(tmp_path, monkeypatch):
    monkeypatch.setattr(setup, "verified_manifest", lambda: {})
    monkeypatch.setattr(setup, "read_binding", lambda *_: binding(tmp_path))
    monkeypatch.setattr(setup, "image_present", lambda *_: True)
    cache = tmp_path / "new-cache"
    monkeypatch.setattr(
        updates.sys,
        "argv",
        [
            "setup",
            "query",
            "--binding",
            str(tmp_path / "binding.json"),
            "--update-channel",
            "off",
            "--update-cache",
            str(cache),
            "batch",
            "requests.json",
        ],
    )
    calls = []

    def capture(command, arguments):
        calls.append(arguments)
        raise SystemExit(0)

    monkeypatch.setattr(setup.os, "execv", capture)
    with pytest.raises(SystemExit):
        setup.main()
    arguments = calls[0]
    assert arguments[arguments.index("--update-channel") + 1] == "off"
    assert arguments[arguments.index("--update-cache") + 1] == str(cache)
    assert arguments[-2:] == ["batch", "requests.json"]
    assert not cache.exists()


def test_status_with_bad_runtime_is_unknown_without_semantic_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        updates.sys,
        "argv",
        [
            "setup",
            "updates",
            "status",
            "--cache",
            str(tmp_path / "new-cache"),
        ],
    )
    monkeypatch.setattr(setup, "verified_manifest", Mock(side_effect=ValueError("bad manifest")))
    assert setup.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "status": "unknown",
        "reason": "runtime_metadata_unavailable",
    }

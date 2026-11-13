"""Explicit searches refresh metadata without installation consent or policy edits."""

import fcntl
import json
import os
import time
from datetime import UTC, datetime
from email.utils import format_datetime
from unittest.mock import Mock

import ada_mcp_setup as setup
import pytest
import release_updates as updates
from test_release_updates import feed


def test_manual_search_observes_new_release_now_without_installing(tmp_path, monkeypatch):
    now = int(time.time())
    monkeypatch.setattr(updates.time, "time", lambda: now)
    immutable = [tmp_path / name for name in ["old-runtime", "old-binding", "skill", "native.toml"]]
    for path in immutable:
        path.write_bytes(b"old verified installation")
    before = {path: path.read_bytes() for path in immutable}
    call = feed(monkeypatch, ["0.2.0"])
    cache = tmp_path / "private-cache"
    assert updates.check_updates("0.2.0", "stable", cache)["status"] == "up_to_date"
    call.return_value = {"status": "ok", "versions": ["0.3.0"], "complete": True}
    assert updates.check_updates("0.2.0", "stable", cache)["status"] == "up_to_date"
    assert call.call_count == 1
    cached_bytes = {path: path.read_bytes() for path in cache.iterdir()}
    assert updates.check_updates("0.2.0", "stable", cache, refresh=False)["status"] == "up_to_date"
    assert {path: path.read_bytes() for path in cache.iterdir()} == cached_bytes
    assert call.call_count == 1
    searched = updates.check_updates("0.2.0", "stable", cache, manual=True)
    assert searched["check_performed"] is True and searched["status"] == "available"
    assert searched["update_notice"]["available_version"] == "0.3.0"
    assert call.call_count == 2
    assert updates.check_updates("0.2.0", "stable", cache)["status"] == "available"
    assert call.call_count == 2
    call.return_value = {"status": "ok", "versions": ["0.2.0"], "complete": True}
    assert updates.check_updates("0.2.0", "stable", cache, manual=True)["status"] == "up_to_date"
    assert call.call_count == 3
    assert {path: path.read_bytes() for path in immutable} == before


def test_manual_retry_bypasses_artificial_offline_cooldown(tmp_path, monkeypatch):
    call = Mock(return_value={"status": "offline"})
    monkeypatch.setattr(updates, "bounded_fetch", call)
    cache = tmp_path / "private-cache"
    assert updates.check_updates("0.2.0", "stable", cache)["status"] == "offline"
    assert updates.check_updates("0.2.0", "stable", cache)["status"] == "offline"
    assert call.call_count == 1
    call.return_value = {"status": "ok", "versions": ["0.3.0"], "complete": True}
    assert updates.check_updates("0.2.0", "stable", cache, manual=True)["status"] == "available"
    assert call.call_count == 2


@pytest.mark.parametrize("header", ["seconds", "date", "reset"])
def test_provider_deadline_is_exact_and_shared_across_channels(tmp_path, monkeypatch, header):
    now = int(time.time())
    monkeypatch.setattr(updates.time, "time", lambda: now)
    target = now + 45
    retry = "45" if header == "seconds" else format_datetime(datetime.fromtimestamp(target, UTC))
    deadline = updates.retry_deadline(
        "" if header == "reset" else retry, str(target) if header == "reset" else "", now
    )
    assert deadline == target
    call = Mock(return_value={"status": "rate_limited", "retry_until": deadline})
    monkeypatch.setattr(updates, "bounded_fetch", call)
    cache = tmp_path / "private-cache"
    limited = updates.check_updates("0.2.0", "stable", cache, manual=True)
    assert limited["status"] == "rate_limited" and limited["blocked_until"] == target
    for channel in ["stable", "prerelease"]:
        blocked = updates.check_updates("0.2.0", channel, cache, manual=True)
        assert blocked["status"] == "blocked" and blocked["blocked_until"] == target
        assert blocked["check_performed"] is False
    assert call.call_count == 1
    now += 46
    call.return_value = {"status": "ok", "versions": ["0.3.0"], "complete": True}
    assert updates.check_updates("0.2.0", "stable", cache, manual=True)["status"] == "available"
    assert call.call_count == 2


def test_provider_limit_outlives_expired_advisory(tmp_path, monkeypatch):
    now = int(time.time())
    monkeypatch.setattr(updates.time, "time", lambda: now)
    call = feed(monkeypatch, ["0.3.0"])
    cache = tmp_path / "private-cache"
    updates.check_updates("0.2.0", "stable", cache)
    deadline = now + 10 * updates.DAY
    call.return_value = {"status": "rate_limited", "retry_until": deadline}
    updates.check_updates("0.2.0", "stable", cache, manual=True)
    now += 8 * updates.DAY
    blocked = updates.check_updates("0.2.0", "stable", cache, manual=True)
    assert blocked["status"] == "blocked" and blocked["blocked_until"] == deadline
    assert "update_notice" not in blocked and call.call_count == 2


def test_manual_lock_contention_cannot_claim_a_fresh_current_result(tmp_path, monkeypatch):
    call = feed(monkeypatch, ["0.2.0"])
    cache = tmp_path / "private-cache"
    updates.check_updates("0.2.0", "stable", cache)
    descriptor = updates.private_file(cache / "releases.lock", os.O_RDWR)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = updates.check_updates("0.2.0", "stable", cache, manual=True)
        assert result["status"] == "unknown" and result["reason"] == "check_in_progress"
        assert result["check_performed"] is False and call.call_count == 1
    finally:
        os.close(descriptor)


@pytest.mark.parametrize(
    "mode,expected_channel,manual",
    [
        ("check", "auto", True),
        ("status", "off", False),
        ("snapshot", "off", False),
    ],
)
def test_direct_cli_one_shot_search_preserves_automatic_optout(
    tmp_path, monkeypatch, capsys, mode, expected_channel, manual
):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"project_version": "0.2.0"}))
    call = Mock(return_value={"status": "unknown"})
    monkeypatch.setattr(updates, "check_updates", call)
    monkeypatch.setattr(
        updates.sys,
        "argv",
        [
            "checker",
            mode,
            "--manifest",
            str(manifest),
            "--cache",
            str(tmp_path / "private-cache"),
        ],
    )
    updates.main()
    capsys.readouterr()
    assert call.call_args.args[1] == expected_channel
    assert call.call_args.kwargs["manual"] is manual
    assert os.environ["ADA_MCP_UPDATE_CHANNEL"] == "off"


@pytest.mark.parametrize(
    "action,channel,manual", [("check", "auto", True), ("status", "off", False)]
)
def test_setup_cli_requests_fresh_search_without_persisting_policy(
    tmp_path, monkeypatch, capsys, action, channel, manual
):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "release_updates.py").write_text(
        "def check_updates(version, channel, cache, *, refresh, manual):\n"
        "    return {'status': 'unknown', 'channel': channel, 'manual': manual}\n"
    )
    monkeypatch.setattr(setup, "SCRIPT_ROOT", scripts)
    monkeypatch.setattr(setup, "verified_manifest", lambda: {"project_version": "0.2.0"})
    monkeypatch.setattr(
        updates.sys,
        "argv",
        [
            "setup",
            "updates",
            action,
            "--cache",
            str(tmp_path / "private-cache"),
        ],
    )
    assert setup.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["channel"] == channel and result["manual"] is manual
    assert os.environ["ADA_MCP_UPDATE_CHANNEL"] == "off"


def test_explicit_off_still_disables_manual_search(tmp_path, monkeypatch):
    monkeypatch.setattr(updates, "bounded_fetch", lambda: pytest.fail("network attempted"))
    cache = tmp_path / "unused-cache"
    assert updates.check_updates("0.2.0", "off", cache, manual=True) == {
        "status": "disabled",
        "current_version": "0.2.0",
        "check_performed": False,
    }
    assert not cache.exists()

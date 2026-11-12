"""Permission-only controls with synthetic data; no actual Mac/Docker evidence."""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import mac_smoke
import mcp_client
import pytest


@pytest.fixture
def permissive_parent(tmp_path):
    parent = tmp_path / "public-parent"
    saved = os.umask(0o022)
    try:
        parent.mkdir(mode=0o755)
        yield parent
    finally:
        os.umask(saved)


def test_real_session_logs_are_private_before_open_and_normal_child_eof(
    permissive_parent, monkeypatch
):
    root = permissive_parent / "new-parent/logs"
    original_open = Path.open
    checked = []

    def checked_open(path, *args, **kwargs):
        if path.parent == root:
            assert stat.S_IMODE(root.stat().st_mode) == 0o700
            assert stat.S_IMODE(root.parent.stat().st_mode) == 0o700
            checked.append(path.name)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", checked_open)
    child = [sys.executable, "-u", "-c", "import sys; sys.stdin.read()"]
    session = mcp_client.Session(child, log_dir=root)
    session._record("client", {"scenario": "SYNTHETIC_PRIVATE_SENTINEL"})
    assert session.close() == 0
    assert {"protocol.jsonl", "server-stderr.log", "command.json"} <= set(checked)
    assert "SYNTHETIC_PRIVATE_SENTINEL" in (root / "protocol.jsonl").read_text()
    assert stat.S_IMODE(permissive_parent.stat().st_mode) == 0o755


def test_existing_session_log_directory_is_neither_chmodded_nor_overwritten(
    permissive_parent, monkeypatch
):
    root = permissive_parent / "existing"
    root.mkdir(mode=0o755)
    marker = root / "protocol.jsonl"
    marker.write_bytes(b"FOREIGN_EXISTING_LOG")
    monkeypatch.setattr(
        mcp_client.subprocess, "Popen", lambda *_a, **_k: pytest.fail("child started")
    )
    with pytest.raises(FileExistsError):
        mcp_client.Session(["unused"], log_dir=root)
    assert marker.read_bytes() == b"FOREIGN_EXISTING_LOG"
    assert stat.S_IMODE(root.stat().st_mode) == 0o755


def mac_permission_stubs(monkeypatch):
    """Stop after writing synthetic cases/inspect data; simulate no Ada results."""
    monkeypatch.setattr(mac_smoke.platform, "system", lambda: "Darwin")
    image = "sha256:" + "a" * 64
    cases = [{"scenario_variables": {"PRIVATE": "SYNTHETIC_CASE_SENTINEL"}}]
    monkeypatch.setattr(mac_smoke, "read_cases", lambda _: cases)
    inspected = []

    def inspect(_command, _environment, name, observations):
        inspected.append(name)
        state = None
        if len(inspected) == 2:
            state = {
                "Id": "synthetic-container",
                "Image": image,
                "Config": {
                    "Labels": {"ada-mcp-generic": "1"},
                    "Env": ["SYNTHETIC_ENV=PRIVATE_PERMISSION_CONTROL"],
                },
                "HostConfig": {"ReadonlyRootfs": True, "NetworkMode": "none"},
            }
        observations.append({"status": "present" if state else "absent-confirmed"})
        return state

    monkeypatch.setattr(mac_smoke, "inspect_container", inspect)

    def run(command, _environment=None):
        if "--check" in command:
            stdout = "image=" + image + "\n"
        elif command[1:2] == ["version"]:
            stdout = "{}"
        elif command[:2] == ["/bin/bash", "--version"]:
            stdout = "explicit stub Bash; not Mac evidence"
        elif command[1:2] == ["exec"]:
            raise RuntimeError("permission-only control stops before runtime or Ada queries")
        else:
            raise AssertionError(command)
        return subprocess.CompletedProcess(command, 0, stdout, "")

    monkeypatch.setattr(mac_smoke, "run", run)

    class StubSession:
        def __init__(self, *_args):
            pass

        def initialize(self):
            return {}

        def tools(self):
            return [
                {"name": name}
                for name in ["ada_project_info", "ada_workspace_symbols", "ada_diagnostics"]
            ]

        def close(self):
            return 0

    monkeypatch.setattr(mac_smoke, "Session", StubSession)


def test_mac_evidence_mkdir_private_before_writes_under_explicit_stubs(
    permissive_parent, monkeypatch
):
    mac_permission_stubs(monkeypatch)
    output = permissive_parent / "new-parent/mac-output"
    original_write = Path.write_text
    checked = []

    def checked_write(path, *args, **kwargs):
        if path.parent == output:
            assert stat.S_IMODE(output.stat().st_mode) == 0o700
            assert stat.S_IMODE(output.parent.stat().st_mode) == 0o700
            checked.append(path.name)
        return original_write(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", checked_write)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mac-smoke",
            "--image",
            "synthetic",
            "--root",
            str(permissive_parent),
            "--cases",
            "stub-cases",
            "--output",
            str(output),
        ],
    )
    assert mac_smoke.main() == 1
    assert {"cases.json", "container.json", "summary.json"} <= set(checked)
    assert "SYNTHETIC_CASE_SENTINEL" in (output / "cases.json").read_text()
    assert "SYNTHETIC_ENV" in (output / "container.json").read_text()
    assert json.loads((output / "summary.json").read_text())["status"] == "failed"
    assert stat.S_IMODE(permissive_parent.stat().st_mode) == 0o755


def test_mac_existing_output_is_preserved_under_explicit_stubs(permissive_parent, monkeypatch):
    mac_permission_stubs(monkeypatch)
    output = permissive_parent / "existing"
    output.mkdir(mode=0o755)
    marker = output / "summary.json"
    marker.write_bytes(b"FOREIGN_EVIDENCE")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mac-smoke",
            "--image",
            "synthetic",
            "--root",
            str(permissive_parent),
            "--cases",
            "stub-cases",
            "--output",
            str(output),
        ],
    )
    assert mac_smoke.main() == 1
    assert marker.read_bytes() == b"FOREIGN_EVIDENCE"
    assert stat.S_IMODE(output.stat().st_mode) == 0o755

"""Core-procfs controls are metadata tests, not simulated Ada runtime evidence."""

from pathlib import Path
from types import SimpleNamespace

import pytest
import real_diagnostics


def record(root, pid, parent, program, started, state="S"):
    directory = root / str(pid)
    directory.mkdir(exist_ok=True)
    fields = [state, str(parent), *(["0"] * 17), str(started)]
    # Linux comm may contain spaces and parentheses; it is not a split token.
    (directory / "stat").write_text(f"{pid} (comm with ) parentheses) " + " ".join(fields) + "\n")
    (directory / "cmdline").write_bytes(program.encode() + b"\0--stdio\0")


@pytest.fixture
def proc_fixture(tmp_path):
    root = tmp_path / "proc"
    root.mkdir()
    record(root, 7001, 1, "/opt/python", 100)
    record(root, 7002, 7001, "/opt/ada_language_server", 200)
    errors = tmp_path / "server-stderr.log"
    errors.write_text("INFO Starting ALS: /opt/ada_language_server\n")
    session = SimpleNamespace(process=SimpleNamespace(pid=7001, poll=lambda: None))
    return root, errors, session


def test_optional_children_absence_does_not_block_actual_identity(proc_fixture, monkeypatch):
    root, errors, session = proc_fixture
    monkeypatch.setattr(real_diagnostics, "PROC_ROOT", root)
    monkeypatch.setenv("ALS_PATH", "/opt/ada_language_server")
    original_path = Path

    def core_paths_only(value):
        if str(value).endswith("/children"):
            raise AssertionError("optional task children interface must not be used")
        return original_path(value)

    monkeypatch.setattr(real_diagnostics, "Path", core_paths_only)
    observed = real_diagnostics.process_state(session, errors)
    assert observed["mcp_pid"] == 7001 and observed["als_pid"] == 7002
    assert observed["als_parent_pid"] == 7001
    assert observed["mcp_start_ticks"] == 100 and observed["als_start_ticks"] == 200
    assert not (root / "7001/task/7001/children").exists()


@pytest.mark.parametrize(
    "defect",
    [
        "wrong-parent",
        "wrong-command",
        "empty-command",
        "invalid-stat",
        "mismatched-pid",
        "zombie",
        "missing-stat",
        "missing-command",
        "ambiguous",
    ],
)
def test_unavailable_bad_or_ambiguous_identity_fails_closed(proc_fixture, monkeypatch, defect):
    root, errors, session = proc_fixture
    monkeypatch.setattr(real_diagnostics, "PROC_ROOT", root)
    monkeypatch.setenv("ALS_PATH", "/opt/ada_language_server")
    child = root / "7002"
    if defect == "wrong-parent":
        record(root, 7002, 999, "/opt/ada_language_server", 200)
    elif defect == "wrong-command":
        (child / "cmdline").write_bytes(b"/opt/unrelated\0")
    elif defect == "empty-command":
        (child / "cmdline").write_bytes(b"")
    elif defect == "invalid-stat":
        (child / "stat").write_text("unparseable identity\n")
    elif defect == "mismatched-pid":
        (child / "stat").write_text((child / "stat").read_text().replace("7002 (", "7777 (", 1))
    elif defect == "zombie":
        record(root, 7002, 7001, "/opt/ada_language_server", 200, state="Z")
    elif defect == "missing-stat":
        (child / "stat").unlink()
    elif defect == "missing-command":
        (child / "cmdline").unlink()
    elif defect == "ambiguous":
        record(root, 7003, 7001, "/opt/ada_language_server", 300)
    # The one-start log deliberately remains valid; logs alone cannot pass.
    with pytest.raises((RuntimeError, OSError)):
        real_diagnostics.process_state(session, errors)


def test_process_birth_change_is_rejected_during_observation(proc_fixture, monkeypatch):
    root, _, _ = proc_fixture
    original = real_diagnostics.read_identity
    reads = 0

    def changed_identity(directory):
        nonlocal reads
        identity = original(directory)
        if directory.name == "7002":
            reads += 1
            if reads == 2:
                identity["start_ticks"] += 1
        return identity

    monkeypatch.setattr(real_diagnostics, "read_identity", changed_identity)
    with pytest.raises(RuntimeError, match="identity changed"):
        real_diagnostics.observe_process_pair(7001, "ada_language_server", root)


def test_dead_mcp_cannot_be_replaced_by_a_start_log(proc_fixture, monkeypatch):
    root, errors, session = proc_fixture
    monkeypatch.setattr(real_diagnostics, "PROC_ROOT", root)
    session.process.poll = lambda: 1
    with pytest.raises(RuntimeError, match="MCP process exited"):
        real_diagnostics.process_state(session, errors)

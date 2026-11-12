"""Actual timeout/start negatives must retain primary command receipts."""

import json
import subprocess
import sys

import host_acceptance
import pytest


def test_timeout_retains_partial_streams_before_propagation(tmp_path):
    command = [
        sys.executable,
        "-c",
        "import sys,time; print('partial out',flush=True); "
        "print('partial err',file=sys.stderr,flush=True); time.sleep(30)",
    ]
    with pytest.raises(subprocess.TimeoutExpired):
        host_acceptance.checked(command, tmp_path, "timeout", timeout=1, cwd=tmp_path)
    receipt = json.loads((tmp_path / "timeout.json").read_text())
    assert receipt["argv"] == command and receipt["cwd"] == str(tmp_path.resolve())
    assert receipt["timeout"] == 1 and receipt["rc"] is None
    assert receipt["exception"]["type"] == "TimeoutExpired" and receipt["timed_out"] is True
    assert "partial out" in receipt["stdout"] and "partial err" in receipt["stderr"]


def test_failed_start_retains_attempt_and_error_before_propagation(tmp_path):
    command = [str(tmp_path / "missing-executable")]
    with pytest.raises(FileNotFoundError):
        host_acceptance.checked(command, tmp_path, "start", timeout=2, cwd=tmp_path)
    receipt = json.loads((tmp_path / "start.json").read_text())
    assert receipt["argv"] == command and receipt["cwd"] == str(tmp_path.resolve())
    assert receipt["timeout"] == 2 and receipt["rc"] is None
    assert receipt["exception"]["type"] == "FileNotFoundError"
    assert receipt["stdout"] == receipt["stderr"] == ""


def test_nonzero_exit_retains_streams_and_existing_receipts_are_not_replaced(tmp_path):
    command = [sys.executable, "-c", "print('failed out'); raise SystemExit(17)"]
    with pytest.raises(subprocess.CalledProcessError):
        host_acceptance.checked(command, tmp_path, "nonzero")
    path = tmp_path / "nonzero.json"
    before = path.read_bytes()
    receipt = json.loads(before)
    assert receipt["rc"] == 17 and receipt["stdout"] == "failed out\n"
    assert receipt["exception"]["type"] == "CalledProcessError"
    with pytest.raises(FileExistsError):
        host_acceptance.checked(command, tmp_path, "nonzero")
    assert path.read_bytes() == before

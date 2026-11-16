"""Require real nonroot scan errors to abort fixture inspection; never skip proof."""

import json
import os

import additional_support as support
import pytest
import real_additional as real

from tests.host import test_additional_runner as runner_tests

strict_runner = runner_tests.runner


def make_unreadable(root, name="hidden"):
    assert os.geteuid() != 0, "Permission regression must actually run as nonroot"
    directory = root / name
    directory.mkdir()
    (directory / "dangling").symlink_to(root / "missing-owned-target")
    directory.chmod(0)
    return directory


@pytest.mark.parametrize("name", ["hidden", "obj"])
def test_unreadable_new_directory_is_not_an_unchanged_snapshot(tmp_path, name):
    assert os.geteuid() != 0
    root = tmp_path / "owned"
    root.mkdir()
    (root / "source.adb").write_text("procedure Source is begin null; end Source;\n")
    before = support.file_hashes(root)
    blocked = make_unreadable(root, name)
    try:
        with pytest.raises(PermissionError):
            with os.scandir(blocked) as entries:
                list(entries)
        with pytest.raises(PermissionError):
            support.require_changes(before, support.file_hashes(root), allow_build=False)
    finally:
        blocked.chmod(0o700)


def test_strict_runner_keeps_real_scan_failure_unaccepted(strict_runner):
    blocked = None

    def mutate(root, tool, _arguments, _result):
        nonlocal blocked
        if tool == "ada_call_hierarchy" and blocked is None:
            blocked = make_unreadable(root)

    strict_runner.on_call = mutate
    try:
        with pytest.raises(RuntimeError, match="PermissionError"):
            real.run_control(strict_runner.output, allow_positional_blocker=True)
    finally:
        if blocked is not None:
            blocked.chmod(0o700)
    report = json.loads((strict_runner.output / "summary.json").read_text())
    last = report["calls"][-1]
    assert last["accepted"] is False and last["raw_result"]
    assert last["file_inspection_error"].startswith("PermissionError:")
    assert strict_runner.close_count == strict_runner.cleanup_count == 1


def test_unreadable_regular_file_error_was_already_propagated(tmp_path):
    assert os.geteuid() != 0
    path = tmp_path / "owned-file"
    path.write_text("retain\n")
    path.chmod(0)
    try:
        with pytest.raises(PermissionError):
            support.file_hashes(tmp_path)
    finally:
        path.chmod(0o600)


def test_unreadable_root_cannot_be_an_empty_inventory(tmp_path):
    assert os.geteuid() != 0
    root = tmp_path / "owned-root"
    root.mkdir()
    (root / "source.adb").write_text("retain\n")
    root.chmod(0)
    try:
        with pytest.raises(PermissionError):
            support.file_hashes(root)
    finally:
        root.chmod(0o700)


def test_owned_writer_aborts_before_write_if_any_subtree_is_unreadable(tmp_path):
    root = tmp_path / "owned"
    root.mkdir()
    target = root / "source.adb"
    target.write_bytes(b"retain\n")
    blocked = make_unreadable(root)
    try:
        with pytest.raises(PermissionError):
            support.mutate_owned(root, {target: b"changed\n"})
        assert target.read_bytes() == b"retain\n"
    finally:
        blocked.chmod(0o700)

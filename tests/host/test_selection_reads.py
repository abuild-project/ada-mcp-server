"""Bind private-record trust to the opened inode and retain structured CLI failures."""

import copy
import errno
import hashlib
import json
import os
from pathlib import Path

import acquire
import image_identity
import pytest
from image_fixtures import metadata_archive
from test_runtime_selection import activate, command, entry, runtime_pair
from test_update_bytecode import snapshot


@pytest.mark.parametrize("kind", ["symlink", "replacement-mode"])
def test_record_swap_cannot_supply_new_helper_pins(tmp_path, monkeypatch, kind):
    old = runtime_pair(tmp_path, "old")
    marker = tmp_path / "unexpected-helper"
    bait = runtime_pair(tmp_path, "bait", "0.2.0-rc.91", marker=marker)
    record = acquire.inspect_runtime(*old, 1)
    state = tmp_path / "selection.json"
    original = json.dumps(record).encode()
    state.write_bytes(original)
    state.chmod(0o600)
    bait_record = dict(
        record,
        runtime=str(bait[0]),
        binding=str(bait[2]),
        runtime_manifest_sha256=bait[1],
        binding_sha256=hashlib.sha256(bait[2].read_bytes()).hexdigest(),
        project_version="0.2.0-rc.91",
    )
    public = tmp_path / "untrusted-record.json"
    public.write_text(json.dumps(bait_record))
    public.chmod(0o644)
    before = {str(pair[0]): snapshot(pair[0]) for pair in [old, bait]}
    swapped = []
    actual_lstat = Path.lstat
    actual_open = os.open

    def swap():
        if not swapped:
            state.unlink()
            if kind == "symlink":
                state.symlink_to(public)
            else:
                state.write_bytes(public.read_bytes())
                state.chmod(0o644)
            swapped.append(True)

    def after_old_lstat(path, *args, **kwargs):
        metadata = actual_lstat(path, *args, **kwargs)
        if path == state:
            swap()
        return metadata

    def before_new_open(path, flags, *args, **kwargs):
        if Path(path) == state:
            swap()
        return actual_open(path, flags, *args, **kwargs)

    with monkeypatch.context() as patch:
        # Exercise either implementation's actual boundary, so a missing old
        # lstat hook alone cannot make this negative control pass vacuously.
        patch.setattr(Path, "lstat", after_old_lstat)
        patch.setattr(os, "open", before_new_open)
        with pytest.raises((ValueError, OSError)):
            acquire.selected_runtime(state)
    assert swapped and not marker.exists()
    assert {str(pair[0]): snapshot(pair[0]) for pair in [old, bait]} == before
    state.unlink()  # undo only the attack fixture's replacement
    state.write_bytes(original)
    state.chmod(0o600)
    assert acquire.selected_runtime(state)["runtime"] == str(old[0])
    assert not marker.exists()


@pytest.mark.parametrize("defect", ["owner", "permissions", "size"])
def test_private_validation_uses_open_descriptor_and_closes_it(tmp_path, monkeypatch, defect):
    path = tmp_path / "record.json"
    path.write_bytes(b"private bytes")
    path.chmod(0o600)
    actual_open, actual_fstat = os.open, os.fstat
    opened = []

    def capture(path, flags, *args, **kwargs):
        assert flags & os.O_ACCMODE == os.O_RDONLY
        assert flags & os.O_NOFOLLOW and flags & os.O_NONBLOCK
        descriptor = actual_open(path, flags, *args, **kwargs)
        assert not os.get_inheritable(descriptor)
        opened.append(descriptor)
        return descriptor

    def metadata(descriptor):
        values = list(actual_fstat(descriptor))
        if descriptor not in opened:
            return os.stat_result(values)
        if defect == "owner":
            values[4] = os.getuid() + 1  # no chown/privileged fixture needed
        elif defect == "permissions":
            values[0] |= 0o040
        else:
            values[6] = 65
        return os.stat_result(values)

    def unexpected_read(*args, **kwargs):
        raise AssertionError("read preceded descriptor validation")

    monkeypatch.setattr(os, "open", capture)
    monkeypatch.setattr(os, "fstat", metadata)
    monkeypatch.setattr(os, "fdopen", unexpected_read)
    with pytest.raises(ValueError):
        acquire.bounded_file(path, 64, private=True)
    assert len(opened) == 1
    with pytest.raises(OSError) as closed:
        actual_fstat(opened[0])
    assert closed.value.errno == errno.EBADF


def test_nonregular_fifo_is_opened_nonblocking_rejected_and_closed(tmp_path, monkeypatch):
    path = tmp_path / "fifo"
    os.mkfifo(path, 0o600)
    actual_open = os.open
    opened = []

    def capture(path, flags, *args, **kwargs):
        assert flags & os.O_NONBLOCK
        descriptor = actual_open(path, flags, *args, **kwargs)
        opened.append(descriptor)
        return descriptor

    monkeypatch.setattr(os, "open", capture)
    with pytest.raises(ValueError, match="regular file"):
        acquire.bounded_file(path, 64, private=True)
    assert len(opened) == 1
    with pytest.raises(OSError) as closed:
        os.fstat(opened[0])
    assert closed.value.errno == errno.EBADF


def test_path_replacement_after_open_does_not_change_the_validated_bytes(tmp_path, monkeypatch):
    path = tmp_path / "private.json"
    path.write_bytes(b"original private bytes")
    path.chmod(0o600)
    actual_open = os.open
    opened = []

    def replace_after_open(candidate, flags, *args, **kwargs):
        descriptor = actual_open(candidate, flags, *args, **kwargs)
        path.unlink()
        path.write_bytes(b"unvalidated replacement")
        path.chmod(0o644)
        opened.append(descriptor)
        return descriptor

    monkeypatch.setattr(os, "open", replace_after_open)
    assert acquire.bounded_file(path, 64, private=True) == b"original private bytes"
    assert len(opened) == 1 and path.read_bytes() == b"unvalidated replacement"
    with pytest.raises(OSError) as closed:
        os.fstat(opened[0])
    assert closed.value.errno == errno.EBADF


def test_same_descriptor_read_remains_byte_bounded_if_size_changes(tmp_path, monkeypatch):
    path = tmp_path / "record.json"
    path.write_bytes(b"x" * 65)
    path.chmod(0o600)
    actual_fstat = os.fstat
    read = []
    actual_fdopen = os.fdopen

    def old_size(descriptor):
        values = list(actual_fstat(descriptor))
        values[6] = 0
        return os.stat_result(values)

    def capture_read(*args, **kwargs):
        read.append(True)
        return actual_fdopen(*args, **kwargs)

    monkeypatch.setattr(os, "fstat", old_size)
    monkeypatch.setattr(os, "fdopen", capture_read)
    with pytest.raises(ValueError, match="size bound"):
        acquire.bounded_file(path, 64, private=True)
    assert read


@pytest.mark.parametrize("stage", ["stat", "read"])
def test_descriptor_is_closed_when_metadata_or_reading_fails(tmp_path, monkeypatch, stage):
    path = tmp_path / "record.json"
    path.write_bytes(b"private bytes")
    path.chmod(0o600)
    actual_open, actual_fstat = os.open, os.fstat
    opened = []

    def capture(*args, **kwargs):
        descriptor = actual_open(*args, **kwargs)
        opened.append(descriptor)
        return descriptor

    actual_fdopen = os.fdopen

    def fail(descriptor, *args, **kwargs):
        if descriptor in opened:
            raise OSError("controlled descriptor failure")
        return (actual_fstat if stage == "stat" else actual_fdopen)(descriptor, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(os, "open", capture)
        patch.setattr(os, "fstat" if stage == "stat" else "fdopen", fail)
        with pytest.raises(OSError, match="controlled descriptor failure"):
            acquire.bounded_file(path, 64, private=True)
    assert len(opened) == 1
    with pytest.raises(OSError) as closed:
        actual_fstat(opened[0])
    assert closed.value.errno == errno.EBADF


@pytest.mark.parametrize("replace", [False, True])
def test_malformed_nested_oci_binding_returns_json_without_activation(tmp_path, replace):
    script = entry(tmp_path)
    state = tmp_path / "selection.json"
    extra = []
    previous = None
    if replace:
        old = runtime_pair(tmp_path, "old")
        result, selected = activate(script, state, old)
        assert result.returncode == 0
        previous = state.read_bytes()
        extra = [
            "--expected-sha256",
            selected["selection_sha256"],
            "--backup",
            str(tmp_path / "unused-backup.json"),
        ]
    runtime, _, bound = runtime_pair(tmp_path, "invalid")
    stream, _, _ = metadata_archive(oci=True)
    identity = image_identity.archive_identity(stream)
    manifest_path = runtime / "scripts/runtime-manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest.update(image_id=identity["image_id"], image_identity=identity)
    manifest_path.write_text(json.dumps(manifest))
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    value = json.loads(bound.read_bytes())
    value.update(image_id=identity["image_id"], image_identity=copy.deepcopy(identity))
    value["image_identity"]["target"]["platform"] = "linux/amd64"
    bound.write_text(json.dumps(value))
    before = snapshot(runtime)
    result, invalid = command(
        script,
        state,
        "activate",
        "--runtime",
        str(runtime),
        "--manifest-sha256",
        digest,
        "--binding",
        str(bound),
        "--workflow-contract",
        "1",
        *extra,
    )
    assert result.returncode == 1 and invalid["status"] == "invalid"
    assert "get" in invalid["reason"] and not result.stderr
    if replace:
        assert state.read_bytes() == previous
    else:
        assert not state.exists()
    assert not (tmp_path / "unused-backup.json").exists()
    assert not state.with_name(state.name + ".lock").exists()
    assert snapshot(runtime) == before

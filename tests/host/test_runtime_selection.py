"""Keep an entry unchanged while explicitly switching compatible pinned runtime pairs."""

import hashlib
import json
import os
import subprocess
import sys

import acquire
import artifacts
import pytest
from image_fixtures import classic_identity
from test_setup_boundaries import binding
from test_update_bytecode import poison, snapshot
from version import ROOT


def runtime_pair(tmp_path, name, version="0.2.0-rc.90", contract=1, marker=None):
    runtime = tmp_path / name
    image_id = "sha256:" + "b" * 64
    identity = classic_identity(image_id)
    files = artifacts.tooling_files(ROOT, "a" * 40, identity, {})
    manifest = json.loads(files["scripts/runtime-manifest.json"])
    manifest.update(project_version=version, python_version=version.replace("-rc.", "rc"))
    if contract is None:
        manifest.pop("workflow_contract")
    else:
        manifest["workflow_contract"] = contract
    files["scripts/ada_mcp/_version.py"] = f'VERSION = "{version}"\n'.encode()
    if marker:
        files["scripts/ada_mcp_setup.py"] = (
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n".encode()
            + files["scripts/ada_mcp_setup.py"]
        )
    manifest["files_sha256"].update(
        {
            name: hashlib.sha256(data).hexdigest()
            for name, data in files.items()
            if name != "scripts/runtime-manifest.json"
        }
    )
    files["scripts/runtime-manifest.json"] = (json.dumps(manifest) + "\n").encode()
    acquire.materialize(files, runtime)
    roots = tmp_path / (name + "-projects")
    roots.mkdir()
    path = tmp_path / (name + "-binding.json")
    path.write_text(json.dumps(binding(roots, image_id)))
    return runtime, hashlib.sha256(files["scripts/runtime-manifest.json"]).hexdigest(), path


def entry(tmp_path):
    path = tmp_path / "unchanged-entry.py"
    path.write_bytes((ROOT / "tooling/acquire.py").read_bytes())
    return path


def command(script, state, *arguments, env=None):
    result = subprocess.run(
        [sys.executable, "-I", str(script), "selection", *arguments, "--file", str(state)],
        text=True,
        capture_output=True,
        timeout=10,
        env=env,
    )
    return result, json.loads(result.stdout)


def activate(script, state, pair, *extra):
    runtime, digest, bound = pair
    return command(
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


def test_unchanged_entry_reuses_later_selected_version_and_can_rollback(tmp_path):
    script = entry(tmp_path)
    before_entry = script.read_bytes()
    state = tmp_path / "private-state/selection.json"
    result, absent = command(script, state, "show")
    assert result.returncode == 0 and absent["status"] == "absent"
    assert not state.parent.exists()
    first = runtime_pair(tmp_path, "first")
    second = runtime_pair(tmp_path, "second", "0.2.0-rc.91")
    before = {str(pair[0]): snapshot(pair[0]) for pair in [first, second]}
    result, old = activate(script, state, first)
    assert result.returncode == 0 and old["project_version"] == "0.2.0-rc.90"
    backup = tmp_path / "backups/old.json"
    result, current = activate(
        script, state, second, "--expected-sha256", old["selection_sha256"], "--backup", str(backup)
    )
    assert result.returncode == 0 and current["project_version"] == "0.2.0-rc.91"
    assert json.loads(backup.read_bytes())["runtime"] == str(first[0])
    result, later = command(script, state, "show")
    assert result.returncode == 0 and later == current
    assert later["binding"] == str(second[2])
    result, restored = activate(
        script,
        state,
        first,
        "--expected-sha256",
        current["selection_sha256"],
        "--backup",
        str(tmp_path / "backups/new.json"),
    )
    assert result.returncode == 0 and restored["project_version"] == "0.2.0-rc.90"
    assert script.read_bytes() == before_entry
    assert {str(pair[0]): snapshot(pair[0]) for pair in [first, second]} == before
    assert state.stat().st_mode & 0o077 == backup.stat().st_mode & 0o077 == 0


@pytest.mark.parametrize("contract", [None, 0, 2, True, "1"])
def test_unknown_or_legacy_contract_never_executes_target_or_activates(tmp_path, contract):
    marker = tmp_path / "executed"
    pair = runtime_pair(tmp_path, "target", contract=contract, marker=marker)
    state = tmp_path / "unused/selection.json"
    result, report = activate(entry(tmp_path), state, pair)
    assert result.returncode == 1 and report["status"] == "incompatible"
    assert "updated compatible skill/plugin" in report["reason"]
    assert not marker.exists() and not state.parent.exists()


@pytest.mark.parametrize("defect", ["manifest", "helper", "binding-image", "release-contract"])
def test_invalid_target_is_rejected_before_authenticated_helper_runs(tmp_path, defect):
    marker = tmp_path / "executed"
    runtime, digest, bound = runtime_pair(tmp_path, "target", marker=marker)
    contract = 1
    if defect == "manifest":
        digest = "0" * 64
    elif defect == "helper":
        (runtime / "scripts/image_identity.py").write_text("raise AssertionError('unverified')\n")
    elif defect == "binding-image":
        value = json.loads(bound.read_bytes())
        value["image_id"] = "sha256:" + "c" * 64
        bound.write_text(json.dumps(value))
    else:
        contract = 2
    with pytest.raises((ValueError, RuntimeError)):
        acquire.inspect_runtime(runtime, digest, bound, contract)
    assert not marker.exists()


def test_selected_pins_and_source_corruption_stop_before_target_execution(tmp_path):
    marker = tmp_path / "executed"
    pair = runtime_pair(tmp_path, "target", marker=marker)
    script = entry(tmp_path)
    state = tmp_path / "selection.json"
    result, _ = activate(script, state, pair)
    assert result.returncode == 0 and marker.exists()  # nonvacuous helper-execution control
    marker.unlink()
    original = state.read_bytes()
    for change in ["source_sha", "project_version", "binding_sha256"]:
        record = json.loads(original)
        record[change] = "0" * 64 if change.endswith("sha256") else "mismatch"
        state.write_text(json.dumps(record))
        result, report = command(script, state, "show")
        assert result.returncode == 1 and report["status"] == "invalid"
        assert not marker.exists()
    state.write_bytes(original)
    pair[2].write_text(pair[2].read_text() + " ")
    result, report = command(script, state, "show")
    assert result.returncode == 1 and "binding SHA256 mismatch" in report["reason"]
    assert not marker.exists()


def test_preexisting_helper_bytecode_is_ignored_and_runtime_bytes_do_not_change(tmp_path):
    pair = runtime_pair(tmp_path, "target")
    marker = tmp_path / "pyc-executed"
    for name in ["ada_mcp_setup.py", "image_identity.py"]:
        poison(pair[0] / "scripts" / name, marker)
    before = snapshot(pair[0])
    result, report = activate(entry(tmp_path), tmp_path / "selection.json", pair)
    assert result.returncode == 0 and report["status"] == "selected"
    assert not marker.exists() and snapshot(pair[0]) == before


@pytest.mark.parametrize("defect", ["no-replace", "stale", "backup", "lock", "symlink"])
def test_replacement_guards_preserve_existing_selection(tmp_path, defect):
    script = entry(tmp_path)
    pair = runtime_pair(tmp_path, "target")
    state = tmp_path / "selection.json"
    result, current = activate(script, state, pair)
    assert result.returncode == 0
    before = state.read_bytes()
    backup = tmp_path / "backup.json"
    if defect == "backup":
        backup.write_text("preserve this\n")
    if defect == "lock":
        state.with_name(state.name + ".lock").write_text("busy\n")
    if defect == "symlink":
        actual = tmp_path / "actual.json"
        state.rename(actual)
        state.symlink_to(actual)
    extra = (
        []
        if defect == "no-replace"
        else [
            "--expected-sha256",
            "0" * 64 if defect == "stale" else current["selection_sha256"],
            "--backup",
            str(backup),
        ]
    )
    result, report = activate(script, state, pair, *extra)
    assert result.returncode == 1 and report["status"] == "invalid"
    assert state.read_bytes() == before
    if defect == "backup":
        assert backup.read_text() == "preserve this\n"


def test_replace_failure_keeps_old_choice_and_rollback_backup(tmp_path, monkeypatch):
    pair = runtime_pair(tmp_path, "target")
    record = acquire.inspect_runtime(*pair, 1)
    state = tmp_path / "selection.json"
    acquire.activate_selection(state, record, None, None)
    before = state.read_bytes()
    backup = tmp_path / "backup.json"

    def fail(*args):
        raise OSError("controlled replace failure")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError, match="controlled"):
        acquire.activate_selection(state, record, hashlib.sha256(before).hexdigest(), backup)
    assert state.read_bytes() == backup.read_bytes() == before
    assert not state.with_name(state.name + ".lock").exists()


def test_show_respects_explicit_selection_over_environment_and_checks_bounds(tmp_path):
    script = entry(tmp_path)
    pair = runtime_pair(tmp_path, "target")
    state = tmp_path / "selection.json"
    assert activate(script, state, pair)[0].returncode == 0
    env = dict(os.environ, ADA_MCP_SELECTION=str(tmp_path / "absent.json"))
    assert command(script, state, "show", env=env)[1]["status"] == "selected"
    env["ADA_MCP_SELECTION"] = str(state)
    discovered = subprocess.run(
        [sys.executable, "-I", str(script), "selection", "show"],
        env=env,
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    assert json.loads(discovered.stdout)["runtime"] == str(pair[0])
    state.write_bytes(b"x" * (acquire.MAX_SELECTION_BYTES + 1))
    result, report = command(script, state, "show")
    assert result.returncode == 1 and "size bound" in report["reason"]


def test_fresh_process_needs_the_custom_locator_even_when_its_pair_persists(tmp_path):
    """Model explicit next-process settings, without assuming provider persistence."""
    script = entry(tmp_path)
    before_entry = script.read_bytes()
    pair = runtime_pair(tmp_path, "target")
    state = tmp_path / "custom-private/selection.json"
    result, activated = activate(script, state, pair)
    assert result.returncode == 0
    before_state = state.read_bytes()
    private_home = tmp_path / "fresh-private-home"
    private_home.mkdir(mode=0o700)
    process_env = dict(os.environ, HOME=str(private_home))
    process_env.pop("ADA_MCP_SELECTION", None)

    def discover(env):
        return json.loads(
            subprocess.run(
                [sys.executable, "-I", str(script), "selection", "show"],
                env=env,
                text=True,
                capture_output=True,
                check=True,
                timeout=10,
            ).stdout
        )

    default = discover(process_env)
    assert default == {
        "status": "absent",
        "selection": str(private_home / ".config/ada-mcp/selection.json"),
    }
    assert list(private_home.iterdir()) == []
    explicit, supplied = command(script, state, "show", env=process_env)
    assert explicit.returncode == 0 and supplied == activated
    retained_locator_env = dict(process_env, ADA_MCP_SELECTION=str(state))
    assert discover(retained_locator_env) == activated
    assert discover(process_env) == default  # no implicit persisted pointer/config write
    assert list(private_home.iterdir()) == []
    assert script.read_bytes() == before_entry and state.read_bytes() == before_state


def test_archive_contract_check_refuses_legacy_or_mismatched_release_before_writes(tmp_path):
    pair = runtime_pair(tmp_path, "target", contract=None)
    files = {
        str(path.relative_to(pair[0])): path.read_bytes()
        for path in pair[0].rglob("*")
        if path.is_file()
    }
    archive = tmp_path / "legacy.tar.gz"
    artifacts.write_tar(archive, files)
    with pytest.raises(acquire.IncompatibleRuntimeError):
        acquire.verified_files(
            archive.read_bytes(), hashlib.sha256(archive.read_bytes()).hexdigest(), pair[1], 1
        )

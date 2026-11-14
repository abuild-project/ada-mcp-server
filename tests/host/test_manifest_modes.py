"""Packaged bootstrap cannot downgrade to contributor source when metadata disappears."""

import hashlib
import json
import subprocess
import sys

import pytest
from test_update_bytecode import environment, poison, prepare, snapshot
from test_update_source_capture import declare
from version import ROOT


def run(tmp_path, arguments):
    return subprocess.run(
        [sys.executable, "-I", *arguments],
        cwd=tmp_path,
        env=environment(tmp_path),
        text=True,
        capture_output=True,
        timeout=8,
    )


def setup_program(scripts):
    return (
        "from pathlib import Path\nimport json\n"
        f"source=Path({str(scripts / 'ada_mcp_setup.py')!r})\n"
        "ns={'__name__':'_fixture_setup','__file__':str(source)}\n"
        "exec(compile(source.read_bytes(),str(source),'exec'),ns)\n"
    )


def unlist_client(scripts, marker):
    client = scripts / "mcp_client.py"
    client.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        + client.read_text()
    )
    manifest = scripts / "runtime-manifest.json"
    data = json.loads(manifest.read_text())
    data["files_sha256"].pop("scripts/mcp_client.py")
    manifest.write_text(json.dumps(data))


@pytest.mark.parametrize("kind", ["source", "bundle"])
@pytest.mark.parametrize("poisoned", [False, True])
def test_real_smoke_help_preserves_valid_runtime_and_cached_helpers(tmp_path, kind, poisoned):
    runtime, scripts, _ = prepare(tmp_path, kind)
    if kind == "source":
        for name in ["ada_mcp_setup.py", "mcp_client.py", "mac_smoke.py"]:
            (scripts / name).write_bytes((ROOT / "tooling" / name).read_bytes())
    marker = tmp_path / "unverified-bytecode-executed"
    if poisoned:
        for name in ["ada_mcp_setup.py", "mcp_client.py"]:
            poison(scripts / name, marker)
    expected = snapshot(runtime)
    result = run(tmp_path, [str(scripts / "mac_smoke.py"), "--help"])
    assert result.returncode == 0 and "usage:" in result.stdout, result.stderr
    assert not marker.exists() and snapshot(runtime) == expected


def test_packaged_smoke_rejects_missing_manifest_before_setup_execution(tmp_path):
    runtime, scripts, _ = prepare(tmp_path, "bundle")
    manifest, setup = scripts / "runtime-manifest.json", scripts / "ada_mcp_setup.py"
    marker = tmp_path / "unverified-setup-executed"
    manifest.unlink()
    setup.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        + setup.read_text()
    )
    expected = snapshot(runtime)
    result = run(tmp_path, [str(scripts / "mac_smoke.py"), "--help"])
    assert result.returncode != 0 and "runtime-manifest.json" in result.stderr
    assert not marker.exists() and snapshot(runtime) == expected


@pytest.mark.parametrize("removal", ["unlink", "rename"])
def test_smoke_keeps_installed_mode_when_manifest_disappears_during_setup(tmp_path, removal):
    runtime, scripts, _ = prepare(tmp_path, "bundle")
    manifest, setup = scripts / "runtime-manifest.json", scripts / "ada_mcp_setup.py"
    marker = tmp_path / "unlisted-client-executed"
    unlist_client(scripts, marker)
    action = (
        f"Path({str(manifest)!r}).unlink()\n"
        if removal == "unlink"
        else f"Path({str(manifest)!r}).rename({str(tmp_path / 'retained-manifest.json')!r})\n"
    )
    # A trusted fixture setup removes metadata after the smoke entry's initial
    # authentication. Its omitted client remains untrusted and must not execute.
    setup.write_text("from pathlib import Path\n" + action + setup.read_text())
    declare(scripts, setup)
    expected = snapshot(runtime)
    expected.pop("scripts/runtime-manifest.json")
    result = run(tmp_path, [str(scripts / "mac_smoke.py"), "--help"])
    assert result.returncode != 0 and "runtime-manifest.json" in result.stderr
    assert not marker.exists() and snapshot(runtime) == expected


@pytest.mark.parametrize("stage", ["initially-missing", "observed", "verified"])
def test_packaged_loader_never_executes_unlisted_source_after_manifest_removal(tmp_path, stage):
    runtime, scripts, _ = prepare(tmp_path, "bundle")
    manifest = scripts / "runtime-manifest.json"
    marker = tmp_path / "unlisted-client-executed"
    unlist_client(scripts, marker)
    program = setup_program(scripts)
    if stage == "initially-missing":
        manifest.unlink()
    else:
        if stage == "verified":
            program += "ns['verified_manifest']()\n"
        program += f"Path({str(manifest)!r}).unlink()\n"
    program += "ns['load_helper']('mcp_client')\n"
    expected = snapshot(runtime)
    expected.pop("scripts/runtime-manifest.json", None)
    result = run(tmp_path, ["-c", program])
    assert result.returncode != 0 and "has not been verified" in result.stderr
    assert not marker.exists() and snapshot(runtime) == expected


@pytest.mark.parametrize("cached", [False, True])
def test_declared_sources_stay_usable_after_manifest_and_source_replacement(tmp_path, cached):
    runtime, scripts, _ = prepare(tmp_path, "bundle")
    manifest, client = scripts / "runtime-manifest.json", scripts / "mcp_client.py"
    marker = tmp_path / "replacement-client-executed"
    poison(client, marker)
    replacement = (
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        "raise RuntimeError('unverified source executed')\n"
    )
    program = setup_program(scripts) + "ns['verified_manifest']()\n"
    if cached:
        program += "ns['load_helper']('mcp_client')\n"
    program += (
        f"Path({str(manifest)!r}).unlink()\n"
        f"Path({str(client)!r}).write_text({replacement!r})\n"
        "assert 'ada_project_info' in ns['load_helper']('mcp_client')['READ_TOOLS']\n"
        "print(json.dumps({'retained_source_used':True}))\n"
    )
    expected = snapshot(runtime)
    expected.pop("scripts/runtime-manifest.json")
    expected["scripts/mcp_client.py"] = (
        hashlib.sha256(replacement.encode()).hexdigest(),
        expected["scripts/mcp_client.py"][1],
    )
    result = run(tmp_path, ["-c", program])
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"retained_source_used": True}
    assert not marker.exists() and snapshot(runtime) == expected


def test_packaged_checker_with_src_sibling_still_requires_manifest(tmp_path):
    runtime, scripts, _ = prepare(tmp_path, "bundle")
    (scripts / "runtime-manifest.json").unlink()
    # The source fallback requires the real tooling/src relation. A src file
    # beside a packaged scripts tree must not change its installed mode.
    source = runtime / "src/ada_mcp/update_notice.py"
    source.parent.mkdir(parents=True)
    source.write_bytes((ROOT / "src/ada_mcp/update_notice.py").read_bytes())
    expected = snapshot(runtime)
    result = run(
        tmp_path,
        [str(scripts / "release_updates.py"), "status", "--channel", "off"],
    )
    assert result.returncode != 0 and "runtime-manifest.json" in result.stderr
    assert snapshot(runtime) == expected

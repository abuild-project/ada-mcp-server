"""Installed release workers require declared sources and keep their exact snapshot."""

import hashlib
import json
import os
import subprocess
import sys

import pytest
from test_update_bytecode import environment, prepare, snapshot
from version import ROOT


def run(tmp_path, program):
    return subprocess.run(
        [sys.executable, "-I", "-c", program],
        cwd=tmp_path,
        env=environment(tmp_path),
        text=True,
        capture_output=True,
        timeout=8,
    )


def declare(scripts, path):
    """Make a synthetic fixture source part of the installed bundle's trust input."""
    manifest = scripts / "runtime-manifest.json"
    data = json.loads(manifest.read_text())
    data["files_sha256"][str(path.relative_to(scripts.parent))] = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()
    manifest.write_text(json.dumps(data))


def load(scripts, entry):
    source = scripts / ("ada_mcp_setup.py" if entry == "setup" else "release_updates.py")
    program = (
        "from pathlib import Path\nimport json\n"
        f"source=Path({str(source)!r})\n"
        "ns={'__name__':'_fixture_parent','__file__':str(source)}\n"
        "exec(compile(source.read_bytes(),str(source),'exec'),ns)\n"
    )
    return program + (
        "ns['verified_manifest']()\nchecker=ns['load_helper']('release_updates')\n"
        if entry == "setup"
        else "checker=ns\n"
    )


@pytest.mark.parametrize("entry", ["setup", "direct", "setup-cli", "direct-cli"])
@pytest.mark.parametrize("missing", ["validator", "checker"])
def test_undeclared_checker_sources_never_fall_back_to_disk(tmp_path, entry, missing):
    runtime, scripts, package = prepare(tmp_path, "bundle")
    target = (
        package / "update_notice.py" if missing == "validator" else scripts / "release_updates.py"
    )
    marker = tmp_path / "undeclared-source-executed"
    # For the direct entry the checker is the trusted bootstrap already running;
    # poisoning its on-disk copy is covered by the post-capture controls below.
    if missing == "validator":
        target.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
            + target.read_text()
        )
    manifest = scripts / "runtime-manifest.json"
    data = json.loads(manifest.read_text())
    data["files_sha256"].pop(str(target.relative_to(runtime)))
    manifest.write_text(json.dumps(data))
    expected = snapshot(runtime)
    if entry.endswith("-cli"):
        command = [sys.executable, "-I", str(scripts / "release_updates.py")]
        if entry == "setup-cli":
            command = [sys.executable, "-I", str(scripts / "ada_mcp_setup.py"), "updates"]
        result = subprocess.run(
            command + ["status", "--channel", "off", "--cache", str(tmp_path / "unused-cache")],
            cwd=tmp_path,
            env=environment(tmp_path),
            text=True,
            capture_output=True,
            timeout=8,
        )
    else:
        result = run(
            tmp_path,
            load(scripts, entry)
            + f"cache=Path({str(tmp_path / 'unused-cache')!r})\n"
            + "print(json.dumps(checker['check_updates']('0.2.0','off',cache)))\n",
        )
    if entry == "setup-cli":
        # Setup reports unavailable advisories without making MCP use fail.
        assert result.returncode == 0
        assert json.loads(result.stdout) == {
            "status": "unknown",
            "reason": "runtime_metadata_unavailable",
        }
    else:
        assert result.returncode != 0 and "verified" in result.stderr + result.stdout
    assert not marker.exists() and snapshot(runtime) == expected
    assert not (tmp_path / "unused-cache").exists()


@pytest.mark.parametrize("retained", ["empty", "missing-validator", "missing-checker"])
def test_explicit_retained_context_cannot_be_reinterpreted_as_contributor_source(
    tmp_path, retained
):
    runtime, scripts, package = prepare(tmp_path, "source")
    checker, validator = scripts / "release_updates.py", package / "update_notice.py"
    program = (
        "from pathlib import Path\n"
        f"checker,validator=Path({str(checker)!r}),Path({str(validator)!r})\n"
        "sources={}\n"
    )
    if retained == "missing-validator":
        program += "sources[checker]=checker.read_bytes()\n"
    elif retained == "missing-checker":
        program += "sources[validator]=validator.read_bytes()\n"
    program += (
        "ns={'__name__':'_fixture_parent','__file__':str(checker),'__verified_sources__':sources}\n"
        "exec(compile(checker.read_bytes(),str(checker),'exec'),ns)\n"
    )
    expected = snapshot(runtime)
    result = run(tmp_path, program)
    assert result.returncode != 0 and "both have been verified" in result.stderr
    assert snapshot(runtime) == expected


def test_contributor_helper_loading_does_not_claim_a_verified_context(tmp_path):
    runtime, scripts, _ = prepare(tmp_path, "source")
    setup = scripts / "ada_mcp_setup.py"
    setup.write_bytes((ROOT / "tooling/ada_mcp_setup.py").read_bytes())
    expected = snapshot(runtime)
    program = (
        "from pathlib import Path\nimport json\n"
        f"source=Path({str(setup)!r})\n"
        "ns={'__name__':'_fixture_parent','__file__':str(source)}\n"
        "exec(compile(source.read_bytes(),str(source),'exec'),ns)\n"
        "checker=ns['load_helper']('release_updates')\n"
        f"cache=Path({str(tmp_path / 'unused-cache')!r})\n"
        "print(json.dumps(checker['check_updates']('0.2.0','off',cache)))\n"
    )
    result = run(tmp_path, program)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"status": "disabled", "current_version": "0.2.0"}
    assert snapshot(runtime) == expected and not (tmp_path / "unused-cache").exists()


@pytest.mark.parametrize(
    "entry,kind", [("setup", "bundle"), ("direct", "bundle"), ("direct", "source")]
)
@pytest.mark.parametrize("changed", ["checker", "validator", "none"])
def test_real_fetch_child_uses_captured_sources_after_replacement(tmp_path, entry, kind, changed):
    runtime, scripts, package = prepare(tmp_path, kind)
    checker, validator = scripts / "release_updates.py", package / "update_notice.py"
    worker_pid = tmp_path / "fetch-worker-pid"
    # This trusted synthetic source retains production fetch_feed parsing, URL,
    # size and completeness checks while substituting only its HTTP transport.
    transport = (
        "\nclass FixtureResponse:\n"
        "    headers={}\n"
        "    def __enter__(self): return self\n"
        "    def __exit__(self,*args): pass\n"
        "    def geturl(self): return API_URL\n"
        "    def read(self,limit):\n"
        "        assert limit == MAX_FEED+1\n"
        '        return b\'[{"tag_name":"v0.3.0","draft":false,"prerelease":false}]\'\n'
        "class FixtureOpener:\n"
        "    def open(self,request,timeout):\n"
        "        assert request.full_url == API_URL and timeout == 1.5\n"
        f"        Path({str(worker_pid)!r}).write_text(str(os.getpid()))\n"
        "        return FixtureResponse()\n"
        "urllib.request.build_opener=lambda *args: FixtureOpener()\n"
    )
    checker.write_text(
        checker.read_text().replace(
            '\nif __name__ == "__main__":', transport + '\nif __name__ == "__main__":'
        )
    )
    if kind == "bundle":
        declare(scripts, checker)
    expected = snapshot(runtime)
    marker = tmp_path / "replacement-executed"
    program = load(scripts, entry)
    if changed != "none":
        target = checker if changed == "checker" else validator
        replacement = (
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
            "raise RuntimeError('post-verification source executed')\n"
        )
        program += f"Path({str(target)!r}).write_text({replacement!r})\n"
        relative = str(target.relative_to(runtime))
        expected[relative] = (
            hashlib.sha256(replacement.encode()).hexdigest(),
            expected[relative][1],
        )
    program += (
        f"cache=Path({str(tmp_path / 'private-cache')!r})\n"
        "result=checker['check_updates']('0.2.0-rc.1','auto',cache,manual=True)\n"
        "print(json.dumps({'result':result,'parent_pid':__import__('os').getpid()}))\n"
    )
    result = run(tmp_path, program)
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["result"]["status"] == "available"
    assert output["result"]["check_performed"] is True
    assert output["result"]["update_notice"]["available_version"] == "0.3.0"
    assert int(worker_pid.read_text()) not in {os.getpid(), output["parent_pid"]}
    assert not marker.exists() and snapshot(runtime) == expected


@pytest.mark.parametrize("missing", [True, False])
def test_direct_installed_bootstrap_authenticates_setup_before_execution(tmp_path, missing):
    runtime, scripts, _ = prepare(tmp_path, "bundle")
    setup = scripts / "ada_mcp_setup.py"
    marker = tmp_path / "unverified-setup-executed"
    setup.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n")
    if missing:
        manifest = scripts / "runtime-manifest.json"
        data = json.loads(manifest.read_text())
        data["files_sha256"].pop("scripts/ada_mcp_setup.py")
        manifest.write_text(json.dumps(data))
    expected = snapshot(runtime)
    result = run(tmp_path, load(scripts, "direct"))
    assert result.returncode != 0
    assert not marker.exists() and snapshot(runtime) == expected


def test_missing_manifest_cannot_turn_packaged_validator_into_contributor_source(tmp_path):
    runtime, scripts, package = prepare(tmp_path, "bundle")
    (scripts / "runtime-manifest.json").unlink()
    validator = package / "update_notice.py"
    marker = tmp_path / "undeclared-validator-executed"
    validator.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        + validator.read_text()
    )
    expected = snapshot(runtime)
    result = run(tmp_path, load(scripts, "direct"))
    assert result.returncode != 0
    assert not marker.exists() and snapshot(runtime) == expected

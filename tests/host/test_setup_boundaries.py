"""Exercise host boundaries with explicit mocks; no Ada runtime claim is made."""

import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tomllib

import ada_mcp_setup as setup
import mcp_client
import pytest
from image_fixtures import classic_identity


def image_archive(config=None, extra=None):
    config = config or {
        "os": "linux",
        "architecture": "amd64",
        "rootfs": {"diff_ids": ["sha256:" + "a" * 64]},
    }
    content = json.dumps(config).encode()
    image_id = "sha256:" + hashlib.sha256(content).hexdigest()
    members = {
        "config.json": content,
        "layer.tar": b"layer",
        "manifest.json": json.dumps([{"Config": "config.json", "Layers": ["layer.tar"]}]).encode(),
    }
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for name, data in members.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        if extra is not None:
            archive.addfile(extra)
    stream.seek(0)
    return stream, image_id


def binding(root, image_id="sha256:" + "b" * 64):
    return {
        "version": 2,
        "image_id": image_id,
        "image_identity": classic_identity(image_id),
        "roots": [str(root)],
        "docker_host": None,
        "docker_context": None,
        "uid": 1000,
        "gid": 1000,
        "image_source": None,
    }


def test_actual_archive_config_is_verified_before_any_load(tmp_path, monkeypatch):
    stream, actual = image_archive()
    archive = tmp_path / "unrelated.tar"
    archive.write_bytes(stream.getvalue())
    candidate = binding(tmp_path)
    candidate["image_source"] = {
        "kind": "archive",
        "path": str(archive),
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    monkeypatch.setattr(
        setup.subprocess, "run", lambda *args, **kwargs: pytest.fail("Docker started")
    )
    report = {}
    with pytest.raises(RuntimeError, match="config image ID differs"):
        setup.provision_image(candidate, report, 1)
    assert report["archive"]["image_validation"]["actual_image_id"] == actual
    assert report["archive"]["image_validation"]["status"] == "failed"


def test_single_image_metadata_and_amd64_are_required():
    stream, image_id = image_archive()
    evidence = {}
    setup.validate_docker_archive(stream, image_id, evidence)
    assert evidence["image_validation"]["verified_before_load"] is True
    assert not stream.closed
    stream, image_id = image_archive(
        {"os": "linux", "architecture": "arm64", "rootfs": {"diff_ids": ["x"]}}
    )
    with pytest.raises(RuntimeError, match="linux/amd64"):
        setup.validate_docker_archive(stream, image_id, {})
    stream, image_id = image_archive(extra=tarfile.TarInfo("manifest.json"))
    with pytest.raises(RuntimeError, match="duplicate"):
        setup.validate_docker_archive(stream, image_id, {})


def test_inspect_timeout_is_unknown_and_preserves_partial_evidence(monkeypatch):
    def timeout(command, **kwargs):
        assert kwargs["timeout"] == 0.01
        assert "Config.Env" not in command[command.index("--format") + 1]
        raise subprocess.TimeoutExpired(command, 0.01, output=b"partial", stderr=b"timed out")

    monkeypatch.setattr(setup.subprocess, "run", timeout)
    observations = []
    with pytest.raises(subprocess.TimeoutExpired):
        setup.inspect_container(["docker"], {}, "owned-name", observations, 0.01)
    assert observations[0]["status"] == "unknown"
    assert observations[0]["stdout"] == "partial"
    assert observations[0]["timed_out"] is True


@pytest.mark.parametrize(
    "stderr,absent",
    [
        ("Error response from daemon: No such container: exact-name\n", True),
        ("Cannot connect to the Docker daemon", False),
        ("permission denied", False),
        ("Error response from daemon: No such container: wrong-name", False),
    ],
)
def test_absence_is_not_inferred_from_arbitrary_failure(monkeypatch, stderr, absent):
    monkeypatch.setattr(
        setup.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 1, "", stderr),
    )
    observations = []
    if absent:
        assert setup.inspect_container(["docker"], {}, "exact-name", observations, 1) is None
    else:
        with pytest.raises(RuntimeError, match="unknown"):
            setup.inspect_container(["docker"], {}, "exact-name", observations, 1)


@pytest.mark.parametrize("key", ["uid", "gid"])
def test_root_identity_is_refused_before_runtime(tmp_path, key):
    candidate = binding(tmp_path)
    candidate[key] = 0
    with pytest.raises(RuntimeError, match="nonzero"):
        setup.validate_binding(
            candidate,
            {"image_id": candidate["image_id"], "image_identity": candidate["image_identity"]},
        )


def test_explicit_docker_selection_clears_only_conflicting_selectors(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCKER_HOST", "tcp://wrong")
    monkeypatch.setenv("DOCKER_CONTEXT", "wrong")
    monkeypatch.setenv("DOCKER_CONFIG", "/keep/credential-selector")
    candidate = binding(tmp_path)
    candidate["docker_host"] = "unix:///selected.sock"
    command, environment = setup.docker_binding(candidate)
    assert command == ["docker", "--host", "unix:///selected.sock"]
    assert "DOCKER_HOST" not in environment and "DOCKER_CONTEXT" not in environment
    assert environment["DOCKER_CONFIG"] == "/keep/credential-selector"
    assert os.environ["DOCKER_HOST"] == "tcp://wrong"


def test_native_toml_supports_non_bmp_and_control_escaping():
    values = ["/tmp/project 😀/library.gpr", "delete\x7f", 'quote"', "slash\\"]
    assert tomllib.loads("args = " + setup.toml_string_array(values))["args"] == values


def test_binding_and_config_writes_never_replace_existing(tmp_path):
    target = tmp_path / "existing"
    target.write_text("keep")
    with pytest.raises(FileExistsError):
        setup.write_new(target, "replace")
    assert target.read_text() == "keep"
    assert not list(tmp_path.glob(".ada-mcp-*"))


def test_installer_verifies_text_resources_and_only_prepares_launcher(tmp_path, monkeypatch):
    source = tmp_path / "skill-source"
    (source / "scripts").mkdir(parents=True)
    files = {
        "SKILL.md": b"name: example\n",
        "LICENSE": b"MIT\n",
        "scripts/ada-mcp-launch": b"#!/bin/bash\n",
        "scripts/helper.py": b"pass\n",
    }
    for name, content in files.items():
        path = source / name
        path.write_bytes(content)
        path.chmod(0o644)
    manifest = {
        "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }
    (source / "scripts/runtime-manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(setup, "SKILL_ROOT", source)
    target = tmp_path / "repo/.agents/skills/ada-development"
    report = {}
    setup.install_skill(target, manifest, report)
    assert target.is_symlink()
    assert not target.resolve().is_relative_to(target.parent.resolve())
    assert (target / "scripts/ada-mcp-launch").stat().st_mode & 0o100
    assert not (target / "scripts/helper.py").stat().st_mode & 0o111
    with pytest.raises(RuntimeError, match="already exists"):
        setup.install_skill(target, manifest, {})
    assert (target / "LICENSE").read_bytes() == files["LICENSE"]


def test_existing_evidence_directory_is_not_written(tmp_path, monkeypatch):
    directory = tmp_path / "existing"
    directory.mkdir()
    (directory / "summary.json").write_text("original")
    monkeypatch.setattr(setup, "verified_manifest", lambda: {})
    monkeypatch.setattr(sys, "argv", ["setup", "doctor", "--output", str(directory)])
    assert setup.main() == 1
    assert (directory / "summary.json").read_text() == "original"


@pytest.mark.parametrize(
    "call",
    [
        {"tool": "ada_build", "arguments": {}},
        {"tool": "ada_format_file", "arguments": {}},
        {"tool": "ada_rename_symbol", "arguments": {"preview": 1}},
    ],
)
def test_write_calls_are_rejected_before_subprocess(call, monkeypatch):
    monkeypatch.setattr(
        mcp_client.subprocess, "Popen", lambda *args, **kwargs: pytest.fail("process started")
    )
    with pytest.raises(ValueError):
        mcp_client.validate_calls([call])

"""Validate real packaging boundaries with small fixtures, without Docker or publishing."""

import ast
import hashlib
import io
import json
import re
import tarfile

import acquire
import artifacts
import host_acceptance
import promote
import pytest
from image_fixtures import classic_identity, metadata_archive
from version import ROOT, project_version

from ada_mcp import __version__
from ada_mcp.server import server


def test_one_project_version_reaches_mcp_and_python_metadata():
    assert project_version() == "0.2.0-rc.1"
    assert __version__ == "0.2.0rc1"
    assert server.create_initialization_options().server_version == __version__


def test_tooling_and_light_skill_pin_exact_generated_bytes(tmp_path):
    image = tmp_path / "image.tar.gz"
    stream, config_id, target = metadata_archive(oci=True)
    image.write_bytes(stream.getvalue())
    manifest = artifacts.package(ROOT, tmp_path, "a" * 40, target, image)
    tools = tmp_path / manifest["tooling"]["filename"]
    data = tools.read_bytes()
    verified = acquire.verified_files(
        data, manifest["tooling"]["sha256"], manifest["tooling"]["runtime_manifest_sha256"]
    )
    runtime = json.loads(verified["scripts/runtime-manifest.json"])
    assert runtime["project_version"] == project_version()
    assert runtime["source_sha"] == "a" * 40
    assert runtime["image_id"] == config_id and config_id != target
    assert runtime["image_identity"]["target"]["digest"] == target
    assert verified["references/support.md"] == (ROOT / "doc/support.md").read_bytes()
    assert "support.md" in verified["references/setup.md"].decode()
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", verified["references/setup.md"].decode()):
        assert "references/" + target in verified
    assert runtime["available_archive"]["sha256"] == hashlib.sha256(image.read_bytes()).hexdigest()
    assert len(runtime["server_tools"]) == 19
    plugin = tmp_path / manifest["plugin"]["filename"]
    code = host_acceptance.plugin_acquirer(plugin)
    ast.parse(code)
    assert code.strip() == (ROOT / "tooling/acquire.py").read_bytes().strip()
    with tarfile.open(plugin) as archive:
        skill = archive.extractfile("skills/ada-development/SKILL.md").read().decode()
        assert manifest["tooling"]["sha256"] in skill
        assert manifest["tooling"]["runtime_manifest_sha256"] in skill
        assert f'--url "{manifest["tooling"]["download_url"]}"' in skill
        assert "/releases/latest/" not in manifest["tooling"]["download_url"]
        assert not any(member.name.endswith("mcp.json") for member in archive)


def test_deterministic_archives_and_existing_output_protection(tmp_path):
    files = {"a": b"content", "b": b"notice"}
    artifacts.write_tar(tmp_path / "one.tar.gz", files)
    artifacts.write_tar(tmp_path / "two.tar.gz", files)
    assert (tmp_path / "one.tar.gz").read_bytes() == (tmp_path / "two.tar.gz").read_bytes()
    with pytest.raises(FileExistsError):
        artifacts.write_tar(tmp_path / "one.tar.gz", {"a": b"changed"})


def test_release_plan_refuses_unapproved_source_and_tampering(tmp_path):
    archive = tmp_path / "tooling.tar.gz"
    archive.write_bytes(b"tested bytes")
    expected = hashlib.sha256(archive.read_bytes()).hexdigest()
    record = {"filename": archive.name, "sha256": expected}
    manifest = {
        "version": "0.2.0-rc.1",
        "source_sha": "a" * 40,
        "image_id": "sha256:" + "b" * 64,
        "image_identity": classic_identity("sha256:" + "b" * 64),
        "platform": "linux/amd64",
        "python_distributions": {
            "version": 2,
            "tested_image_target": "sha256:" + "b" * 64,
            "tested_image_platform": "linux/amd64",
        },
        "artifacts_sha256": {archive.name: expected},
        "image_archive": record,
        "tooling": record,
        "plugin": record,
    }
    (tmp_path / "release-manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="approved revision"):
        promote.validate_release(tmp_path, "c" * 40)
    checked = promote.validate_release(tmp_path, "a" * 40)
    assert promote.plan(checked)["rebuild"] is False
    archive.write_bytes(b"untested replacement")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        promote.validate_release(tmp_path, "a" * 40)


def test_publication_requires_explicit_source_bound_permission(tmp_path, monkeypatch):
    monkeypatch.delenv("ADA_MCP_PUBLISH_APPROVED_SOURCE", raising=False)
    monkeypatch.setattr(
        promote.subprocess, "run", lambda *args, **kwargs: pytest.fail("external write")
    )
    with pytest.raises(PermissionError, match="approval"):
        promote.execute(tmp_path, {"source_sha": "a" * 40})


def test_inline_plugin_reader_rejects_special_members(tmp_path):
    plugin = tmp_path / "plugin.tar.gz"
    with tarfile.open(plugin, "w:gz") as archive:
        link = tarfile.TarInfo("skills/ada-development/SKILL.md")
        link.type = tarfile.SYMTYPE
        link.linkname = "/outside"
        archive.addfile(link, io.BytesIO())
    with pytest.raises(ValueError, match="invalid"):
        host_acceptance.plugin_acquirer(plugin)

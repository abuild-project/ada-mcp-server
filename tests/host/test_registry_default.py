"""Exercise registry-first host provisioning with locked, non-executable fixtures."""

import hashlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import ada_mcp_setup as setup
import image_identity
import pytest
from image_fixtures import corrupt_config_size, metadata_archive
from test_setup_boundaries import binding
from version import project_version


def source_case(tmp_path):
    stream, config, target = metadata_archive(oci=True)
    cache = tmp_path / "images"
    cache.mkdir()
    archive = cache / "fixture-image.tar"
    archive.write_bytes(stream.getvalue())
    candidate = binding(tmp_path, config)
    candidate["image_identity"] = image_identity.archive_identity(stream)
    manifest = {
        "project_version": project_version(),
        "source_sha": "a" * 40,
        "image_id": config,
        "image_identity": candidate["image_identity"],
        "available_archive": {
            "filename": archive.name,
            "download_url": "https://example.invalid/fixture-image.tar",
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "bytes": archive.stat().st_size,
        },
    }
    candidate["image_source"] = {
        "kind": "registry-fallback",
        "reference": setup.default_registry(manifest),
        "cache": str(cache),
    }
    return candidate, manifest, archive, target


def test_new_binding_defaults_to_registry_and_explicit_sources_remain_available(tmp_path):
    candidate, manifest, archive, _ = source_case(tmp_path)
    options = SimpleNamespace(
        root=[str(tmp_path)],
        archive=None,
        archive_sha256=None,
        registry=None,
        image_cache=str(archive.parent),
        transport=None,
        image_id=None,
        docker_host=None,
        docker_context=None,
        uid=1000,
        gid=1000,
    )
    created = setup.new_binding(options, manifest)
    assert created["image_source"] == candidate["image_source"]
    assert setup.validate_binding(json.loads(json.dumps(created)), manifest) == created
    options.transport = "archive"
    assert setup.new_binding(options, manifest)["image_source"]["kind"] == "download"
    options.archive = str(archive)
    options.image_cache = None
    options.archive_sha256 = manifest["available_archive"]["sha256"]
    assert setup.new_binding(options, manifest)["image_source"]["kind"] == "archive"
    options.archive = None
    options.archive_sha256 = None
    options.registry = "registry.example.org/team/image@sha256:" + "d" * 64
    with pytest.raises(RuntimeError, match="conflicts"):
        setup.new_binding(options, manifest)
    options.transport = None
    assert setup.new_binding(options, manifest)["image_source"] == {
        "kind": "registry",
        "reference": options.registry,
    }


@pytest.mark.parametrize(
    "mode", ["success", "failure", "timeout", "bad-export", "unknown", "bad-cache"]
)
def test_registry_transport_falls_back_only_before_identity_validation(tmp_path, monkeypatch, mode):
    candidate, manifest, archive, target = source_case(tmp_path)
    export = tmp_path / "store.tar"
    export.write_bytes(archive.read_bytes())
    if mode == "bad-export":
        bad, _, _ = metadata_archive(oci=True, mutate=corrupt_config_size)
        export.write_bytes(bad.getvalue())
    elif mode == "bad-cache":
        archive.write_bytes(b"corrupted cached archive")
    fake = tmp_path / "docker.py"
    fake.write_text("""import json, sys, time
from pathlib import Path
mode, target, export = sys.argv[1:4]
args = sys.argv[4:]
if args[:2] == ["image", "pull"]:
    assert args[2:4] == ["--platform", "linux/amd64"]
    assert args[-1].startswith("ghcr.io/abuild-project/ada-mcp-server:v")
    if mode == "timeout": time.sleep(3)
    if mode in {"failure", "bad-cache"}:
        print("registry unavailable", file=sys.stderr)
        raise SystemExit(1)
    print("Pulled release locator")
elif args[:2] == ["image", "load"]:
    sys.stdin.buffer.read()
    print("Loaded image ID: " + target)
elif args[:2] == ["image", "inspect"]:
    if mode == "unknown":
        print("permission denied", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(dict(Id=target, Os="linux", Architecture="amd64", Labels={})))
elif args[:2] == ["image", "save"]:
    assert args[-1] == target
    sys.stdout.buffer.write(Path(export).read_bytes())
else: raise SystemExit("unexpected Docker command")
""")
    monkeypatch.setattr(
        setup,
        "docker_binding",
        lambda _: ([sys.executable, str(fake), mode, target, str(export)], dict(os.environ)),
    )
    report = {}
    original_source = dict(candidate["image_source"])
    if mode in {"bad-export", "unknown", "bad-cache"}:
        with pytest.raises((RuntimeError, ValueError)):
            setup.provision_image(candidate, report, 1, manifest)
        assert not any("load" in x["argv"] for x in report["commands"])
        if mode != "bad-cache":
            assert "archive" not in report and "download" not in report
    else:
        setup.provision_image(candidate, report, 1, manifest)
        fallback = mode != "success"
        assert report["image_transport"]["used"] == ("archive" if fallback else "registry")
        assert any("load" in x["argv"] for x in report["commands"]) is fallback
        assert ("download" in report) is fallback
        assert setup.target_id(candidate) == target
        if fallback:
            assert report["download"]["cache_hit"]
            assert report["archive"]["verified_before_load"]
    assert candidate["image_source"] == original_source


def test_warm_default_can_reuse_locked_target_without_a_pull(tmp_path, monkeypatch, capsys):
    _, manifest, archive, _ = source_case(tmp_path)
    path = tmp_path / "new-binding.json"
    monkeypatch.setattr(setup, "verified_manifest", lambda: manifest)
    monkeypatch.setattr(setup, "image_present", lambda *args: True)
    monkeypatch.setattr(setup, "doctor", lambda *args: None)
    monkeypatch.setattr(setup, "tag_image", lambda *args: None)
    monkeypatch.setattr(setup, "provision_image", lambda *args: pytest.fail("unnecessary pull"))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "setup",
            "bootstrap",
            "--binding",
            str(path),
            "--root",
            str(tmp_path),
            "--uid",
            "1000",
            "--gid",
            "1000",
            "--image-cache",
            str(archive.parent),
        ],
    )
    assert setup.main() == 0, capsys.readouterr().out
    assert json.loads(path.read_text())["image_source"]["kind"] == "registry-fallback"


@pytest.mark.parametrize(
    "field,value", [("reference", "ghcr.io/other/image:v0.2.0-rc.3"), ("cache", "relative")]
)
def test_default_source_rejects_other_registry_or_relative_cache(tmp_path, field, value):
    candidate, manifest, _, _ = source_case(tmp_path)
    candidate["image_source"][field] = value
    with pytest.raises(RuntimeError):
        setup.validate_binding(candidate, manifest)


@pytest.mark.parametrize(
    "platform,xdg,expected",
    [
        ("darwin", None, "Library/Caches/ada-mcp/images"),
        ("darwin", "/ignored-xdg", "Library/Caches/ada-mcp/images"),
        ("linux", None, ".cache/ada-mcp/images"),
        ("linux", "", ".cache/ada-mcp/images"),
        ("linux", "relative/cache", ".cache/ada-mcp/images"),
        ("linux", "/absolute-cache", "/absolute-cache/ada-mcp/images"),
    ],
)
def test_native_cache_default_is_absolute_and_has_no_filesystem_effect(
    tmp_path, monkeypatch, platform, xdg, expected
):
    home = tmp_path / "home"
    monkeypatch.setattr(setup.Path, "home", lambda: home)
    monkeypatch.setattr(setup.sys, "platform", platform)
    if xdg is None:
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    else:
        monkeypatch.setenv("XDG_CACHE_HOME", xdg)
    expected_path = Path(expected) if expected.startswith("/") else home / expected
    assert setup.default_image_cache() == expected_path
    assert expected_path.is_absolute()
    assert not home.exists()


def test_explicit_cache_overrides_platform_default(tmp_path, monkeypatch):
    _, manifest, archive, _ = source_case(tmp_path)
    options = SimpleNamespace(
        root=[str(tmp_path)],
        archive=None,
        archive_sha256=None,
        registry=None,
        image_cache=str(archive.parent),
        transport=None,
        image_id=None,
        docker_host=None,
        docker_context=None,
        uid=1000,
        gid=1000,
    )
    monkeypatch.setattr(setup, "default_image_cache", lambda: pytest.fail("default cache used"))
    created = setup.new_binding(options, manifest)
    assert created["image_source"]["cache"] == str(archive.parent)


@pytest.mark.parametrize("version", ["0.3.0+abc", "0.3.0-beta.1"])
def test_other_version_formats_explain_explicit_archive_selection(tmp_path, version):
    _, manifest, archive, _ = source_case(tmp_path)
    manifest["project_version"] = version
    options = SimpleNamespace(
        root=[str(tmp_path)],
        archive=None,
        archive_sha256=None,
        registry=None,
        image_cache=str(archive.parent),
        transport=None,
        image_id=None,
        docker_host=None,
        docker_context=None,
        uid=1000,
        gid=1000,
    )
    with pytest.raises(RuntimeError, match=r"require X.Y.Z or X.Y.Z-rc.N; use --transport archive"):
        setup.new_binding(options, manifest)
    options.transport = "archive"
    assert setup.new_binding(options, manifest)["image_source"]["kind"] == "download"


def test_registry_binding_survives_optional_alias_conflict(tmp_path, monkeypatch, capsys):
    candidate, manifest, archive, target = source_case(tmp_path)
    path = tmp_path / "combined-binding.json"
    events = []
    monkeypatch.setattr(setup, "verified_manifest", lambda: manifest)
    monkeypatch.setattr(setup, "image_present", lambda *args: True)
    monkeypatch.setattr(setup, "doctor", lambda *args: events.append("doctor"))
    monkeypatch.setattr(setup, "provision_image", lambda *args: pytest.fail("unnecessary pull"))

    def conflicting_alias(docker, environment, reference, report, timeout):
        assert events == ["doctor"]
        assert reference == "ada-mcp-server:v" + project_version()
        return dict(Id="sha256:" + "f" * 64)

    monkeypatch.setattr(setup, "inspect_image", conflicting_alias)
    monkeypatch.setattr(
        setup, "command_run", lambda *args, **kwargs: pytest.fail("tag overwritten")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "setup",
            "bootstrap",
            "--binding",
            str(path),
            "--root",
            str(tmp_path),
            "--uid",
            "1000",
            "--gid",
            "1000",
            "--image-cache",
            str(archive.parent),
        ],
    )
    assert setup.main() == 0
    report = json.loads(capsys.readouterr().out)
    saved = json.loads(path.read_text())
    assert report["status"] == "passed" and report["image_tag"]["status"] == "conflict"
    assert saved["image_source"] == candidate["image_source"]
    assert setup.target_id(saved) == target

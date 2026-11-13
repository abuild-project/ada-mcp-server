"""Small real Git/package boundaries; these are not built Ada runtime artifacts."""

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import zipfile

import artifacts
import distribution_receipt as receipt
import pytest


@pytest.fixture
def checked_pair(tmp_path):
    root = tmp_path / "repo"
    package = root / "src/ada_mcp"
    package.mkdir(parents=True)
    (package / "server.py").write_bytes(b"COMMITTED_SENTINEL = True\n")
    (package / "_version.py").write_text('VERSION = "0.2.0-rc.1"\n')
    git = ["git", "-C", str(root)]
    subprocess.run(
        git + ["init", "--initial-branch", "codex/provenance"], check=True, capture_output=True
    )
    subprocess.run(git + ["add", "."], check=True)
    subprocess.run(
        git
        + [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "Fixture",
        ],
        check=True,
        capture_output=True,
    )
    sha = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    archive = tmp_path / "committed.tar"
    archive.write_bytes(subprocess.check_output(git + ["archive", "--format=tar", sha]))
    folder = tmp_path / "checked-python-dist"
    folder.mkdir()
    metadata = b"Name: ada-mcp-server\nVersion: 0.2.0rc1\n\n"
    prefix = "ada_mcp_server-0.2.0rc1"
    wheel = folder / (prefix + "-py3-none-any.whl")
    sdist = folder / (prefix + ".tar.gz")
    with zipfile.ZipFile(wheel, "w") as output:
        output.writestr(prefix + ".dist-info/METADATA", metadata)
        for path in package.iterdir():
            output.writestr("ada_mcp/" + path.name, path.read_bytes())
    with tarfile.open(sdist, "w:gz") as output:
        files = {prefix + "/PKG-INFO": metadata}
        files.update(
            {prefix + "/src/ada_mcp/" + path.name: path.read_bytes() for path in package.iterdir()}
        )
        for name, content in files.items():
            member = tarfile.TarInfo(name)
            member.size = len(content)
            output.addfile(member, io.BytesIO(content))
    return root, folder, sha, archive


def test_receipt_binds_actual_snapshot_and_distribution_bytes(checked_pair):
    root, folder, sha, archive = checked_pair
    recorded = receipt.write_receipt(
        root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64"
    )
    paths, observed = artifacts.validate_python_distributions(
        folder, "0.2.0-rc.1", sha, receipt.committed_archive_sha256(root, sha)
    )
    assert recorded == observed
    assert recorded["version"] == 2
    assert recorded["tested_image_target"] == "sha256:" + "a" * 64
    assert recorded["tested_image_platform"] == "linux/amd64"
    assert {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths} == observed[
        "distributions_sha256"
    ]
    before = (folder / receipt.RECEIPT).read_bytes()
    with pytest.raises(FileExistsError):
        receipt.write_receipt(root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64")
    assert (folder / receipt.RECEIPT).read_bytes() == before


@pytest.mark.parametrize(
    "defect",
    ["missing", "source", "snapshot", "wheel-bytes", "sdist-bytes", "receipt-hash", "receipt-set"],
)
def test_same_version_is_not_a_substitute_for_checked_provenance(checked_pair, defect):
    root, folder, sha, archive = checked_pair
    recorded = receipt.write_receipt(
        root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64"
    )
    path = folder / receipt.RECEIPT
    if defect == "missing":
        path.unlink()
    elif defect == "source":
        recorded["source_sha"] = "f" * 40
    elif defect == "snapshot":
        recorded["source_archive_sha256"] = "f" * 64
    elif defect in {"wheel-bytes", "sdist-bytes"}:
        extension = "*.whl" if defect == "wheel-bytes" else "*.tar.gz"
        package = next(folder.glob(extension))
        package.write_bytes(package.read_bytes() + b"changed same-version bytes")
    elif defect == "receipt-hash":
        recorded["distributions_sha256"][next(iter(recorded["distributions_sha256"]))] = "f" * 64
    elif defect == "receipt-set":
        recorded["distributions_sha256"].pop(next(iter(recorded["distributions_sha256"])))
    if defect not in {"missing", "wheel-bytes", "sdist-bytes"}:
        path.write_text(json.dumps(recorded))
    with pytest.raises(ValueError):
        artifacts.validate_python_distributions(
            folder, "0.2.0-rc.1", sha, hashlib.sha256(archive.read_bytes()).hexdigest()
        )


@pytest.mark.parametrize("kind", ["wheel", "sdist"])
def test_writer_cannot_issue_current_source_receipt_for_stale_payload(checked_pair, kind):
    root, folder, sha, archive = checked_pair
    path = next(folder.glob("*.whl" if kind == "wheel" else "*.tar.gz"))
    if kind == "wheel":
        with zipfile.ZipFile(path) as package:
            files = {name: package.read(name) for name in package.namelist()}
        files["ada_mcp/server.py"] = b"OTHER_SOURCE_SAME_VERSION = True\n"
        with zipfile.ZipFile(path, "w") as package:
            for name, content in files.items():
                package.writestr(name, content)
    else:
        with tarfile.open(path) as package:
            files = {
                member.name: package.extractfile(member).read()
                for member in package
                if member.isfile()
            }
        key = next(name for name in files if name.endswith("/server.py"))
        files[key] = b"OTHER_SOURCE_SAME_VERSION = True\n"
        with tarfile.open(path, "w:gz") as package:
            for name, content in files.items():
                member = tarfile.TarInfo(name)
                member.size = len(content)
                package.addfile(member, io.BytesIO(content))
    with pytest.raises(ValueError, match="payload differs"):
        receipt.write_receipt(root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64")
    assert not (folder / receipt.RECEIPT).exists()


def test_writer_rejects_actual_tree_changed_after_commit(checked_pair):
    root, folder, sha, archive = checked_pair
    (root / "src/ada_mcp/server.py").write_text("UNCOMMITTED = True\n")
    with pytest.raises(ValueError, match="checked source"):
        receipt.write_receipt(root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64")
    assert not (folder / receipt.RECEIPT).exists()


@pytest.mark.parametrize(
    "defect",
    ["legacy", "missing-target", "short-target", "tag", "platform", "non-object", "float-version"],
)
def test_receipt_without_strict_checked_native_target_is_rejected(checked_pair, defect):
    root, folder, sha, archive = checked_pair
    data = receipt.write_receipt(root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64")
    if defect == "legacy":
        data["version"] = 1
    elif defect == "missing-target":
        data.pop("tested_image_target")
    elif defect == "short-target":
        data["tested_image_target"] = "sha256:abc"
    elif defect == "tag":
        data["tested_image_target"] = "same-source:candidate"
    elif defect == "platform":
        data["tested_image_platform"] = "linux/arm64"
    elif defect == "float-version":
        data["version"] = 2.0
    else:
        data = []
    (folder / receipt.RECEIPT).write_text(json.dumps(data))
    with pytest.raises(ValueError):
        receipt.validate_receipt(folder, "0.2.0-rc.1", sha, receipt.sha256_file(archive))


@pytest.mark.parametrize("same_image", [False, True])
def test_packaging_checks_native_image_before_export_and_allows_identical_retag(
    checked_pair, tmp_path, monkeypatch, same_image
):
    root, folder, sha, archive = checked_pair
    receipt.write_receipt(root, folder, sha, archive, "sha256:" + "a" * 64, "linux/amd64")
    monkeypatch.setattr(artifacts, "ROOT", root)
    monkeypatch.setattr(
        artifacts,
        "inspect_image",
        lambda *_args: {
            "Id": "sha256:" + ("a" if same_image else "b") * 64,
            "Os": "linux",
            "Architecture": "amd64",
            "Labels": {
                "org.opencontainers.image.revision": sha,
                "org.opencontainers.image.version": "0.2.0-rc.1",
            },
        },
    )
    original = subprocess.Popen

    class ExportReachedError(Exception):
        pass

    def git_only(argv, *args, **kwargs):
        if argv[0] != "git":
            assert argv[:3] == ["docker", "image", "save"]
            raise ExportReachedError("bounded control stops before any Docker call")
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", git_only)
    output = tmp_path / "new-release"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "artifacts",
            "--image",
            "retagged:candidate",
            "--python-dist",
            str(folder),
            "--output",
            str(output),
        ],
    )
    if same_image:
        with pytest.raises(ExportReachedError):
            artifacts.main()
    else:
        with pytest.raises(ValueError, match="image target/platform was not checked"):
            artifacts.main()
    assert not list(output.glob("*.tar.gz"))
    assert not (output / "release-manifest.json").exists()


@pytest.mark.parametrize("kind", ["legacy", "hybrid", "oci"])
def test_checked_native_target_does_not_confuse_config_with_oci_index(kind):
    from image_fixtures import metadata_archive
    from image_identity import archive_identity

    stream, config, target = metadata_archive(oci=kind == "oci", hybrid=kind == "hybrid")
    provenance = {
        "version": 2,
        "tested_image_target": target,
        "tested_image_platform": "linux/amd64",
    }
    receipt.validate_checked_target(provenance, target, "linux/amd64")
    identity = archive_identity(stream, config, target)
    assert identity["image_id"] == config and identity["target"]["digest"] == target
    if kind == "oci":
        assert config != target
        with pytest.raises(ValueError):
            receipt.validate_checked_target(provenance, config, "linux/amd64")

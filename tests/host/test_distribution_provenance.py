"""Small real Git/package boundaries; these are not built Ada runtime artifacts."""

import hashlib
import io
import json
import subprocess
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
    recorded = receipt.write_receipt(root, folder, sha, archive)
    paths, observed = artifacts.validate_python_distributions(
        folder, "0.2.0-rc.1", sha, receipt.committed_archive_sha256(root, sha)
    )
    assert recorded == observed
    assert {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths} == observed[
        "distributions_sha256"
    ]
    before = (folder / receipt.RECEIPT).read_bytes()
    with pytest.raises(FileExistsError):
        receipt.write_receipt(root, folder, sha, archive)
    assert (folder / receipt.RECEIPT).read_bytes() == before


@pytest.mark.parametrize(
    "defect",
    ["missing", "source", "snapshot", "wheel-bytes", "sdist-bytes", "receipt-hash", "receipt-set"],
)
def test_same_version_is_not_a_substitute_for_checked_provenance(checked_pair, defect):
    root, folder, sha, archive = checked_pair
    recorded = receipt.write_receipt(root, folder, sha, archive)
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
        receipt.write_receipt(root, folder, sha, archive)
    assert not (folder / receipt.RECEIPT).exists()


def test_writer_rejects_actual_tree_changed_after_commit(checked_pair):
    root, folder, sha, archive = checked_pair
    (root / "src/ada_mcp/server.py").write_text("UNCOMMITTED = True\n")
    with pytest.raises(ValueError, match="checked source"):
        receipt.write_receipt(root, folder, sha, archive)
    assert not (folder / receipt.RECEIPT).exists()

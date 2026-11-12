# SPDX-License-Identifier: MIT
"""Bind checked Python distribution bytes to the committed-source CI snapshot."""

import argparse
import email
import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from version import ROOT, project_version

JSON = dict[str, Any]
RECEIPT = "provenance.json"


def sha256_file(path: Path) -> str:
    """Hash the exact bytes of a file, without loading an archive into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def distribution_files(folder: Path, version: str) -> list[Path]:
    """Require exactly one matching wheel/sdist pair and validate their metadata."""
    python_version = version.replace("-rc.", "rc")
    names = {
        f"ada_mcp_server-{python_version}-py3-none-any.whl",
        f"ada_mcp_server-{python_version}.tar.gz",
    }
    actual = {path.name for path in folder.iterdir()}
    if actual - {RECEIPT} != names:
        raise ValueError("provide exactly the two checked Python distributions for this version")
    paths = [folder / name for name in sorted(names)]
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError("Python distributions must be regular, nonsymlink files")
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as wheel:
                wheel_members = [
                    name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
                ]
                if len(wheel_members) != 1:
                    raise ValueError("wheel must have one metadata record")
                metadata = wheel.read(wheel_members[0])
        else:
            with tarfile.open(path) as archive:
                sdist_members = [
                    member
                    for member in archive
                    if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
                ]
                if len(sdist_members) != 1 or not sdist_members[0].isfile():
                    raise ValueError("sdist must have one regular package metadata record")
                stream = archive.extractfile(sdist_members[0])
                assert stream is not None
                with stream:
                    metadata = stream.read()
        message = email.message_from_bytes(metadata)
        if message["Name"] != "ada-mcp-server" or message["Version"] != python_version:
            raise ValueError("Python distribution metadata differs from the canonical version")
    return paths


def committed_archive_sha256(root: Path, source_sha: str) -> str:
    """Hash Git's committed tar snapshot using the same format as docker/check."""
    with tempfile.TemporaryFile() as stream:
        subprocess.run(
            ["git", "-C", str(root), "archive", "--format=tar", source_sha],
            stdout=stream,
            check=True,
        )
        stream.seek(0)
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def verify_checked_snapshot(root: Path, source_archive: Path) -> tuple[str, dict[str, str]]:
    """Compare every committed file with the actual tree used by the check chain."""
    seen = set()
    package_hashes = {}
    with tarfile.open(source_archive) as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or str(name) != member.name.rstrip("/"):
                raise ValueError("unsafe committed source snapshot path")
            if member.isdir():
                continue
            if not member.isfile() or member.name in seen:
                raise ValueError("source snapshot must contain unique regular files")
            seen.add(member.name)
            actual = root / member.name
            if not actual.is_file() or actual.is_symlink():
                raise ValueError("checked source file is missing or aliased: " + member.name)
            expected = archive.extractfile(member)
            assert expected is not None
            with expected, actual.open("rb") as stream:
                digest = hashlib.sha256()
                for block in iter(lambda: expected.read(1024 * 1024), b""):
                    digest.update(block)
                    if stream.read(len(block)) != block:
                        raise ValueError(
                            "checked source differs from committed snapshot: " + member.name
                        )
                if stream.read(1):
                    raise ValueError("checked source has additional bytes: " + member.name)
            if member.name.startswith("src/ada_mcp/"):
                package_hashes[member.name.removeprefix("src/")] = digest.hexdigest()
    if not seen:
        raise ValueError("committed source snapshot is empty")
    if not package_hashes:
        raise ValueError("committed snapshot contains no server package")
    return sha256_file(source_archive), package_hashes


def verify_package_payloads(paths: list[Path], expected: dict[str, str]) -> None:
    """Do not issue a current-source receipt for stale same-version package code."""
    for path in paths:
        actual = {}
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as wheel:
                for name in wheel.namelist():
                    if name.startswith("ada_mcp/") and not name.endswith("/"):
                        if name in actual:
                            raise ValueError("duplicate wheel package member")
                        actual[name] = hashlib.sha256(wheel.read(name)).hexdigest()
        else:
            with tarfile.open(path) as archive:
                for member in archive:
                    parts = PurePosixPath(member.name).parts
                    if len(parts) < 4 or parts[1:3] != ("src", "ada_mcp") or member.isdir():
                        continue
                    name = "/".join(parts[2:])
                    if name in actual or not member.isfile():
                        raise ValueError("sdist package members must be unique regular files")
                    stream = archive.extractfile(member)
                    assert stream is not None
                    with stream:
                        actual[name] = hashlib.sha256(stream.read()).hexdigest()
        if actual != expected:
            raise ValueError("Python package payload differs from committed source: " + path.name)


def write_receipt(root: Path, folder: Path, source_sha: str, source_archive: Path) -> JSON:
    """Write once, only after the complete CI chain has checked these bytes."""
    if not re.fullmatch("[0-9a-f]{40}", source_sha):
        raise ValueError("provide the committed source SHA from docker/check")
    snapshot_sha, package_hashes = verify_checked_snapshot(root, source_archive)
    paths = distribution_files(folder, project_version(root))
    verify_package_payloads(paths, package_hashes)
    receipt = {
        "version": 1,
        "source_sha": source_sha,
        "source_archive_sha256": snapshot_sha,
        "project_version": project_version(root),
        "distributions_sha256": {path.name: sha256_file(path) for path in paths},
    }
    with (folder / RECEIPT).open("x") as stream:
        stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def validate_receipt(folder: Path, version: str, source_sha: str, archive_sha256: str) -> JSON:
    """Reject missing/stale receipts or changed same-version distribution bytes."""
    path = folder / RECEIPT
    if not path.is_file() or path.is_symlink():
        raise ValueError("checked Python distribution provenance receipt is missing")
    receipt: JSON = json.loads(path.read_text())
    if set(receipt) != {
        "version",
        "source_sha",
        "source_archive_sha256",
        "project_version",
        "distributions_sha256",
    }:
        raise ValueError("invalid Python distribution provenance fields")
    if (
        receipt["version"] != 1
        or receipt["source_sha"] != source_sha
        or receipt["source_archive_sha256"] != archive_sha256
    ):
        raise ValueError("Python distributions were not checked from this committed source")
    if receipt["project_version"] != version:
        raise ValueError("Python distribution provenance version differs")
    paths = distribution_files(folder, version)
    hashes = receipt["distributions_sha256"]
    if not isinstance(hashes, dict) or set(hashes) != {item.name for item in paths}:
        raise ValueError("Python distribution provenance hash set differs")
    for item in paths:
        if hashes[item.name] != sha256_file(item):
            raise ValueError("checked Python distribution SHA256 mismatch: " + item.name)
    return receipt


def main() -> None:
    """Called last by scripts/ci with docker/check's read-only Git archive input."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    options = parser.parse_args()
    print(
        json.dumps(
            write_receipt(ROOT, options.folder, options.source_sha, options.source_archive),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

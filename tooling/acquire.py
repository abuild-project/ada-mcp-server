#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Acquire a complete tooling bundle using trusted version-specific hashes."""

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import tarfile
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024


def require(condition: object, message: str) -> None:
    """Reject invalid boundaries before publishing executable files."""
    if not condition:
        raise ValueError(message)


def canonical(name: str) -> str:
    """Accept only canonical relative POSIX names, without path aliases."""
    path = PurePosixPath(name)
    require(
        name and not path.is_absolute() and ".." not in path.parts and str(path) != ".",
        "unsafe archive path",
    )
    require(str(path) == name.rstrip("/") and "\\" not in name, "noncanonical archive path")
    return str(path)


def sha256(data: bytes) -> str:
    """Hash exact bytes rather than normalized text."""
    return hashlib.sha256(data).hexdigest()


class HTTPSRedirects(urllib.request.HTTPRedirectHandler):
    """Keep the verified download on HTTPS, including GitHub asset redirects."""

    def redirect_request(
        self,
        request: urllib.request.Request,
        response: Any,
        code: int,
        message: str,
        headers: Any,
        new_url: str,
    ) -> urllib.request.Request | None:
        require(urllib.parse.urlsplit(new_url).scheme == "https", "HTTPS downgrade refused")
        return super().redirect_request(request, response, code, message, headers, new_url)


def download(url: str, timeout: float = 60) -> bytes:
    """Read a bounded HTTPS asset with inherited proxy and CA settings."""
    parsed = urllib.parse.urlsplit(url)
    require(
        parsed.scheme == "https"
        and parsed.hostname
        and not parsed.username
        and not parsed.password,
        "a credential-free HTTPS artifact URL is required",
    )
    require("/releases/latest/" not in parsed.path, "mutable latest release URLs are refused")
    opener = urllib.request.build_opener(HTTPSRedirects())
    with opener.open(url, timeout=timeout) as response:
        data: bytes = response.read(MAX_ARCHIVE_BYTES + 1)
    require(len(data) <= MAX_ARCHIVE_BYTES, "tooling archive exceeds the size limit")
    return data


def download_file(
    url: str, destination: Path, expected_hash: str, expected_bytes: int
) -> dict[str, object]:
    """Stream a pinned image archive to an explicit cache without replacement."""
    parsed = urllib.parse.urlsplit(url)
    require(
        parsed.scheme == "https"
        and parsed.hostname
        and not parsed.username
        and not parsed.password,
        "a credential-free HTTPS image URL is required",
    )
    require(
        re.fullmatch("[0-9a-f]{64}", expected_hash) and expected_bytes > 0,
        "invalid trusted image download metadata",
    )
    require(destination.is_absolute(), "image cache path must be absolute")
    if os.path.lexists(destination):
        require(
            destination.is_file() and not destination.is_symlink(),
            "image cache is not a regular file",
        )
        digest = hashlib.sha256()
        with destination.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        require(
            destination.stat().st_size == expected_bytes and digest.hexdigest() == expected_hash,
            "existing image cache differs; nothing overwritten",
        )
        return {"cache_hit": True, "path": str(destination), "sha256": expected_hash}
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "wb", dir=destination.parent, prefix=".ada-image-", delete=False
        ) as output:
            temporary = Path(output.name)
            digest = hashlib.sha256()
            count = 0
            opener = urllib.request.build_opener(HTTPSRedirects())
            with opener.open(url, timeout=60) as response:
                while block := response.read(1024 * 1024):
                    count += len(block)
                    require(count <= expected_bytes, "image download exceeds trusted byte count")
                    digest.update(block)
                    output.write(block)
            require(
                count == expected_bytes and digest.hexdigest() == expected_hash,
                "image download size/SHA256 mismatch",
            )
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, destination)
        return {
            "cache_hit": False,
            "path": str(destination),
            "sha256": expected_hash,
            "bytes": count,
        }
    finally:
        if temporary is not None:
            temporary.unlink()


def verified_files(data: bytes, archive_hash: str, manifest_hash: str) -> dict[str, bytes]:
    """Validate archive, manifest and every declared regular member before writes."""
    require(re.fullmatch("[0-9a-f]{64}", archive_hash), "invalid archive SHA256")
    require(re.fullmatch("[0-9a-f]{64}", manifest_hash), "invalid runtime manifest SHA256")
    require(
        len(data) <= MAX_ARCHIVE_BYTES and sha256(data) == archive_hash, "archive SHA256 mismatch"
    )
    files: dict[str, bytes] = {}
    seen: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
        for count, member in enumerate(archive, 1):
            require(count <= 100, "too many tooling archive members")
            name = canonical(member.name)
            require(name not in seen, "duplicate tooling archive member")
            seen.add(name)
            require(
                member.isdir() or member.isfile(), "links and special archive members are refused"
            )
            if member.isdir():
                continue
            require(0 <= member.size <= MAX_FILE_BYTES, "tooling member exceeds size limit")
            stream = archive.extractfile(member)
            require(stream is not None, "missing regular archive payload")
            assert stream is not None
            with stream:
                content = stream.read(MAX_FILE_BYTES + 1)
            require(len(content) == member.size, "truncated tooling archive member")
            files[name] = content
    manifest_name = "scripts/runtime-manifest.json"
    require(
        manifest_name in files and sha256(files[manifest_name]) == manifest_hash,
        "runtime manifest SHA256 mismatch",
    )
    manifest = json.loads(files[manifest_name])
    declared = manifest["files_sha256"]
    require(isinstance(declared, dict) and bool(declared), "missing runtime file declarations")
    require(set(files) == set(declared) | {manifest_name}, "undeclared or missing tooling file")
    for name, expected in declared.items():
        require(
            canonical(name) == name and re.fullmatch("[0-9a-f]{64}", expected),
            "invalid runtime file declaration",
        )
        require(sha256(files[name]) == expected, "tooling file SHA256 mismatch: " + name)
    require("scripts/ada-mcp-launch" in files and "LICENSE" in files, "incomplete tooling bundle")
    return files


def materialize(files: dict[str, bytes], destination: Path) -> dict[str, str]:
    """Write a new private runtime; prepare only the launcher's user execute bit."""
    require(destination.is_absolute(), "destination must be absolute")
    require(not os.path.lexists(destination), "destination exists; nothing overwritten")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(mode=0o700)
    try:
        for name, data in files.items():
            target = destination / name
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fchmod(stream.fileno(), 0o644)
        hashes = {name: sha256((destination / name).read_bytes()) for name in files}
        require(
            all(hashes[name] == sha256(data) for name, data in files.items()),
            "materialized tooling bytes differ",
        )
        launcher = destination / "scripts/ada-mcp-launch"
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
        return hashes
    except BaseException:
        shutil.rmtree(destination)
        raise


def main() -> None:
    """Require explicit trusted hashes and a new runtime destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--archive", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    options = parser.parse_args()
    if options.archive:
        with options.archive.open("rb") as stream:
            data = stream.read(MAX_ARCHIVE_BYTES + 1)
    else:
        data = download(options.url)
    files = verified_files(data, options.sha256, options.manifest_sha256)
    hashes = materialize(files, options.destination)
    print(json.dumps({"runtime": str(options.destination), "files_sha256": hashes}, indent=2))


if __name__ == "__main__":
    main()

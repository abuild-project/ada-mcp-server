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
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024
WORKFLOW_CONTRACT = 1
MAX_SELECTION_BYTES = 64 * 1024


class IncompatibleRuntimeError(ValueError):
    """The installed entry cannot operate this runtime workflow."""


def compatible_contract(value: object) -> None:
    """Accept only the exact workflow interface understood by this entry."""
    if type(value) is not int or value != WORKFLOW_CONTRACT:
        raise IncompatibleRuntimeError(
            "runtime workflow requires an updated compatible skill/plugin entry"
        )


def private_path(value: str | Path) -> Path:
    """Require an absolute, physical parent for user-selected state paths."""
    path = Path(value)
    require(path.is_absolute(), "selection/runtime/binding paths must be absolute")
    require(path.parent.resolve() == path.parent, "state parent must be a physical path")
    return path


def bounded_file(path: Path, limit: int, *, private: bool = False) -> bytes:
    """Read bounded regular files; selection records must belong only to this user."""
    state = path.lstat()
    require(stat.S_ISREG(state.st_mode), "expected a regular file: " + str(path))
    if private:
        require(
            state.st_uid == os.getuid() and state.st_mode & 0o077 == 0,
            "selection must be owned by the current user with private permissions",
        )
    require(state.st_size <= limit, "selection/runtime input exceeds its size bound")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "selection/runtime input exceeds its size bound")
    return data


def inspect_runtime(
    runtime: Path,
    manifest_hash: str,
    binding: Path,
    contract: object,
    expected: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Authenticate a compatible exact runtime and binding before loading any helper."""
    compatible_contract(contract)
    runtime = private_path(runtime)
    binding = private_path(binding)
    require(
        runtime.resolve() == runtime and runtime.is_dir(), "runtime must be a physical directory"
    )
    require(re.fullmatch("[0-9a-f]{64}", manifest_hash), "invalid runtime manifest SHA256")
    data = bounded_file(runtime / "scripts/runtime-manifest.json", MAX_FILE_BYTES)
    require(sha256(data) == manifest_hash, "selected runtime manifest SHA256 mismatch")
    manifest = json.loads(data)
    require(isinstance(manifest, dict), "runtime manifest must be an object")
    compatible_contract(manifest.get("workflow_contract"))
    require(
        type(manifest.get("version")) is int
        and manifest["version"] == 1
        and manifest.get("platform") == "linux/amd64"
        and re.fullmatch("sha256:[0-9a-f]{64}", manifest["image_id"]),
        "invalid runtime schema/platform/image pin",
    )
    require(
        re.fullmatch(r"\d+\.\d+\.\d+(?:-rc\.\d+)?", manifest["project_version"])
        and re.fullmatch("[0-9a-f]{40}", manifest["source_sha"]),
        "invalid runtime version/source",
    )
    if expected is not None:
        require(
            all(
                expected[key] == manifest[key]
                for key in ["project_version", "source_sha", "image_id"]
            ),
            "selected version/source/image metadata mismatch",
        )
    declared = manifest["files_sha256"]
    require(isinstance(declared, dict) and 0 < len(declared) <= 100, "invalid runtime declarations")
    captured = {}
    total = 0
    for name, expected_hash in declared.items():
        require(
            canonical(name) == name and re.fullmatch("[0-9a-f]{64}", expected_hash),
            "invalid runtime file declaration",
        )
        path = runtime / name
        content = bounded_file(path, MAX_FILE_BYTES)
        total += len(content)
        require(total <= MAX_ARCHIVE_BYTES, "runtime files exceed the total size bound")
        require(sha256(content) == expected_hash, "selected runtime file SHA256 mismatch: " + name)
        if path.suffix == ".py":
            captured[path] = content
    setup = runtime / "scripts/ada_mcp_setup.py"
    require(setup in captured, "selected runtime omits its setup helper")
    binding_bytes = bounded_file(binding, MAX_SELECTION_BYTES)
    if expected is not None:
        require(
            sha256(binding_bytes) == expected["binding_sha256"], "selected binding SHA256 mismatch"
        )
    bound = json.loads(binding_bytes)
    require(
        isinstance(bound, dict)
        and type(bound.get("version")) is int
        and bound["version"] == 2
        and bound.get("image_id") == manifest["image_id"]
        and isinstance(bound.get("image_identity"), dict)
        and bound["image_identity"].get("config_size") == manifest["image_identity"]["config_size"],
        "selected binding differs from the runtime image lock",
    )
    # Only fully authenticated sources execute. The existing parser then checks
    # physical roots, image identity, sources and Docker selectors, source-only.
    namespace: dict[str, Any] = {"__name__": "_ada_selected_setup", "__file__": str(setup)}
    exec(compile(captured[setup], str(setup), "exec"), namespace)
    namespace["_verified_sources"].update(captured)
    namespace["validate_binding"](bound, manifest)
    return {
        "schema": 1,
        "workflow_contract": WORKFLOW_CONTRACT,
        "runtime": str(runtime),
        "binding": str(binding),
        "runtime_manifest_sha256": manifest_hash,
        "binding_sha256": sha256(binding_bytes),
        "project_version": manifest["project_version"],
        "source_sha": manifest["source_sha"],
        "image_id": manifest["image_id"],
    }


def selected_runtime(path: Path) -> dict[str, Any]:
    """Resolve only the pinned selected pair; never silently fall back to entry pins."""
    path = private_path(path)
    if not os.path.lexists(path):
        return {"status": "absent", "selection": str(path)}
    data = bounded_file(path, MAX_SELECTION_BYTES, private=True)
    record = json.loads(data)
    fields = {
        "schema",
        "workflow_contract",
        "runtime",
        "binding",
        "runtime_manifest_sha256",
        "binding_sha256",
        "project_version",
        "source_sha",
        "image_id",
    }
    require(
        isinstance(record, dict)
        and set(record) == fields
        and type(record["schema"]) is int
        and record["schema"] == 1,
        "invalid selection record",
    )
    compatible_contract(record["workflow_contract"])
    actual = inspect_runtime(
        Path(record["runtime"]),
        record["runtime_manifest_sha256"],
        Path(record["binding"]),
        record["workflow_contract"],
        expected=record,
    )
    require(actual == record, "selected runtime/binding record mismatch")
    return {
        "status": "selected",
        "selection": str(path),
        "selection_sha256": sha256(data),
        **actual,
    }


def private_new(path: Path, data: bytes) -> None:
    """Write a new private record atomically without replacing another file."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink()


def activate_selection(
    path: Path, record: dict[str, Any], expected: str | None, backup: Path | None
) -> None:
    """Switch explicit local selection with expected-old bytes and a no-clobber backup."""
    path = private_path(path)
    require(
        (expected is None) == (backup is None),
        "replacement requires expected SHA256 and NEW backup",
    )
    if backup is not None:
        backup = private_path(backup)
        require(backup != path, "backup must differ from the selection")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    temporary = None
    try:
        os.close(descriptor)
        data = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        if expected is None:
            private_new(path, data)
        else:
            old = bounded_file(path, MAX_SELECTION_BYTES, private=True)
            require(
                re.fullmatch("[0-9a-f]{64}", expected) and sha256(old) == expected,
                "selection changed; nothing activated",
            )
            assert backup is not None
            private_new(backup, old)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink()


def selection_main(arguments: list[str]) -> int:
    """Read or explicitly activate a compatible pinned runtime; never acquire or install."""
    parser = argparse.ArgumentParser(
        description="Inspect or activate the exact Ada MCP runtime selection"
    )
    parser.add_argument("action", choices=["show", "activate"])
    parser.add_argument(
        "--file",
        default=os.environ.get(
            "ADA_MCP_SELECTION", str(Path.home() / ".config/ada-mcp/selection.json")
        ),
    )
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--workflow-contract", type=int)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--backup", type=Path)
    options = parser.parse_args(arguments)
    try:
        path = private_path(options.file)
        if options.action == "activate":
            require(
                options.runtime and options.manifest_sha256 and options.binding,
                "activation requires verified runtime, manifest SHA256 and binding",
            )
            record = inspect_runtime(
                options.runtime, options.manifest_sha256, options.binding, options.workflow_contract
            )
            activate_selection(path, record, options.expected_sha256, options.backup)
        result = selected_runtime(path)
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as error:
        result = {
            "status": "incompatible" if isinstance(error, IncompatibleRuntimeError) else "invalid",
            "reason": str(error),
        }
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"selected", "absent"} else 1


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


def verified_files(
    data: bytes, archive_hash: str, manifest_hash: str, workflow_contract: object = None
) -> dict[str, bytes]:
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
    if workflow_contract is not None:
        compatible_contract(workflow_contract)
        compatible_contract(manifest.get("workflow_contract"))
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
    parser.add_argument("--workflow-contract", type=int)
    options = parser.parse_args()
    if options.archive:
        with options.archive.open("rb") as stream:
            data = stream.read(MAX_ARCHIVE_BYTES + 1)
    else:
        data = download(options.url)
    files = verified_files(data, options.sha256, options.manifest_sha256, options.workflow_contract)
    hashes = materialize(files, options.destination)
    print(json.dumps({"runtime": str(options.destination), "files_sha256": hashes}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selection":
        raise SystemExit(selection_main(sys.argv[2:]))
    main()

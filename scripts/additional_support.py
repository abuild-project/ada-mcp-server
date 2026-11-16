# SPDX-License-Identifier: MIT
"""Shared owned-fixture guards, MCP decoding and test-only native tracing."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
FIXTURE = Path(__file__).resolve().parent.parent / "tests/fixtures/additional_project"
GENERATED = {"obj", "bin"}


def file_hashes(root: Path) -> dict[str, str]:
    """Hash regular fixture files, rejecting links and special entries before reads."""
    require_no_symlink_ancestors(root)
    if not stat.S_ISDIR(root.lstat().st_mode):
        raise AssertionError("fixture inspection requires an existing directory")
    hashes: dict[str, str] = {}

    def inspect_directory(directory: Path) -> None:
        # Unlike rglob, scandir propagates an unreadable directory's scan error.
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda entry: entry.name)
        for entry in children:
            path = Path(entry.path)
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                raise AssertionError(f"fixture inspection rejects symlink: {path}")
            if stat.S_ISREG(mode):
                hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
            elif stat.S_ISDIR(mode):
                inspect_directory(path)
            else:
                raise AssertionError(f"fixture inspection rejects a nonregular entry: {path}")

    inspect_directory(root)
    return hashes


def require_no_symlink_ancestors(path: Path) -> None:
    """Reject even dangling links in a requested path or any of its ancestors."""
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise AssertionError(f"owned fixture path rejects symlink: {path}")


def mutate_owned(root: Path, changes: dict[Path, bytes]) -> None:
    """Validate the entire existing-file batch before writing any fresh owned source."""
    file_hashes(root)
    for path in changes:
        if not path.is_relative_to(root) or path.is_relative_to(FIXTURE) or ".." in path.parts:
            raise AssertionError("source mutation must stay in the fresh owned fixture")
        require_no_symlink_ancestors(path)
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise AssertionError("source mutation requires an existing owned regular file")
    for path, text in changes.items():
        path.write_bytes(text)


def input_hashes(root: Path) -> dict[str, str]:
    """Include Ada/GPR/TOML/templates while excluding only owned obj/bin."""
    return {
        name: digest
        for name, digest in file_hashes(root).items()
        if Path(name).parts[0] not in GENERATED
    }


def require_changes(before: JSON, after: JSON, allow_build: bool) -> list[str]:
    """Permit build products only below the explicitly owned output paths."""
    changed = sorted(
        name for name in before.keys() | after.keys() if before.get(name) != after.get(name)
    )
    if any(not allow_build or Path(name).parts[0] not in GENERATED for name in changed):
        raise AssertionError("a tool changed files outside its allowed owned build outputs")
    return changed


def decode_result(result: JSON) -> JSON:
    """Preserve semantic errors as observations instead of accepting positives."""
    payload = result.get("structuredContent")
    if isinstance(payload, dict):
        return payload
    for item in result.get("content", []):
        if item.get("type") == "text":
            try:
                parsed = json.loads(item["text"])
            except ValueError:
                continue
            if isinstance(parsed, dict):
                return parsed
    raise ValueError("MCP tool response has no JSON object payload")


def observed_server(trace: Path) -> None:
    """Trace native requests in a test-only entry point around real dispatch."""
    from ada_mcp.__main__ import main as server_main
    from ada_mcp.als.client import ALSClient, LSPError

    original = ALSClient.send_request
    serial = 0
    with trace.open("x") as stream:

        def write(value: JSON) -> None:
            stream.write(json.dumps(value) + "\n")
            stream.flush()

        async def traced_request(client: ALSClient, method: str, params: JSON | None = None) -> Any:
            nonlocal serial
            serial += 1
            ident = serial
            write({"event": "request", "id": ident, "method": method, "params": params})
            try:
                result = await original(client, method, params)
            except BaseException as error:
                observation: JSON = {
                    "event": "error",
                    "id": ident,
                    "method": method,
                    "type": type(error).__name__,
                    "message": str(error),
                }
                if isinstance(error, LSPError):
                    observation.update(code=error.code, data=error.data)
                write(observation)
                raise
            write({"event": "result", "id": ident, "method": method, "result": result})
            return result

        setattr(ALSClient, "send_request", traced_request)
        server_main()

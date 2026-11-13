#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Test generated tooling against real repositories and two Linux identities."""

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

JSON = dict[str, Any]


def checked(
    command: list[str],
    directory: Path,
    label: str,
    *,
    timeout: float = 900,
    cwd: Path | None = None,
) -> str:
    """Retain an exact command and both streams, including failed attempts."""
    path = directory / (label + ".json")
    if os.path.lexists(path):
        raise FileExistsError("command receipt already exists: " + str(path))
    receipt: JSON = {
        "argv": command,
        "cwd": str((cwd or Path.cwd()).resolve()),
        "timeout": timeout,
        "started_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "rc": None,
        "stdout": "",
        "stderr": "",
        "exception": None,
    }
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        receipt.update(rc=result.returncode, stdout=result.stdout, stderr=result.stderr)
        result.check_returncode()
        return result.stdout
    except BaseException as error:
        receipt["exception"] = {"type": type(error).__name__, "message": str(error)}
        receipt["timed_out"] = isinstance(error, subprocess.TimeoutExpired)
        for field in ["stdout", "stderr"]:
            partial = getattr(error, field, None)
            if partial is not None:
                receipt[field] = (
                    partial.decode("utf-8", errors="replace")
                    if isinstance(partial, bytes)
                    else partial
                )
        raise
    finally:
        receipt["seconds"] = time.monotonic() - started
        with path.open("x") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")


def readable_copy(source: Path, destination: Path) -> dict[str, str]:
    """Copy tracked bytes to new readable paths; never chmod an original path."""
    names = (
        subprocess.check_output(["git", "-C", str(source), "ls-files", "-z"]).decode().split("\0")
    )
    destination.mkdir(mode=0o755)
    destination.chmod(0o755)
    hashes = {}
    for name in filter(None, names):
        original = source / name
        data = original.read_bytes()
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o644)
        hashes[name] = hashlib.sha256(data).hexdigest()
    for directory in destination.rglob("*"):
        if directory.is_dir():
            directory.chmod(0o755)
    for name, digest in hashes.items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError("original source changed during copy")
        if hashlib.sha256((destination / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError("source-copy bytes differ")
    return hashes


def artifact(release: Path, record: JSON) -> Path:
    """Resolve only a hash-verified bare artifact name from release metadata."""
    name = record["filename"]
    if not isinstance(name, str) or Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("unsafe artifact filename")
    path = release / name
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != record["sha256"]:
        raise ValueError("release artifact checksum mismatch")
    return path


def plugin_acquirer(path: Path) -> bytes:
    """Read the packaged inline acquisition path instead of using source helpers."""
    files = {}
    with tarfile.open(fileobj=io.BytesIO(path.read_bytes()), mode="r:*") as archive:
        for member in archive:
            if member.name in files or not member.isfile() or member.size > 4 * 1024 * 1024:
                raise ValueError("invalid lightweight plugin members")
            payload = archive.extractfile(member)
            assert payload is not None
            with payload:
                files[member.name] = payload.read()
    expected = {"plugin.json", "LICENSE", "skills/ada-development/SKILL.md"}
    if set(files) != expected:
        raise ValueError("unexpected lightweight plugin layout")
    match = re.search(
        r"<<'PY'\n(.*?)\nPY\n", files["skills/ada-development/SKILL.md"].decode(), re.DOTALL
    )
    if match is None:
        raise ValueError("packaged acquisition example is missing")
    return (match.group(1) + "\n").encode()


def removed(name: str, directory: Path, docker_host: str | None) -> None:
    """Confirm exact query-container absence without broad cleanup or unknown states."""
    command = ["docker"]
    environment = dict(os.environ)
    if docker_host:
        command.extend(["--host", docker_host])
        for key in [
            "DOCKER_HOST",
            "DOCKER_CONTEXT",
            "DOCKER_TLS",
            "DOCKER_TLS_VERIFY",
            "DOCKER_CERT_PATH",
        ]:
            environment.pop(key, None)
    command.extend(["container", "inspect", "--format", "{{.Id}}", name])
    result = subprocess.run(command, env=environment, text=True, capture_output=True, timeout=30)
    (directory / (name + "-cleanup.json")).write_text(
        json.dumps(
            {
                "argv": command,
                "rc": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            indent=2,
        )
        + "\n"
    )
    missing = {
        prefix + kind + name
        for prefix in ["", "Error: ", "Error response from daemon: "]
        for kind in ["No such container: ", "No such object: "]
    }
    if (
        result.returncode != 1
        or result.stdout.strip() not in {"", "[]"}
        or result.stderr.strip() not in missing
    ):
        raise RuntimeError("exact query-container absence was not established")


def token_position(path: Path, fragment: str, token: str) -> tuple[int, int]:
    """Locate the source token independently of any server result."""
    positions = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if fragment in line:
            positions.append((number, line.index(fragment) + fragment.index(token) + 1))
    if len(positions) != 1:
        raise ValueError("source anchor must be unique")
    return positions[0]


def requests(arca: Path, spawn: Path, anet: Path) -> tuple[list[JSON], list[tuple[Path, str]]]:
    """Select real views and cross-library declarations without production oracles."""
    calls: list[JSON] = []
    definitions = []
    cases = [
        (
            arca / "arca.gpr",
            [],
            {"ARCA_BUILD_MODE": "validation"},
            arca / "src/arca-cpio.adb",
            "Item.CPIO_Write_Trailer;",
            "CPIO_Write_Trailer",
            arca / "src/arca-cpio.ads",
            "CPIO_Create",
        ),
        (
            spawn / "spawn_manager.gpr",
            [anet],
            {"OS": "linux", "TARGET_ARCH": "x86_64", "VERSION": ""},
            spawn / "src/spawn-pool.adb",
            "Anet.Socket_Error",
            "Socket_Error",
            anet / "src/anet.ads",
            "Require_C_String",
        ),
    ]
    for project, search, scenarios, anchor, fragment, token, expected, query in cases:
        line, column = token_position(anchor, fragment, token)
        calls.extend(
            [
                {
                    "tool": "ada_project_info",
                    "arguments": {
                        "gpr_file": str(project),
                        "project_paths": [str(path) for path in search],
                        "scenario_variables": scenarios,
                    },
                },
                {
                    "tool": "ada_workspace_symbols",
                    "arguments": {
                        "file": str(anchor),
                        "query": query,
                        "kind": "all",
                        "limit": 100,
                    },
                },
                {
                    "tool": "ada_goto_definition",
                    "arguments": {"file": str(anchor), "line": line, "column": column},
                },
                {
                    "tool": "ada_hover",
                    "arguments": {"file": str(anchor), "line": line, "column": column},
                },
                {"tool": "ada_diagnostics", "arguments": {"file": str(anchor), "severity": "all"}},
            ]
        )
        definitions.append((expected, token))
    return calls, definitions


def verify_results(payload: JSON, definitions: list[tuple[Path, str]]) -> None:
    """Require complete source-bound positive semantics, not only field presence."""
    results = payload["results"]
    for case, (expected, token) in enumerate(definitions):
        project, symbols, definition, hover, diagnostics = [
            entry["result"] for entry in results[case * 5 : case * 5 + 5]
        ]
        assert project.get("complete") is True, project
        assert project["project_file"] == results[case * 5]["arguments"]["gpr_file"], project
        assert symbols.get("complete") is True and not symbols.get("truncated"), symbols
        assert symbols.get("symbols"), symbols
        query = results[case * 5 + 1]["arguments"]["query"]
        symbol_file = expected if case == 0 else Path(results[case * 5 + 1]["arguments"]["file"])
        assert any(
            query.lower() in symbol["name"].lower()
            and Path(symbol["file"]) == symbol_file
            and query.lower() in symbol_file.read_text().splitlines()[symbol["line"] - 1].lower()
            for symbol in symbols["symbols"]
        ), symbols
        assert definition.get("found") is True and definition["file"] == str(expected), definition
        assert token in expected.read_text().splitlines()[definition["line"] - 1], definition
        assert hover.get("found") is True and token.lower() in json.dumps(hover).lower(), hover
        assert diagnostics.get("complete") is True and diagnostics.get("scope") == "file", (
            diagnostics
        )
        assert diagnostics.get("totalCount") == 0 and not diagnostics.get("diagnostics"), (
            diagnostics
        )


def main() -> None:
    """Acquire generated artifacts and execute the actual public host CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--arca", type=Path, required=True)
    parser.add_argument("--spawn", type=Path, required=True)
    parser.add_argument("--anet", type=Path, required=True)
    parser.add_argument("--docker-host")
    options = parser.parse_args()
    if not options.release.is_absolute() or not options.output.is_absolute():
        raise ValueError("release and evidence paths must be absolute")
    options.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    release = json.loads((options.release / "release-manifest.json").read_text())
    plugin = artifact(options.release, release["plugin"])
    tools = artifact(options.release, release["tooling"])
    image = artifact(options.release, release["image_archive"])
    acquire_script = options.output / "acquire-from-packaged-skill.py"
    acquire_script.write_bytes(plugin_acquirer(plugin))
    runtime = options.output / "runtime"
    checked(
        [
            sys.executable,
            str(acquire_script),
            "--archive",
            str(tools),
            "--sha256",
            release["tooling"]["sha256"],
            "--manifest-sha256",
            release["tooling"]["runtime_manifest_sha256"],
            "--destination",
            str(runtime),
        ],
        options.output,
        "acquire",
    )
    sources = Path(tempfile.mkdtemp(prefix="ada-acceptance-sources-"))
    sources.chmod(0o755)
    hashes = {
        "arca": readable_copy(options.arca, sources / "arca"),
        "spawn": readable_copy(options.spawn, sources / "spawn"),
        "anet": readable_copy(options.anet, sources / "anet"),
    }
    original_modes = {
        str(path): stat.S_IMODE(path.stat().st_mode)
        for path in [options.arca, options.spawn, options.anet]
    }
    (options.output / "source-copies.json").write_text(
        json.dumps({"root": str(sources), "hashes": hashes}, indent=2) + "\n"
    )
    calls, expected = requests(sources / "arca", sources / "spawn", sources / "anet")
    batch = options.output / "requests.json"
    batch.write_text(json.dumps(calls, indent=2) + "\n")
    helper = str(runtime / "scripts/ada_mcp_setup.py")
    for uid, gid in [(1000, 1000), (501, 20)]:
        folder = options.output / f"uid-{uid}"
        folder.mkdir()
        binding = folder / "binding.json"
        setup = [
            sys.executable,
            helper,
            "bootstrap",
            "--binding",
            str(binding),
            "--root",
            str(sources),
            "--uid",
            str(uid),
            "--gid",
            str(gid),
            "--archive",
            str(image),
            "--archive-sha256",
            release["image_archive"]["sha256"],
            "--output",
            str(folder / "bootstrap"),
        ]
        if options.docker_host:
            setup.extend(["--docker-host", options.docker_host])
        checked(setup, folder, "bootstrap-command")
        checked(
            [
                sys.executable,
                helper,
                "doctor",
                "--binding",
                str(binding),
                "--output",
                str(folder / "doctor"),
            ],
            folder,
            "doctor-command",
        )
        catalog_name = f"ada-mcp-catalog-{uid}-" + uuid.uuid4().hex
        catalog = json.loads(
            checked(
                [
                    sys.executable,
                    helper,
                    "query",
                    "--binding",
                    str(binding),
                    "--name",
                    catalog_name,
                    "tools",
                ],
                folder,
                "catalog",
            )
        )
        assert catalog["initialize"]["serverInfo"]["version"] == release["python_version"], catalog
        removed(catalog_name, folder, options.docker_host)
        query_name = f"ada-mcp-query-{uid}-" + uuid.uuid4().hex
        payload = json.loads(
            checked(
                [
                    sys.executable,
                    helper,
                    "query",
                    "--binding",
                    str(binding),
                    "--name",
                    query_name,
                    "--log-dir",
                    str(folder / "mcp"),
                    "batch",
                    str(batch),
                ],
                folder,
                "query",
            )
        )
        verify_results(payload, expected)
        removed(query_name, folder, options.docker_host)
    for source, key in [(options.arca, "arca"), (options.spawn, "spawn"), (options.anet, "anet")]:
        if stat.S_IMODE(source.stat().st_mode) != original_modes[str(source)]:
            raise RuntimeError("original source root permissions changed")
        for name, expected_hash in hashes[key].items():
            if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected_hash:
                raise RuntimeError("original source bytes changed")
    (options.output / "summary.json").write_text(
        json.dumps(
            {
                "passed": True,
                "identities": ["1000:1000", "501:20"],
                "sources": str(sources),
                "scope": "real artifacts and Linux AMD64; no Mac/registry/cold-cache proof",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()

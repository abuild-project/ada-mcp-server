#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Package the already tested source/image without rebuilding either."""

import argparse
import email
import gzip
import hashlib
import io
import json
import re
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Any

from version import ROOT, project_version

JSON = dict[str, Any]
REPOSITORY = "https://github.com/abuild-project/ada-mcp-server"


def sha256_file(path: Path) -> str:
    """Hash large artifacts incrementally."""
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_tar(path: Path, files: dict[str, bytes]) -> None:
    """Create a deterministic archive of regular files only."""
    with path.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as archive:
                for name, data in sorted(files.items()):
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    member.mode = 0o644
                    member.mtime = 0
                    archive.addfile(member, io.BytesIO(data))


def tooling_files(
    root: Path, source_sha: str, image_id: str, image_archive: JSON
) -> dict[str, bytes]:
    """Build immutable runtime metadata from the produced image and exact source."""
    files = {
        "LICENSE": (root / "LICENSE").read_bytes(),
        "SKILL.md": (root / "integrations/full-skill.md").read_bytes(),
        "references/setup.md": (root / "doc/setup.md").read_bytes(),
    }
    for name in [
        "ada-mcp-launch",
        "ada_mcp_setup.py",
        "mac_smoke.py",
        "mcp_client.py",
        "acquire.py",
    ]:
        files["scripts/" + name] = (root / "tooling" / name).read_bytes()
    cases = [
        {
            "gpr_file": "/absolute/project-one/project.gpr",
            "project_paths": [],
            "scenario_variables": {},
            "anchor": "/absolute/project-one/src/example.ads",
            "query": "Example",
            "expected_symbol_file": "/absolute/project-one/src/example.ads",
        },
        {
            "gpr_file": "/absolute/project-two/project.gpr",
            "project_paths": ["/absolute/dependency"],
            "scenario_variables": {},
            "anchor": "/absolute/project-two/src/second.ads",
            "query": "Second",
            "expected_symbol_file": "/absolute/project-two/src/second.ads",
        },
    ]
    files["references/smoke-cases.example.json"] = (json.dumps(cases, indent=2) + "\n").encode()
    version = project_version(root)
    manifest = {
        "version": 1,
        "project_version": version,
        "python_version": version.replace("-rc.", "rc"),
        "source_sha": source_sha,
        "image_id": image_id,
        "platform": "linux/amd64",
        "available_archive": image_archive,
        "server_tools": sorted(
            set(re.findall(r'name="(ada_[a-z_]+)"', (root / "src/ada_mcp/server.py").read_text()))
        ),
        "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    files["scripts/runtime-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode()
    return files


def lightweight_plugin(root: Path, version: str, tooling: JSON) -> dict[str, bytes]:
    """Embed the trusted acquisition code in Markdown, avoiding remote script reads."""
    instructions = f'''---
name: ada-development
description: >
  Use for Ada/GPR development and pinned shared Ada MCP setup across repositories.
  Acquire the versioned archive, read project rules and select real GPR views.
  Compiler CI remains separate.
---

# Ada development {version}

This lightweight skill acquires the complete tested tooling through ordinary
HTTPS. It needs no Plugin Creator owner access and no Python/JSON resource
reads through the skill provider. Public availability begins only after the
versioned release exists. Never substitute a mutable latest image or unchecked
download. Preserve the project's AGENTS/workflow/counters.

Choose an explicit new private runtime path, then run this stdlib-only code.
The archive and runtime manifest are pinned to the hashes generated with this
skill. No downloaded helper runs before complete verification.

```sh
python3 - --url "{tooling["download_url"]}" \\
  --sha256 {tooling["sha256"]} \\
  --manifest-sha256 {tooling["runtime_manifest_sha256"]} \\
  --destination /absolute/new-ada-runtime <<'PY'
{(root / "tooling/acquire.py").read_text()}
PY
```

Read the verified runtime's SKILL.md and references/setup.md. Bootstrap with
explicit roots, binding and image-cache paths, then run Doctor and actual
query batches. The full runtime manifest pins the image archive as well.
Native configuration and current managed Cloud tool registration are separate;
actual Mac/other-client/registry/fresh-Cloud acceptance remains in development.
Never replace the repository's compiler/coverage/test/documentation chain.
'''
    plugin = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "ada-development",
        "version": version,
        "description": "Pinned standalone Ada MCP acquisition and development workflow",
        "license": "MIT",
    }
    return {
        "plugin.json": (json.dumps(plugin, indent=2) + "\n").encode(),
        "skills/ada-development/SKILL.md": instructions.encode(),
        "LICENSE": (root / "LICENSE").read_bytes(),
    }


def package(root: Path, output: Path, source_sha: str, image_id: str, archive: Path) -> JSON:
    """Create tooling/plugin manifests around an existing exported image archive."""
    version = project_version(root)
    base_url = f"{REPOSITORY}/releases/download/v{version}/"
    image_record = {
        "filename": archive.name,
        "sha256": sha256_file(archive),
        "bytes": archive.stat().st_size,
        "download_url": base_url + archive.name,
    }
    files = tooling_files(root, source_sha, image_id, image_record)
    tooling_path = output / f"ada-mcp-tooling-{version}.tar.gz"
    write_tar(tooling_path, files)
    tooling = {
        "filename": tooling_path.name,
        "sha256": sha256_file(tooling_path),
        "bytes": tooling_path.stat().st_size,
        "download_url": base_url + tooling_path.name,
        "runtime_manifest_sha256": hashlib.sha256(
            files["scripts/runtime-manifest.json"]
        ).hexdigest(),
    }
    plugin_path = output / f"ada-development-{version}.tar.gz"
    write_tar(plugin_path, lightweight_plugin(root, version, tooling))
    return {
        "version": version,
        "python_version": version.replace("-rc.", "rc"),
        "source_sha": source_sha,
        "image_id": image_id,
        "platform": "linux/amd64",
        "registry_digest": None,
        "registry_public_access": "not published or verified",
        "image_archive": image_record,
        "tooling": tooling,
        "plugin": {"filename": plugin_path.name, "sha256": sha256_file(plugin_path)},
    }


def validate_python_distributions(folder: Path, version: str) -> list[Path]:
    """Reject stale/misnamed distributions instead of relabeling their version."""
    python_version = version.replace("-rc.", "rc")
    expected = {
        f"ada_mcp_server-{python_version}-py3-none-any.whl",
        f"ada_mcp_server-{python_version}.tar.gz",
    }
    distributions = list(folder.glob("*"))
    if {path.name for path in distributions} != expected or not all(
        path.is_file() for path in distributions
    ):
        raise ValueError("provide exactly the two checked Python distributions for this version")
    for path in distributions:
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as wheel:
                names = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
                if len(names) != 1:
                    raise ValueError("wheel must have one metadata record")
                metadata = wheel.read(names[0])
        else:
            with tarfile.open(path) as archive:
                members = [
                    member
                    for member in archive
                    if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
                ]
                if len(members) != 1 or not members[0].isfile():
                    raise ValueError("sdist must have one regular package metadata record")
                stream = archive.extractfile(members[0])
                assert stream is not None
                with stream:
                    metadata = stream.read()
        message = email.message_from_bytes(metadata)
        if message["Name"] != "ada-mcp-server" or message["Version"] != python_version:
            raise ValueError("Python distribution metadata differs from the canonical version")
    return distributions


def main() -> None:
    """Check the source/image match, export once and package the tested bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python-dist", type=Path, default=ROOT / "build/check/python-dist")
    parser.add_argument("--docker-host")
    options = parser.parse_args()
    if not options.output.is_absolute() or options.output.exists():
        raise ValueError("artifact output must be a new absolute directory")
    source_sha = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True)
    if dirty:
        raise ValueError("commit all candidate changes before creating release artifacts")
    docker = ["docker"]
    if options.docker_host:
        docker.extend(["--host", options.docker_host])
    state = json.loads(
        subprocess.check_output(docker + ["image", "inspect", options.image], text=True)
    )[0]
    if state["Os"] != "linux" or state["Architecture"] != "amd64":
        raise ValueError("expected a Linux/AMD64 image")
    if state["Config"]["Labels"].get("org.opencontainers.image.revision") != source_sha:
        raise ValueError("image source revision differs from the committed candidate")
    version = project_version()
    if state["Config"]["Labels"].get("org.opencontainers.image.version") != version:
        raise ValueError("image version differs from the source")
    distributions = validate_python_distributions(options.python_dist, version)
    options.output.mkdir(parents=True)
    image_archive = options.output / f"ada-mcp-image-{version}-linux-amd64.tar.gz"
    process = subprocess.Popen(docker + ["image", "save", state["Id"]], stdout=subprocess.PIPE)
    assert process.stdout is not None
    with image_archive.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as stream:
            shutil.copyfileobj(process.stdout, stream)
    if process.wait() != 0:
        raise RuntimeError("Docker image export failed")
    manifest = package(ROOT, options.output, source_sha, state["Id"], image_archive)
    for distribution in distributions:
        shutil.copy2(distribution, options.output / distribution.name)
    source_archive = options.output / f"ada-mcp-source-{version}.tar.gz"
    with source_archive.open("xb") as stream:
        subprocess.run(
            ["git", "-C", str(ROOT), "archive", "--format=tar.gz", source_sha],
            stdout=stream,
            check=True,
        )
    components = subprocess.check_output(
        docker
        + [
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--entrypoint",
            "cat",
            state["Id"],
            "/usr/share/licenses/ada-mcp-server/components.json",
        ]
    )
    (options.output / "components.json").write_bytes(components)
    manifest["artifacts_sha256"] = {
        path.name: sha256_file(path) for path in sorted(options.output.iterdir()) if path.is_file()
    }
    (options.output / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    with (options.output / "SHA256SUMS").open("x") as stream:
        for path in sorted(options.output.iterdir()):
            if path.is_file() and path.name != "SHA256SUMS":
                stream.write(sha256_file(path) + "  " + path.name + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

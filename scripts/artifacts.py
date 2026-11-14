#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Package the already tested source/image without rebuilding either."""

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any

from distribution_receipt import (
    committed_archive_sha256,
    distribution_files,
    validate_checked_target,
    validate_receipt,
)
from version import ROOT, project_version

sys.path.insert(0, str(ROOT / "tooling"))
from ada_mcp_setup import inspect_image
from image_identity import archive_identity

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
    root: Path, source_sha: str, identity: JSON, image_archive: JSON
) -> dict[str, bytes]:
    """Build immutable runtime metadata from the produced image and exact source."""
    files = {
        "LICENSE": (root / "LICENSE").read_bytes(),
        "SKILL.md": (root / "integrations/full-skill.md").read_bytes(),
        "references/setup.md": (root / "doc/setup.md").read_bytes(),
        "references/support.md": (root / "doc/support.md").read_bytes(),
        "references/updating.md": (root / "doc/updating.md").read_bytes(),
    }
    for name in [
        "ada-mcp-launch",
        "ada_mcp_setup.py",
        "mac_smoke.py",
        "mcp_client.py",
        "acquire.py",
        "image_identity.py",
        "release_updates.py",
    ]:
        files["scripts/" + name] = (root / "tooling" / name).read_bytes()
    for name in ["__init__.py", "_version.py", "update_notice.py"]:
        files["scripts/ada_mcp/" + name] = (root / "src/ada_mcp" / name).read_bytes()
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
        "image_id": identity["image_id"],
        "image_identity": identity,
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
    full_skill = (root / "integrations/full-skill.md").read_text()
    update_workflow = full_skill[full_skill.index("## Release checks and user-approved updates") :]
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
These embedded pins are for this version's first installation. For an existing
installation's checks or a newer target, follow the release-check workflow
below; never reuse these embedded hashes as the target update's pins.

```sh
python3 -I - --url "{tooling["download_url"]}" \\
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

{update_workflow}
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
    evidence: JSON = {}
    try:
        with archive.open("rb") as stream:
            identity = archive_identity(stream, expected_target=image_id, evidence=evidence)
        image = evidence["image_validation"]
        if image["source_revision"] != source_sha or image["project_version"] != version:
            raise ValueError("archived image source/version differs from checked candidate")
    finally:
        (output / "image-identity-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    base_url = f"{REPOSITORY}/releases/download/v{version}/"
    image_record = {
        "filename": archive.name,
        "sha256": sha256_file(archive),
        "bytes": archive.stat().st_size,
        "download_url": base_url + archive.name,
    }
    files = tooling_files(root, source_sha, identity, image_record)
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
        "image_id": identity["image_id"],
        "image_identity": identity,
        "platform": "linux/amd64",
        "registry_digest": None,
        "registry_public_access": "not published or verified",
        "image_archive": image_record,
        "tooling": tooling,
        "plugin": {"filename": plugin_path.name, "sha256": sha256_file(plugin_path)},
    }


def validate_python_distributions(
    folder: Path, version: str, source_sha: str, archive_sha256: str
) -> tuple[list[Path], JSON]:
    """Require the completed check's source/hash receipt, even for the same version."""
    receipt = validate_receipt(folder, version, source_sha, archive_sha256)
    return distribution_files(folder, version), receipt


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
    version = project_version()
    distributions, provenance = validate_python_distributions(
        options.python_dist, version, source_sha, committed_archive_sha256(ROOT, source_sha)
    )
    docker = ["docker"]
    if options.docker_host:
        docker.extend(["--host", options.docker_host])
    options.output.mkdir(parents=True)
    evidence: JSON = {}
    try:
        state = inspect_image(docker, dict(os.environ), options.image, evidence, 60)
        if state is None:
            raise ValueError("checked image is unavailable")
    finally:
        (options.output / "image-inspect-evidence.json").write_text(
            json.dumps(evidence, indent=2) + "\n"
        )
    if state["Os"] != "linux" or state["Architecture"] != "amd64":
        raise ValueError("expected a Linux/AMD64 image")
    if state["Labels"].get("org.opencontainers.image.revision") != source_sha:
        raise ValueError("image source revision differs from the committed candidate")
    if state["Labels"].get("org.opencontainers.image.version") != version:
        raise ValueError("image version differs from the source")
    validate_checked_target(provenance, state["Id"], state["Os"] + "/" + state["Architecture"])
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
        copied = options.output / distribution.name
        shutil.copy2(distribution, copied)
        if sha256_file(copied) != provenance["distributions_sha256"][distribution.name]:
            raise ValueError("Python distribution changed during packaging: " + distribution.name)
    (options.output / "python-distributions-provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    manifest["python_distributions"] = provenance
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

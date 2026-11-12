#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and explicitly promote already tested artifacts, without rebuilding."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from distribution_receipt import validate_checked_target

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))

JSON = dict[str, Any]
REPOSITORY = "abuild-project/ada-mcp-server"


def digest(path: Path) -> str:
    """Hash exact artifact bytes incrementally."""
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def validate_release(release: Path, source_sha: str) -> JSON:
    """Require the approved source plus every recorded immutable artifact hash."""
    manifest: JSON = json.loads((release / "release-manifest.json").read_text())
    if not re.fullmatch("[0-9a-f]{40}", source_sha) or manifest["source_sha"] != source_sha:
        raise ValueError("release source differs from the explicitly approved revision")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-rc\.\d+)?", manifest["version"]):
        raise ValueError("invalid coordinated release version")
    if not re.fullmatch("sha256:[0-9a-f]{64}", manifest["image_id"]):
        raise ValueError("invalid immutable image ID")
    from image_identity import validate_identity

    validate_identity(manifest["image_identity"], manifest["image_id"])
    if manifest["platform"] != "linux/amd64":
        raise ValueError("unsupported release platform")
    validate_checked_target(
        manifest["python_distributions"],
        manifest["image_identity"]["target"]["digest"],
        manifest["platform"],
    )
    for name, expected in manifest["artifacts_sha256"].items():
        if Path(name).name != name or name in {"", ".", ".."}:
            raise ValueError("unsafe artifact name")
        if digest(release / name) != expected:
            raise ValueError("artifact SHA256 mismatch: " + name)
    for key in ["image_archive", "tooling", "plugin"]:
        record = manifest[key]
        if manifest["artifacts_sha256"].get(record["filename"]) != record["sha256"]:
            raise ValueError("artifact identity records disagree")
    return manifest


def plan(manifest: JSON) -> JSON:
    """Describe the exact future promotion targets, without any external write."""
    return {
        "source_sha": manifest["source_sha"],
        "image_id": manifest["image_id"],
        "tag": "v" + manifest["version"],
        "registry_reference": "ghcr.io/abuild-project/ada-mcp-server:v" + manifest["version"],
        "repository": REPOSITORY,
        "rebuild": False,
        "requirements": [
            "explicit approval",
            "matching existing Git tag",
            "successful trusted CI run",
            "public GHCR package visibility",
            "anonymous digest/config identity proof",
        ],
    }


def execute(release: Path, manifest: JSON) -> JSON:
    """Publish only after explicit approval and verify public access before release."""
    if os.environ.get("ADA_MCP_PUBLISH_APPROVED_SOURCE") != manifest["source_sha"]:
        raise PermissionError("publication needs explicit source-bound maintainer approval")
    from ada_mcp_setup import (
        inspect_image,
        loaded_candidates,
        resolve_candidates,
        validate_docker_archive,
    )

    archive_evidence: JSON = {}
    with (release / manifest["image_archive"]["filename"]).open("rb") as stream:
        validate_docker_archive(stream, manifest["image_id"], archive_evidence)
    image = archive_evidence["image_validation"]
    if (
        image["source_revision"] != manifest["source_sha"]
        or image["project_version"] != manifest["version"]
    ):
        raise ValueError("archived image source/version does not match the approved release")
    proposal = plan(manifest)
    ref = json.loads(
        subprocess.check_output(
            ["gh", "api", f"repos/{REPOSITORY}/git/ref/tags/{proposal['tag']}"],
            text=True,
        )
    )
    target = ref["object"]
    if target["type"] == "tag":
        target = json.loads(
            subprocess.check_output(
                ["gh", "api", f"repos/{REPOSITORY}/git/tags/{target['sha']}"],
                text=True,
            )
        )["object"]
    if target["type"] != "commit" or target["sha"] != manifest["source_sha"]:
        raise ValueError("existing release tag does not identify the approved source")
    with (release / manifest["image_archive"]["filename"]).open("rb") as stream:
        validate_docker_archive(stream, manifest["image_id"], archive_evidence)
        stream.seek(0)
        loaded = subprocess.run(
            ["docker", "image", "load"],
            stdin=stream,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,
        )
    identity_report: JSON = {}
    identity = resolve_candidates(
        ["docker"],
        dict(os.environ),
        loaded_candidates(loaded.stdout, manifest["image_identity"]),
        manifest["image_id"],
        identity_report,
        300,
    )
    subprocess.run(
        ["docker", "tag", identity["target"]["digest"], proposal["registry_reference"]], check=True
    )
    pushed = subprocess.run(
        ["docker", "push", proposal["registry_reference"]],
        capture_output=True,
        text=True,
        check=True,
        timeout=300,
    )
    digests = set(re.findall(r"digest: (sha256:[0-9a-f]{64})", pushed.stdout))
    if len(digests) != 1:
        raise ValueError("Docker push did not report one immutable registry digest")
    registry_digest = digests.pop()
    pinned = proposal["registry_reference"].split(":v", 1)[0] + "@" + registry_digest
    # A new empty Docker client config does not read the publishing account's
    # stored credentials. Visibility is an explicit maintainer/package setting.
    with tempfile.TemporaryDirectory(prefix="ada-mcp-anonymous-") as empty_config:
        docker = ["docker", "--config", empty_config]
        subprocess.run(
            docker + ["image", "pull", "--platform", "linux/amd64", pinned],
            check=True,
            timeout=300,
        )
        state = inspect_image(docker, dict(os.environ), pinned, identity_report, 60)
        if state is None:
            raise ValueError("anonymous pinned registry image is unavailable")
        resolve_candidates(
            docker, dict(os.environ), [state["Id"]], manifest["image_id"], identity_report, 300
        )
    promoted = dict(manifest)
    promoted.update(
        registry_digest=registry_digest,
        registry_public_access="anonymous digest pull/config verified",
    )
    stage = Path(tempfile.mkdtemp(prefix="ada-mcp-promoted-", dir=release.parent))
    for name in manifest["artifacts_sha256"]:
        shutil.copy2(release / name, stage / name)
    shutil.copy2(release / "release-manifest.json", stage / "build-manifest.json")
    (stage / "release-manifest.json").write_text(json.dumps(promoted, indent=2) + "\n")
    with (stage / "SHA256SUMS").open("x") as sums:
        for path in sorted(stage.iterdir()):
            if path.is_file() and path.name != "SHA256SUMS":
                sums.write(digest(path) + "  " + path.name + "\n")
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            proposal["tag"],
            "--repo",
            REPOSITORY,
            "--verify-tag",
            "--prerelease",
            "--title",
            proposal["tag"],
            "--notes",
            "Tested standalone Ada MCP pilot candidate; see support documentation.",
            *[str(path) for path in sorted(stage.iterdir()) if path.is_file()],
        ],
        check=True,
    )
    return promoted


def main() -> None:
    """Default to read-only plan mode; execution is a separate explicit action."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--execute", action="store_true")
    options = parser.parse_args()
    manifest = validate_release(options.release, options.source_sha)
    result = execute(options.release, manifest) if options.execute else plan(manifest)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

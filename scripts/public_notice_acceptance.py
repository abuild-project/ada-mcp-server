#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Manually verify public RC2 notification of published RC3 on an ephemeral Docker host."""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import traceback
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

# Isolated Python excludes the script directory; add only reviewed helper roots.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
import acquire
from host_acceptance import checked, removed
from image_identity import validate_identity
from release_updates import header_deadline
from version import ROOT, project_version

JSON = dict[str, Any]
REPOSITORY = "abuild-project/ada-mcp-server"
API = "https://api.github.com/repos/" + REPOSITORY
PUBLIC = "https://github.com/" + REPOSITORY
INSTALLED = "0.2.0-rc.2"
TARGET = "0.2.0-rc.3"
INSTALLED_SOURCE = "5448ee1eeedb76723d2c726e4d19535743f2b437"
ARCA_SOURCE = "20564468d00024e6f949e92c1da79850abf59086"
SCENARIOS = {"ARCA_BUILD_MODE": "validation"}
LIMIT = 1024 * 1024


def require(condition: object, message: str) -> None:
    """Reject partial or mismatched public evidence rather than infer acceptance."""
    if not condition:
        raise ValueError(message)


class NoRedirects(urllib.request.HTTPRedirectHandler):
    """Keep public API reads on their exact fixed HTTPS endpoints."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def api_json(path: str, output: Path, label: str) -> JSON:
    """Retain bounded anonymous API responses, including actual provider wait headers."""
    url = API + path
    receipt: JSON = {"url": url, "limit": LIMIT, "socket_timeout": 20}
    try:
        request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.build_opener(NoRedirects()).open(request, timeout=20) as response:
            require(response.geturl() == url, "API response changed endpoint")
            deadline = header_deadline(response.headers)
            receipt.update(
                status=response.status,
                provider_headers={
                    key: response.headers.get(key)
                    for key in ["Retry-After", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
                },
            )
            if deadline is not None:
                receipt["blocked_until"] = deadline
                raise ValueError(f"GitHub provider wait until {deadline}; no further requests")
            data = response.read(LIMIT + 1)
            receipt.update(status=response.status, bytes=len(data))
            require(len(data) <= LIMIT, "API response exceeds its byte bound")
            (output / (label + ".body.json")).write_bytes(data)
            result: JSON = json.loads(data)
            require(isinstance(result, dict), "expected a GitHub API object")
            return result
    except urllib.error.HTTPError as error:
        receipt.update(
            status=error.code,
            provider_headers={
                key: error.headers.get(key)
                for key in ["Retry-After", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
            },
        )
        raise
    finally:
        (output / (label + ".request.json")).write_text(json.dumps(receipt, indent=2) + "\n")


def asset(release: JSON, version: str, name: str, limit: int) -> JSON:
    """Require one canonical public asset with an authoritative immutable digest."""
    require(
        release.get("tag_name") == "v" + version
        and release.get("draft") is False
        and release.get("prerelease") is True,
        "wrong or unpublished prerelease",
    )
    require(
        release.get("html_url") == PUBLIC + "/releases/tag/v" + version,
        "release repository/tag URL mismatch",
    )
    assets = release.get("assets")
    require(isinstance(assets, list) and len(assets) <= 100, "invalid release asset list")
    assert isinstance(assets, list)
    matches = [item for item in assets if isinstance(item, dict) and item.get("name") == name]
    require(len(matches) == 1, "missing or duplicate release asset: " + name)
    item: JSON = matches[0]
    require(
        item.get("browser_download_url") == PUBLIC + "/releases/download/v" + version + "/" + name,
        "asset URL differs from the exact public tag",
    )
    require(
        type(item.get("size")) is int
        and 0 < item["size"] <= limit
        and isinstance(item.get("digest"), str)
        and re.fullmatch("sha256:[0-9a-f]{64}", item["digest"]),
        "missing authoritative asset size/digest",
    )
    return item


def verified_release(
    release: JSON, version: str, source: str, tag_source: str, data: bytes
) -> JSON:
    """Authenticate final manifest bytes before using their target/source/artifact fields."""
    pin = asset(release, version, "release-manifest.json", LIMIT)
    require(
        len(data) == pin["size"] and "sha256:" + hashlib.sha256(data).hexdigest() == pin["digest"],
        "release manifest asset digest/size mismatch",
    )
    manifest: JSON = json.loads(data)
    require(isinstance(manifest, dict), "release manifest must be an object")
    require(
        manifest.get("version") == version
        and manifest.get("source_sha") == source
        and tag_source == source
        and re.fullmatch("[0-9a-f]{40}", source),
        "release version/tag/source mismatch",
    )
    require(
        manifest.get("python_version") == version.replace("-rc.", "rc")
        and manifest.get("platform") == "linux/amd64",
        "release Python/platform mismatch",
    )
    require(
        re.fullmatch("[0-9a-f]{64}", manifest["tooling"]["runtime_manifest_sha256"]),
        "invalid runtime manifest pin",
    )
    names = {
        "tooling": f"ada-mcp-tooling-{version}.tar.gz",
        "plugin": f"ada-development-{version}.tar.gz",
        "image_archive": f"ada-mcp-image-{version}-linux-amd64.tar.gz",
    }
    for kind in names:
        record = manifest[kind]
        require(record["filename"] == names[kind], "noncanonical coordinated asset name")
        maximum = acquire.MAX_ARCHIVE_BYTES if kind != "image_archive" else 4 * 1024**3
        item = asset(release, version, record["filename"], maximum)
        require(
            item["digest"] == "sha256:" + record["sha256"]
            and manifest["artifacts_sha256"].get(record["filename"]) == record["sha256"],
            "release artifact digest records disagree",
        )
        if kind != "plugin":
            require(
                record["bytes"] == item["size"]
                and record["download_url"] == item["browser_download_url"],
                "release artifact size/URL records disagree",
            )
    require(
        isinstance(manifest.get("registry_digest"), str)
        and re.fullmatch("sha256:[0-9a-f]{64}", manifest["registry_digest"]),
        "published immutable registry digest missing",
    )
    validate_identity(manifest["image_identity"], manifest["image_id"])
    if version == TARGET:
        require(
            type(manifest["tooling"].get("workflow_contract")) is int
            and manifest["tooling"]["workflow_contract"] == 1,
            "RC3 workflow contract missing",
        )
    return manifest


def public_release(version: str, expected_source: str, output: Path) -> JSON:
    """Read the actual published tag and authenticated final release manifest."""
    label = version.replace(".", "-")
    release = api_json("/releases/tags/v" + version, output, label + "-release")
    pin = asset(release, version, "release-manifest.json", LIMIT)
    target = api_json("/git/ref/tags/v" + version, output, label + "-ref")["object"]
    for depth in range(5):
        require(re.fullmatch("[0-9a-f]{40}", target["sha"]), "invalid Git tag object SHA")
        if target["type"] == "commit":
            break
        require(target["type"] == "tag", "release tag does not resolve to a commit")
        target = api_json("/git/tags/" + target["sha"], output, f"{label}-tag-{depth}")["object"]
    require(target["type"] == "commit", "release tag indirection exceeds the bound")
    data = acquire.download(pin["browser_download_url"], timeout=20)
    manifest = verified_release(release, version, expected_source, target["sha"], data)
    (output / (label + "-manifest.json")).write_bytes(data)
    return manifest


def project_arguments(project: Path) -> JSON:
    """Keep the actual public Arca GPR and scenario view explicit."""
    return {
        "gpr_file": str(project / "arca.gpr"),
        "project_paths": [],
        "scenario_variables": SCENARIOS,
    }


def verify_query(payload: JSON, project: Path, *, notice: bool) -> None:
    """Require actual RC2 transport, exact complete GPR view and both notification paths."""
    initialized = payload["initialize"]
    require(initialized["serverInfo"]["version"] == "0.2.0rc2", "actual server is not RC2")
    entries = payload["results"]
    require(
        len(entries) == 1
        and entries[0]["tool"] == "ada_project_info"
        and entries[0]["arguments"] == project_arguments(project),
        "query GPR/scenarios mismatch",
    )
    info = entries[0]["result"]
    require(
        info.get("complete") is True
        and info.get("project_file") == str(project / "arca.gpr")
        and str(project / "src") in info.get("source_dirs", []),
        "incomplete/wrong project view",
    )
    instructions = initialized.get("instructions")
    require(
        instructions is None or isinstance(instructions, str), "invalid initialization instructions"
    )
    instructions = instructions or ""
    if notice:
        advisory = info.get("update_notice", {})
        require(
            advisory.get("current_version") == INSTALLED
            and advisory.get("available_version") == TARGET
            and advisory.get("release_url") == PUBLIC + "/releases/tag/v" + TARGET
            and advisory.get("freshness") == "fresh",
            "project update notice missing/mismatched",
        )
        require(
            INSTALLED in instructions
            and TARGET in instructions
            and advisory["release_url"] in instructions,
            "initialization notice missing",
        )
    else:
        require(
            "update_notice" not in info and TARGET not in instructions, "off query leaked a notice"
        )


def verify_manual(payload: JSON) -> None:
    """Require a performed fresh check of the same installed and published target pair."""
    advisory = payload.get("update_notice", {})
    require(
        payload.get("check_performed") is True
        and payload.get("status") == "available"
        and payload.get("current_version") == INSTALLED
        and advisory.get("current_version") == INSTALLED
        and advisory.get("available_version") == TARGET
        and advisory.get("freshness") == "fresh"
        and advisory.get("release_url") == PUBLIC + "/releases/tag/v" + TARGET,
        "manual check did not freshly observe RC3; inspect provider/offline evidence",
    )


def retain_cache(cache: Path, output: Path, label: str) -> None:
    """Keep small actual checker state even when notification assertions fail."""
    if cache.exists():
        states = sorted(cache.glob("*.json"))
        require(len(states) <= 10, "unexpected number of notice cache files")
        for state in states:
            (output / (label + "-" + state.name)).write_bytes(
                acquire.bounded_file(state, 64 * 1024, private=True)
            )


def query(
    helper: Path, binding: Path, project: Path, cache: Path, output: Path, channel: str
) -> JSON:
    """Retain protocol and exact named-container EOF cleanup even when a query fails."""
    name = "ada-mcp-public-notice-" + uuid.uuid4().hex
    request = output / (channel + "-requests.json")
    request.write_text(
        json.dumps([{"tool": "ada_project_info", "arguments": project_arguments(project)}])
    )
    try:
        payload: JSON = json.loads(
            checked(
                [
                    sys.executable,
                    "-I",
                    str(helper),
                    "query",
                    "--binding",
                    str(binding),
                    "--update-channel",
                    channel,
                    "--update-cache",
                    str(cache),
                    "--name",
                    name,
                    "--log-dir",
                    str(output / (channel + "-protocol")),
                    "batch",
                    str(request),
                ],
                output,
                channel + "-query",
            )
        )
        return payload
    finally:
        removed(name, output, None)


def main() -> int:
    """Run only this fixed post-publication consumer case, never install a target update."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-source", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    output, workspace = options.output, options.workspace
    require(
        output.is_absolute()
        and workspace.is_absolute()
        and output != workspace
        and not workspace.is_relative_to(output)
        and not output.is_relative_to(workspace),
        "new workspace/evidence paths must be absolute and separate",
    )
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    summary: JSON = {
        "passed": False,
        "installed": INSTALLED,
        "target": TARGET,
        "scope": (
            "public protocol/query-client notice; no target install, private plugin, "
            "native, fresh Cloud or Mac acceptance"
        ),
    }
    try:
        require(
            re.fullmatch("[0-9a-f]{40}", options.expected_source) and project_version() == TARGET,
            "wrong approved RC3 source/version",
        )
        source = checked(["git", "rev-parse", "HEAD"], output, "probe-source", cwd=ROOT).strip()
        require(
            source == options.expected_source, "probe checkout differs from approved RC3 source"
        )
        workspace.mkdir(mode=0o700, parents=True, exist_ok=False)
        docker_config = workspace / "anonymous-docker"
        docker_config.mkdir(mode=0o700)
        os.environ.update(
            DOCKER_CONFIG=str(docker_config),
            ADA_MCP_UPDATE_CHANNEL="off",
            ADA_MCP_UPDATE_CACHE=str(workspace / "unused-cache"),
            GIT_TERMINAL_PROMPT="0",
        )
        installed = public_release(INSTALLED, INSTALLED_SOURCE, output)
        public_release(TARGET, options.expected_source, output)  # data only; never execute RC3
        tools = acquire.download(installed["tooling"]["download_url"])
        require(len(tools) == installed["tooling"]["bytes"], "public RC2 tooling size mismatch")
        files = acquire.verified_files(
            tools, installed["tooling"]["sha256"], installed["tooling"]["runtime_manifest_sha256"]
        )
        runtime_manifest = json.loads(files["scripts/runtime-manifest.json"])
        require(
            all(
                runtime_manifest[key] == installed[key]
                for key in [
                    "source_sha",
                    "image_id",
                    "image_identity",
                    "python_version",
                    "platform",
                ]
            )
            and runtime_manifest["project_version"] == INSTALLED
            and runtime_manifest["available_archive"] == installed["image_archive"],
            "RC2 tooling runtime/image/source lock mismatch",
        )
        (output / "rc2-runtime-manifest.json").write_bytes(files["scripts/runtime-manifest.json"])
        runtime = workspace / "rc2-runtime"
        acquire.materialize(files, runtime)
        project = workspace / "arca"
        checked(["git", "init", str(project)], output, "arca-init")
        checked(
            [
                "git",
                "-C",
                str(project),
                "fetch",
                "--depth=1",
                "https://github.com/abuild-project/arca-Ada.git",
                ARCA_SOURCE,
            ],
            output,
            "arca-fetch",
        )
        checked(
            ["git", "-C", str(project), "checkout", "--detach", ARCA_SOURCE],
            output,
            "arca-checkout",
        )
        require(
            checked(["git", "-C", str(project), "rev-parse", "HEAD"], output, "arca-source").strip()
            == ARCA_SOURCE,
            "wrong actual Arca source",
        )
        helper, binding = runtime / "scripts/ada_mcp_setup.py", workspace / "binding.json"
        checked(
            [
                sys.executable,
                "-I",
                str(helper),
                "bootstrap",
                "--binding",
                str(binding),
                "--root",
                str(project),
                "--registry",
                "ghcr.io/" + REPOSITORY + "@" + installed["registry_digest"],
                "--output",
                str(output / "bootstrap"),
            ],
            output,
            "bootstrap-command",
        )
        checked(
            [
                sys.executable,
                "-I",
                str(helper),
                "doctor",
                "--binding",
                str(binding),
                "--output",
                str(output / "doctor"),
            ],
            output,
            "doctor-command",
        )
        shutil.copy2(binding, output / "binding.json")
        cache = workspace / "notice-cache"
        require(not cache.exists(), "automatic notice cache must be new")
        try:
            verify_query(
                query(helper, binding, project, cache, output, "auto"), project, notice=True
            )
        finally:
            retain_cache(cache, output, "automatic")
        before = cache / "prerelease.json"
        require(
            json.loads(before.read_text())["next_check_at"] > time.time(), "daily cache not active"
        )
        try:
            fresh = json.loads(
                checked(
                    [
                        sys.executable,
                        "-I",
                        str(helper),
                        "updates",
                        "check",
                        "--channel",
                        "auto",
                        "--cache",
                        str(cache),
                    ],
                    output,
                    "manual-check",
                )
            )
        finally:
            retain_cache(cache, output, "manual")
        verify_manual(fresh)
        off_cache = workspace / "off-cache"
        try:
            verify_query(
                query(helper, binding, project, off_cache, output, "off"), project, notice=False
            )
        finally:
            retain_cache(off_cache, output, "off")
        require(not off_cache.exists(), "off query created an update cache")
        summary.update(
            passed=True, expected_source=options.expected_source, arca_source=ARCA_SOURCE
        )
    except Exception as error:
        summary.update(error=type(error).__name__ + ": " + str(error))
        (output / "failure.txt").write_text(traceback.format_exc())
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

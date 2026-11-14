"""Reject fabricated provenance or protocol success without running public acceptance."""

import copy
import hashlib
import json
import subprocess
import sys
import time
from email.message import Message

import public_notice_acceptance as probe
import pytest
from image_fixtures import classic_identity


def released(version=probe.INSTALLED):
    source = probe.INSTALLED_SOURCE
    image_id = "sha256:" + "b" * 64
    records = {}
    assets = []
    for kind, name in [
        ("tooling", f"ada-mcp-tooling-{version}.tar.gz"),
        ("plugin", f"ada-development-{version}.tar.gz"),
        ("image_archive", f"ada-mcp-image-{version}-linux-amd64.tar.gz"),
    ]:
        records[kind] = {"filename": name, "sha256": "a" * 64}
        url = probe.PUBLIC + "/releases/download/v" + version + "/" + name
        if kind != "plugin":
            records[kind].update(bytes=12, download_url=url)
        assets.append(
            {"name": name, "size": 12, "digest": "sha256:" + "a" * 64, "browser_download_url": url}
        )
    records["tooling"].update(runtime_manifest_sha256="c" * 64)
    if version == probe.TARGET:
        records["tooling"]["workflow_contract"] = 1
    manifest = dict(
        version=version,
        source_sha=source,
        python_version=version.replace("-rc.", "rc"),
        platform="linux/amd64",
        image_id=image_id,
        image_identity=classic_identity(image_id),
        registry_digest="sha256:" + "d" * 64,
        artifacts_sha256={record["filename"]: record["sha256"] for record in records.values()},
        **records,
    )
    release = {
        "tag_name": "v" + version,
        "draft": False,
        "prerelease": True,
        "html_url": probe.PUBLIC + "/releases/tag/v" + version,
        "assets": assets,
    }
    return release, manifest


def pin_manifest(release, manifest):
    data = json.dumps(manifest).encode()
    pin = {
        "name": "release-manifest.json",
        "size": len(data),
        "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
        "browser_download_url": probe.PUBLIC
        + "/releases/download/"
        + release["tag_name"]
        + "/release-manifest.json",
    }
    release["assets"] = [item for item in release["assets"] if item["name"] != pin["name"]] + [pin]
    return data


@pytest.mark.parametrize("version", [probe.INSTALLED, probe.TARGET])
def test_real_manifest_shape_is_authenticated_before_use(version):
    release, manifest = released(version)
    data = pin_manifest(release, manifest)
    assert (
        probe.verified_release(
            release, version, probe.INSTALLED_SOURCE, probe.INSTALLED_SOURCE, data
        )
        == manifest
    )
    assert "workflow_contract" not in released()[1]["tooling"]  # public RC2 legacy path


@pytest.mark.parametrize(
    "defect",
    [
        "tag",
        "draft",
        "stable",
        "source",
        "tag-source",
        "digest",
        "asset-pin",
        "asset-url",
        "runtime-pin",
        "asset-name",
        "runtime-contract",
        "no-registry",
    ],
)
def test_wrong_published_identity_is_not_public_acceptance(defect):
    release, manifest = released(probe.TARGET)
    tag_source = probe.INSTALLED_SOURCE
    if defect == "source":
        manifest["source_sha"] = "0" * 40
    elif defect == "asset-pin":
        manifest["tooling"]["sha256"] = "0" * 64
    elif defect == "runtime-pin":
        manifest["tooling"]["runtime_manifest_sha256"] = "not-a-hash"
    elif defect == "asset-name":
        manifest["tooling"]["filename"] = "other.tar.gz"
    elif defect == "runtime-contract":
        manifest["tooling"]["workflow_contract"] = True
    elif defect == "no-registry":
        manifest["registry_digest"] = None
    data = pin_manifest(release, manifest)
    if defect == "tag":
        release["tag_name"] = "v" + probe.INSTALLED
    elif defect == "draft":
        release["draft"] = True
    elif defect == "stable":
        release["prerelease"] = False
    elif defect == "tag-source":
        tag_source = "0" * 40
    elif defect == "digest":
        data += b" "
    elif defect == "asset-url":
        release["assets"][0]["browser_download_url"] = "https://evil.invalid/tooling"
    with pytest.raises(ValueError):
        probe.verified_release(release, probe.TARGET, probe.INSTALLED_SOURCE, tag_source, data)


def query_payload(project):
    advisory = {
        "current_version": probe.INSTALLED,
        "available_version": probe.TARGET,
        "release_url": probe.PUBLIC + "/releases/tag/v" + probe.TARGET,
        "freshness": "fresh",
    }
    return {
        "initialize": {
            "serverInfo": {"version": "0.2.0rc2"},
            "instructions": probe.INSTALLED + " " + probe.TARGET + " " + advisory["release_url"],
        },
        "results": [
            {
                "tool": "ada_project_info",
                "arguments": probe.project_arguments(project),
                "result": {
                    "complete": True,
                    "project_file": str(project / "arca.gpr"),
                    "source_dirs": [str(project / "src")],
                    "update_notice": advisory,
                },
            }
        ],
    }


@pytest.mark.parametrize(
    "defect",
    [
        "none",
        "server",
        "initialize",
        "missing",
        "target",
        "stale",
        "incomplete",
        "gpr",
        "scenario",
        "off-leak",
    ],
)
def test_protocol_result_needs_both_notices_and_actual_complete_rc2_view(tmp_path, defect):
    payload = query_payload(tmp_path)
    result = payload["results"][0]["result"]
    if defect == "none":
        probe.verify_query(payload, tmp_path, notice=True)
        off = copy.deepcopy(payload)
        off["initialize"]["instructions"] = None
        off["results"][0]["result"].pop("update_notice")
        probe.verify_query(off, tmp_path, notice=False)
        return
    if defect == "server":
        payload["initialize"]["serverInfo"]["version"] = "0.2.0rc3"
    elif defect == "initialize":
        payload["initialize"]["instructions"] = ""
    elif defect == "missing":
        result.pop("update_notice")
    elif defect == "target":
        result["update_notice"]["available_version"] = "0.3.0"
    elif defect == "stale":
        result["update_notice"]["freshness"] = "stale"
    elif defect == "incomplete":
        result["complete"] = False
    elif defect == "gpr":
        result["project_file"] = str(tmp_path / "other.gpr")
    elif defect == "scenario":
        payload["results"][0]["arguments"]["scenario_variables"] = {}
    with pytest.raises(ValueError):
        probe.verify_query(payload, tmp_path, notice=defect != "off-leak")


@pytest.mark.parametrize("remaining", ["0", "42"])
def test_api_records_and_honors_actual_provider_waits_without_retry(
    tmp_path, monkeypatch, remaining
):
    deadline = int(time.time()) + 3600
    headers = Message()
    headers["X-RateLimit-Remaining"] = remaining
    headers["X-RateLimit-Reset"] = str(deadline)
    reads, requests = [], []

    class Response:
        status = 200

        def __init__(self):
            self.headers = headers

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def geturl(self):
            return probe.API + "/fixture"

        def read(self, limit):
            reads.append(limit)
            return b'{"ok":true}'

    class Opener:
        def open(self, request, timeout):
            requests.append((request.full_url, timeout))
            return Response()

    monkeypatch.setattr(probe.urllib.request, "build_opener", lambda *args: Opener())
    if remaining == "0":
        with pytest.raises(ValueError, match="provider wait"):
            probe.api_json("/fixture", tmp_path, "request")
        assert not reads
    else:
        assert probe.api_json("/fixture", tmp_path, "request") == {"ok": True}
        assert reads == [probe.LIMIT + 1]
    assert len(requests) == 1
    receipt = json.loads((tmp_path / "request.request.json").read_text())
    assert receipt["provider_headers"]["X-RateLimit-Remaining"] == remaining
    assert receipt.get("blocked_until") == (deadline if remaining == "0" else None)


@pytest.mark.parametrize("defect", ["none", "cached", "blocked", "installed", "target", "stale"])
def test_manual_result_requires_actual_fresh_check_of_the_same_pair(tmp_path, defect):
    payload = {
        "check_performed": True,
        "status": "available",
        "current_version": probe.INSTALLED,
        "update_notice": query_payload(tmp_path)["results"][0]["result"]["update_notice"],
    }
    if defect == "none":
        probe.verify_manual(payload)
        return
    if defect == "cached":
        payload["check_performed"] = False
    elif defect == "blocked":
        payload.update(status="blocked", blocked_until=int(time.time()) + 600)
    elif defect == "installed":
        payload["current_version"] = probe.TARGET
    elif defect == "target":
        payload["update_notice"]["available_version"] = "0.3.0"
    else:
        payload["update_notice"]["freshness"] = "stale"
    with pytest.raises(ValueError):
        probe.verify_manual(payload)


def test_isolated_cli_rejects_unapproved_source_before_network_or_runtime(tmp_path):
    output, workspace = tmp_path / "evidence", tmp_path / "unused-workspace"
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(probe.ROOT / "scripts/public_notice_acceptance.py"),
            "--expected-source",
            "not-approved",
            "--output",
            str(output),
            "--workspace",
            str(workspace),
        ],
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["passed"] is False
    assert "approved RC3 source" in json.loads(result.stdout)["error"]
    assert not workspace.exists()
    assert {path.name for path in output.iterdir()} == {"summary.json", "failure.txt"}

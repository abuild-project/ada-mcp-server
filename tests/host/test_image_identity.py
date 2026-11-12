"""Authenticate metadata and executable-target boundaries; no Docker/Ada oracle."""

import base64
import copy
import hashlib
import json
import os
import subprocess
import sys
import tomllib

import ada_mcp_setup as setup
import artifacts
import image_identity
import pytest
from image_fixtures import classic_identity, corrupt_config_size, digest, metadata_archive
from test_setup_boundaries import binding
from version import ROOT


@pytest.mark.parametrize("kind", ["legacy", "oci", "hybrid"])
def test_export_binds_actual_config_and_target_without_logging_config_env(kind):
    oci = kind == "oci"
    stream, config, target = metadata_archive(oci, hybrid=kind == "hybrid")
    evidence = {}
    identity = image_identity.archive_identity(stream, config, target, evidence)
    assert image_identity.validate_identity(identity, config) == target
    assert identity["image_id"] == config
    assert identity["config_size"] > 0
    assert (target != config) is oci
    assert "TEST_PRIVATE_SENTINEL" not in json.dumps(evidence)
    if oci:
        stream.seek(0)
        with pytest.raises(RuntimeError, match="config image ID differs"):
            image_identity.archive_identity(stream, expected_config=target)


@pytest.mark.parametrize(
    "defect",
    [
        "digest",
        "size",
        "missing",
        "config",
        "platform",
        "duplicate",
        "attestation-only",
        "unreachable",
    ],
)
def test_bad_or_ambiguous_descriptor_proofs_fail_closed(defect):
    stream, config, _ = metadata_archive(True)
    identity = image_identity.archive_identity(stream)
    root = identity["target"]
    if defect == "digest":
        identity["metadata"][root["digest"]] = base64.b64encode(b"altered").decode()
    elif defect == "size":
        root["size"] += 1
    elif defect == "missing":
        identity["metadata"].pop(root["digest"])
    elif defect == "unreachable":
        identity["metadata"]["sha256:" + "d" * 64] = base64.b64encode(b"unused").decode()
    else:
        document = json.loads(base64.b64decode(identity["metadata"].pop(root["digest"])))
        if defect == "config":
            child = document["manifests"][0]
            child_doc = json.loads(base64.b64decode(identity["metadata"].pop(child["digest"])))
            child_doc["config"]["digest"] = "sha256:" + "f" * 64
            data = json.dumps(child_doc).encode()
            child.update(digest=digest(data), size=len(data))
            identity["metadata"][child["digest"]] = base64.b64encode(data).decode()
        elif defect == "platform":
            document["manifests"][0]["platform"]["architecture"] = "arm64"
        elif defect == "duplicate":
            document["manifests"].insert(0, copy.deepcopy(document["manifests"][0]))
        elif defect == "attestation-only":
            document["manifests"] = document["manifests"][1:]
        data = json.dumps(document).encode()
        root.update(digest=digest(data), size=len(data))
        identity["metadata"][root["digest"]] = base64.b64encode(data).decode()
    with pytest.raises(RuntimeError):
        image_identity.validate_identity(identity, config)


def test_inspected_target_and_source_version_cannot_relabel_an_archive(tmp_path):
    stream, config, target = metadata_archive(True)
    with pytest.raises(RuntimeError, match="export target differs"):
        image_identity.archive_identity(stream, expected_target="sha256:" + "f" * 64)
    archive = tmp_path / "image.tar"
    archive.write_bytes(stream.getvalue())
    with pytest.raises(ValueError, match="source/version"):
        artifacts.package(ROOT, tmp_path, "b" * 40, target, archive)
    assert (tmp_path / "image-identity-evidence.json").is_file()
    assert not list(tmp_path.glob("ada-mcp-tooling-*"))


@pytest.mark.parametrize(
    "input_oci,store_oci", [(False, False), (True, True), (True, False), (False, True)]
)
@pytest.mark.parametrize("source_kind", ["archive", "registry"])
def test_host_import_uses_verified_store_target_not_config_assumption(
    tmp_path, monkeypatch, input_oci, store_oci, source_kind
):
    incoming, config, _ = metadata_archive(input_oci)
    outgoing, outgoing_config, target = metadata_archive(store_oci)
    assert outgoing_config == config
    archive = tmp_path / "incoming.tar"
    archive.write_bytes(incoming.getvalue())
    export = tmp_path / "store.tar"
    export.write_bytes(outgoing.getvalue())
    fake = tmp_path / "fake_docker.py"
    fake.write_text("""import json,sys
from pathlib import Path
target, export = sys.argv[1:3]
args = sys.argv[3:]
if args[:2] == ['image','load']:
    sys.stdin.buffer.read()
    print('Loaded image ID: ' + target)
elif args[:2] == ['image','pull']:
    assert '--platform' in args and 'linux/amd64' in args
    print('Pulled pinned image')
elif args[:2] == ['image','inspect']:
    assert 'Config.Env' not in args[args.index('--format')+1]
    if args[-1] != target and not args[-1].startswith('registry.example.org/team/image@sha256:'):
        print('Error response from daemon: No such image: ' + args[-1], file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(dict(Id=target,Os='linux',Architecture='amd64',Labels={})))
elif args[:2] == ['image','save']:
    assert args[-1] == target
    sys.stdout.buffer.write(Path(export).read_bytes())
else: raise SystemExit('unexpected fake Docker command')
""")
    monkeypatch.setattr(
        setup,
        "docker_binding",
        lambda _: ([sys.executable, str(fake), target, str(export)], dict(os.environ)),
    )
    candidate = binding(tmp_path, config)
    candidate["image_identity"] = image_identity.archive_identity(incoming)
    candidate["image_source"] = {
        "kind": "archive",
        "path": str(archive),
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    if source_kind == "registry":
        candidate["image_source"] = {
            "kind": "registry",
            "reference": "registry.example.org/team/image@"
            + candidate["image_identity"]["target"]["digest"],
        }
    report = {}
    setup.provision_image(
        candidate, report, 10, {"source_sha": "a" * 40, "project_version": "0.2.0-rc.1"}
    )
    assert candidate["image_id"] == config
    assert setup.target_id(candidate) == target
    args = setup.launcher_arguments(candidate)
    assert args[args.index("--image") + 1] == target
    if source_kind == "archive":
        assert report["archive"]["image_validation"]["verified_before_load"] is True
    assert report["resolved_image"]["image_validation"]["actual_image_id"] == config


def test_malformed_archive_config_cannot_be_rescued_by_warm_cache(tmp_path, monkeypatch):
    incoming, _, _ = metadata_archive(True)
    archive = tmp_path / "wrong-image.tar"
    archive.write_bytes(incoming.getvalue())
    candidate = binding(tmp_path)
    candidate["image_source"] = {
        "kind": "archive",
        "path": str(archive),
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    monkeypatch.setattr(
        setup, "inspect_image", lambda *_: pytest.fail("cache lookup before archive validation")
    )
    with pytest.raises(RuntimeError, match="config image ID differs"):
        setup.provision_image(candidate, {}, 1)


def test_binding_target_must_have_a_config_bound_proof(tmp_path):
    candidate = binding(tmp_path)
    candidate["image_identity"] = classic_identity("sha256:" + "c" * 64)
    with pytest.raises(RuntimeError, match="config/platform lock"):
        setup.validate_binding(candidate, {"image_id": candidate["image_id"]})


@pytest.mark.parametrize("failure", ["unknown", "timeout", "oversize"])
def test_image_inspect_failure_is_bounded_and_never_absence(tmp_path, failure):
    fake = tmp_path / "inspect.py"
    fake.write_text(
        {
            "unknown": "import sys; print('permission denied',file=sys.stderr); "
            "raise SystemExit(1)",
            "timeout": "import sys,time; print('partial inspect',flush=True); "
            "print('partial err',file=sys.stderr,flush=True); time.sleep(30)",
            "oversize": "print('x'*(1024*1024+5))",
        }[failure]
    )
    report = {}
    with pytest.raises((RuntimeError, subprocess.TimeoutExpired)):
        setup.inspect_image(
            [sys.executable, str(fake)], dict(os.environ), "sha256:" + "a" * 64, report, 1
        )
    entry = report["commands"][0]
    assert "Config.Env" not in entry["argv"][entry["argv"].index("--format") + 1]
    assert len(entry["stdout"].encode()) <= 1024 * 1024
    if failure == "timeout":
        assert entry["timed_out"] and "partial inspect" in entry["stdout"]
        assert "partial err" in entry["stderr"]
    elif failure == "oversize":
        assert entry["stdout_truncated"]
    else:
        assert entry["rc"] == 1 and entry["stderr"] == "permission denied\n"


def test_native_and_query_use_host_target_with_canonical_config_lock(tmp_path, monkeypatch):
    stream, config, target = metadata_archive(True)
    candidate = binding(tmp_path, config)
    candidate["image_identity"] = image_identity.archive_identity(stream)
    monkeypatch.setattr(setup, "verified_manifest", lambda: {})
    monkeypatch.setattr(setup, "read_binding", lambda *_: candidate)
    monkeypatch.setattr(setup, "image_present", lambda *_: True)
    native = tmp_path / "native.toml"
    monkeypatch.setattr(sys, "argv", ["setup", "native-config", "--output", str(native)])
    assert setup.main() == 0
    args = tomllib.loads(native.read_text())["mcp_servers"]["ada"]["args"]
    assert args[args.index("--image") + 1] == target != config
    captured = []

    class ExecutedError(Exception):
        pass

    def execv(executable, args):
        captured.extend(args)
        raise ExecutedError()

    monkeypatch.setattr(setup.os, "execv", execv)
    monkeypatch.setattr(sys, "argv", ["setup", "query", "tools"])
    assert setup.main() == 1
    assert captured[captured.index("--image") + 1] == target != config


@pytest.mark.parametrize("hybrid", [False, True])
def test_rehashed_wrong_config_size_is_rejected_before_docker_load(tmp_path, monkeypatch, hybrid):
    valid, config, target = metadata_archive(oci=True, hybrid=hybrid)
    candidate = binding(tmp_path, config)
    candidate["image_identity"] = image_identity.archive_identity(valid, config, target)
    malformed, _, _ = metadata_archive(oci=True, hybrid=hybrid, mutate=corrupt_config_size)
    archive = tmp_path / "correct-hash-wrong-config-size.tar"
    archive.write_bytes(malformed.getvalue())
    candidate["image_source"] = {
        "kind": "archive",
        "path": str(archive),
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    monkeypatch.setattr(
        setup.subprocess, "run", lambda *_args, **_kwargs: pytest.fail("Docker ran")
    )
    report = {}
    with pytest.raises(RuntimeError, match="config size differs"):
        setup.provision_image(candidate, report, 1)
    assert report["archive"]["verified_before_load"]
    assert report["archive"]["image_validation"]["status"] == "failed"
    assert report["archive"]["image_validation"]["actual_image_id"] == config


def test_hybrid_serialized_proof_checks_graph_and_size_despite_config_execution_target():
    stream, config, target = metadata_archive(hybrid=True)
    identity = image_identity.archive_identity(stream, config, target)
    identity = json.loads(json.dumps(identity))
    root = identity["oci_root"]
    document = json.loads(base64.b64decode(identity["metadata"].pop(root["digest"])))
    document["config"]["size"] += 1
    data = json.dumps(document).encode()
    root.update(digest=digest(data), size=len(data))
    identity["metadata"][root["digest"]] = base64.b64encode(data).decode()
    with pytest.raises(RuntimeError, match="config size differs"):
        image_identity.validate_identity(identity, config)


def test_host_binding_size_cannot_drift_from_trusted_runtime_manifest(tmp_path):
    candidate = binding(tmp_path)
    trusted = {
        "image_id": candidate["image_id"],
        "image_identity": copy.deepcopy(candidate["image_identity"]),
    }
    candidate["image_identity"]["config_size"] += 1
    candidate["image_identity"]["target"]["size"] += 1
    with pytest.raises(RuntimeError, match="byte count does not match"):
        setup.validate_binding(candidate, trusted)


@pytest.mark.parametrize("kind", ["legacy", "hybrid", "oci"])
def test_config_execution_target_size_is_not_an_oci_layout_inference(kind):
    stream, config, target = metadata_archive(oci=kind == "oci", hybrid=kind == "hybrid")
    identity = image_identity.archive_identity(stream, config, target)
    identity["config_size"] += 1
    with pytest.raises(RuntimeError, match="size"):
        image_identity.validate_identity(identity, config)

"""Check bootstrap's local aliases without substituting them for immutable pins."""

import json
import os
import subprocess
import sys

import ada_mcp_setup as setup
import image_identity
import pytest
from image_fixtures import metadata_archive
from test_setup_boundaries import binding


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("cold", [False, True])
def test_bootstrap_assigns_version_tag_and_keeps_binding_target(
    tmp_path, monkeypatch, capsys, existing, cold
):
    candidate = binding(tmp_path)
    path = tmp_path / "binding.json"
    if existing:
        path.write_text(json.dumps(candidate))
    original = path.read_bytes() if existing else None
    manifest = {
        "image_id": candidate["image_id"],
        "image_identity": candidate["image_identity"],
        "project_version": "0.3.0-rc.1",
    }
    events = []
    images = {} if cold else {candidate["image_id"]: candidate["image_id"]}

    def inspect(docker, environment, reference, report, timeout):
        events.append(("inspect", reference))
        target = images.get(reference)
        return (
            dict(Id=target, Os="linux", Architecture="amd64", Labels={})
            if target is not None
            else None
        )

    def provision(value, report, timeout, manifest):
        events.append(("provision", value["image_id"]))
        images[value["image_id"]] = value["image_id"]

    def doctor(*args):
        events.append(("doctor",))

    def command(argv, environment, report, timeout, **kwargs):
        assert argv[:3] == ["docker", "image", "tag"]
        events.append(("tag", argv[-2], argv[-1]))
        images[argv[-1]] = argv[-2]
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(setup, "verified_manifest", lambda: manifest)
    monkeypatch.setattr(setup, "inspect_image", inspect)
    monkeypatch.setattr(setup, "provision_image", provision)
    monkeypatch.setattr(setup, "doctor", doctor)
    monkeypatch.setattr(setup, "command_run", command)
    arguments = ["setup", "bootstrap", "--binding", str(path)]
    if not existing:
        arguments += ["--root", str(tmp_path), "--uid", "1000", "--gid", "1000"]
    monkeypatch.setattr(sys, "argv", arguments)
    assert setup.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert images["ada-mcp-server:0.3.0-rc.1"] == candidate["image_id"]
    assert events.index(("doctor",)) < events.index(
        ("tag", candidate["image_id"], "ada-mcp-server:0.3.0-rc.1")
    )
    assert any(event[0] == "provision" for event in events) is cold
    assert result["image_tag"]["status"] == "created"
    if existing:
        assert path.read_bytes() == original
    saved = json.loads(path.read_text())
    assert setup.target_id(saved) == candidate["image_id"]
    assert setup.launcher_arguments(saved)[2] == candidate["image_id"]


@pytest.mark.parametrize("preexisting", ["absent", "same", "different", "unknown"])
def test_version_alias_observes_docker_identity_without_overwriting(
    tmp_path, monkeypatch, preexisting
):
    candidate = binding(tmp_path)
    target = candidate["image_id"]
    tag = "ada-mcp-server:0.3.0+build.2".replace("+", "_")
    state = tmp_path / "state.json"
    state.write_text(json.dumps({tag: target} if preexisting == "same" else {}))
    if preexisting == "different":
        state.write_text(json.dumps({tag: "sha256:" + "c" * 64}))
    fake = tmp_path / "docker.py"
    fake.write_text("""import json, sys
from pathlib import Path
state, unknown = Path(sys.argv[1]), sys.argv[2]
args = sys.argv[3:]
images = json.loads(state.read_text())
if args[:2] == ["image", "inspect"]:
    if unknown == "unknown":
        print("permission denied", file=sys.stderr)
        raise SystemExit(1)
    if args[-1] not in images:
        print("Error response from daemon: No such image: " + args[-1], file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(dict(Id=images[args[-1]], Os="linux", Architecture="amd64", Labels={})))
elif args[:2] == ["image", "tag"]:
    assert args[-1] not in images, "existing tag overwritten"
    images[args[-1]] = args[-2]
    state.write_text(json.dumps(images))
else:
    raise SystemExit("unexpected Docker command")
""")
    monkeypatch.setattr(
        setup,
        "docker_binding",
        lambda _: ([sys.executable, str(fake), str(state), preexisting], dict(os.environ)),
    )
    report = {}
    if preexisting in {"different", "unknown"}:
        before = state.read_bytes()
        with pytest.raises(RuntimeError, match="different target|unknown"):
            setup.tag_image(candidate, {"project_version": "0.3.0+build.2"}, report, 10)
        assert state.read_bytes() == before
        assert not any("tag" in c["argv"] for c in report.get("commands", []))
    else:
        setup.tag_image(candidate, {"project_version": "0.3.0+build.2"}, report, 10)
        assert json.loads(state.read_text())[tag] == target
        assert report["image_tag"]["status"] == ("present" if preexisting == "same" else "created")
        assert sum("tag" in c["argv"] for c in report["commands"]) == (
            0 if preexisting == "same" else 1
        )


def test_bootstrap_does_not_tag_when_doctor_fails(tmp_path, monkeypatch, capsys):
    candidate = binding(tmp_path)
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(candidate))
    manifest = {"image_id": candidate["image_id"]}
    monkeypatch.setattr(setup, "verified_manifest", lambda: manifest)
    monkeypatch.setattr(setup, "read_binding", lambda *args: candidate)
    monkeypatch.setattr(setup, "image_present", lambda *args: True)

    def fail(*args):
        raise RuntimeError("doctor failed")

    monkeypatch.setattr(setup, "doctor", fail)
    monkeypatch.setattr(
        setup, "command_run", lambda *args, **kwargs: pytest.fail("Docker tag invoked")
    )
    monkeypatch.setattr(sys, "argv", ["setup", "bootstrap", "--binding", str(path)])
    assert setup.main() == 1
    assert "doctor failed" in json.loads(capsys.readouterr().out)["error"]


def test_tag_uses_verified_oci_store_target_and_checks_the_result(tmp_path, monkeypatch):
    stream, config, target = metadata_archive(oci=True)
    assert target != config
    candidate = binding(tmp_path, config)
    candidate["image_identity"] = image_identity.archive_identity(stream)
    commands = []
    inspections = iter([None, dict(Id=config)])
    monkeypatch.setattr(setup, "inspect_image", lambda *args: next(inspections))

    def command(argv, *args):
        commands.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(setup, "command_run", command)
    report = {}
    with pytest.raises(RuntimeError, match="does not identify pinned target"):
        setup.tag_image(candidate, {"project_version": "0.3.0"}, report, 10)
    assert commands == [["docker", "image", "tag", target, "ada-mcp-server:0.3.0"]]
    assert report["image_tag"]["status"] == "checking"


@pytest.mark.parametrize("version", [None, True, "../escape", "v" * 129])
def test_invalid_tag_version_never_reaches_docker(tmp_path, monkeypatch, version):
    monkeypatch.setattr(
        setup, "docker_binding", lambda *args: pytest.fail("Docker prepared for invalid tag")
    )
    with pytest.raises(RuntimeError, match="version"):
        setup.tag_image(binding(tmp_path), {"project_version": version}, {}, 10)

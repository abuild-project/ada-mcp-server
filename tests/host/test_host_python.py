"""Exercise GUI interpreter selection without Docker or update networking."""

import json
import os
import shutil
import subprocess
import sys
import tomllib

import ada_mcp_setup as setup
import pytest
from test_setup_boundaries import binding
from version import ROOT


@pytest.fixture
def gui_launch(tmp_path):
    binary = tmp_path / "bin"
    binary.mkdir()
    bad_python = binary / "python3"
    bad_python.write_text("#!/bin/sh\nprintf '3.9.6\\n'\nexit 1\n")
    bad_python.chmod(0o755)
    capture = tmp_path / "docker.json"
    docker = binary / "docker"
    docker.write_text(
        f"#!{sys.executable}\n"
        "import json,os,sys\nfrom pathlib import Path\n"
        "if sys.argv[1:3] == ['image','inspect']:\n"
        "    print('linux/amd64' if 'Architecture' in sys.argv[4] else 'sha256:'+'a'*64)\n"
        "else:\n"
        f"    Path({str(capture)!r}).write_text(json.dumps(sys.argv[1:]))\n"
        "    sys.stdout.write(sys.stdin.read())\n"
    )
    docker.chmod(0o755)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    launcher = scripts / "ada-mcp-launch"
    shutil.copy2(ROOT / "tooling/ada-mcp-launch", launcher)
    marker = tmp_path / "checker"
    (scripts / "release_updates.py").write_text(
        "import sys\nfrom pathlib import Path\n"
        "assert sys.version_info >= (3,11)\n"
        f"Path({str(marker)!r}).write_text(sys.stdin.read())\n"
        'print(\'{"available_version":"0.3.0"}\')\n'
    )
    environment = dict(os.environ, PATH=str(binary) + ":/usr/bin:/bin")
    environment.pop("ADA_MCP_UPDATE_CHANNEL", None)
    environment.pop("ADA_MCP_UPDATE_CACHE", None)
    command = [
        "/bin/bash",
        str(launcher),
        "--image",
        "fixture",
        "--root",
        str(tmp_path.resolve()),
        "--uid",
        "1000",
        "--gid",
        "1000",
    ]
    return command, environment, capture, marker


def launch(gui_launch, arguments):
    command, environment, _, _ = gui_launch
    return subprocess.run(
        command + arguments,
        env=environment,
        input='{"jsonrpc":"2.0","id":1}\n',
        text=True,
        capture_output=True,
        timeout=10,
    )


def notice(capture):
    return next(
        arg.split("=", 1)[1]
        for arg in json.loads(capture.read_text())
        if arg.startswith("ADA_MCP_UPDATE_NOTICE=")
    )


def test_pinned_setup_python_survives_gui_path_with_python39(gui_launch):
    result = launch(gui_launch, ["--python", sys.executable])
    _, _, capture, marker = gui_launch
    assert result.returncode == 0 and result.stderr == ""
    assert result.stdout == '{"jsonrpc":"2.0","id":1}\n'
    assert json.loads(notice(capture)) == {"available_version": "0.3.0"}
    assert marker.read_text() == ""


@pytest.mark.parametrize("arguments", [[], ["--python", "/missing/python"]])
def test_bad_advisory_python_is_diagnosed_without_consuming_protocol(gui_launch, arguments):
    result = launch(gui_launch, arguments)
    _, _, capture, marker = gui_launch
    assert result.returncode == 0 and notice(capture) == ""
    assert result.stdout == '{"jsonrpc":"2.0","id":1}\n'
    assert "Python 3.11+ required" in result.stderr
    assert "MCP remains usable" in result.stderr and len(result.stderr) < 256
    assert not marker.exists()


@pytest.mark.parametrize("supported", [False, True])
def test_launcher_check_validates_python_offline(gui_launch, supported):
    arguments = ["--check", "--update-channel", "auto"]
    if supported:
        arguments += ["--python", sys.executable]
    result = launch(gui_launch, arguments)
    _, _, capture, marker = gui_launch
    metadata = dict(line.split("=", 1) for line in result.stdout.splitlines())
    assert metadata["update_channel"] == "auto"
    assert metadata["python_status"] == ("supported" if supported else "unavailable-or-unsupported")
    assert result.returncode == (0 if supported else 2)
    assert not capture.exists() and not marker.exists()


def test_deliberate_off_needs_no_advisory_python(gui_launch):
    result = launch(gui_launch, ["--python", "/missing/python", "--update-channel", "off"])
    _, _, capture, marker = gui_launch
    assert result.returncode == 0 and result.stderr == "" and notice(capture) == ""
    checked = launch(
        gui_launch, ["--python", "/missing/python", "--update-channel", "off", "--check"]
    )
    assert checked.returncode == 0 and checked.stderr == ""
    assert "python_status=disabled" in checked.stdout and not marker.exists()


@pytest.mark.parametrize(
    "environment,arguments,channel,source",
    [
        (None, [], "auto", "default"),
        ("off", [], "off", "environment"),
        ("off", ["--update-channel", "auto"], "auto", "argument"),
        ("auto", ["--update-channel", "off"], "off", "argument"),
    ],
)
def test_native_generation_pins_python_and_effective_policy(
    tmp_path, monkeypatch, capsys, environment, arguments, channel, source
):
    candidate = binding(tmp_path)
    monkeypatch.setattr(setup, "verified_manifest", lambda: {})
    monkeypatch.setattr(setup, "read_binding", lambda *_: candidate)
    monkeypatch.setattr(setup, "image_present", lambda *_: True)
    monkeypatch.delenv("ADA_MCP_UPDATE_CHANNEL", raising=False)
    monkeypatch.delenv("ADA_MCP_UPDATE_CACHE", raising=False)
    if environment:
        monkeypatch.setenv("ADA_MCP_UPDATE_CHANNEL", environment)
    output = tmp_path / "native.toml"
    monkeypatch.setattr(
        sys,
        "argv",
        ["setup", "native-config", "--output", str(output), *arguments],
    )
    assert setup.main() == 0
    report = json.loads(capsys.readouterr().out)
    fragment = tomllib.loads(output.read_text())["mcp_servers"]["ada"]["args"]
    assert fragment[fragment.index("--python") + 1] == sys.executable
    assert fragment[fragment.index("--update-channel") + 1] == channel
    assert report["update_policy"] == {"channel": channel, "source": source}
    assert report["host_python"]["path"] == sys.executable
    assert report["installed_in_native_client"] is False


def test_doctor_separates_intended_policy_from_its_offline_probe(tmp_path, monkeypatch):
    commands = []
    launches = []
    monkeypatch.setattr(setup, "image_present", lambda *_: True)
    monkeypatch.setattr(setup, "inspect_container", lambda *_: None)

    def checked(command, *_):
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "python_status=supported\n", "")

    def session(command, *_):
        launches.append(command)
        raise RuntimeError("stop after offline validation")

    monkeypatch.setattr(setup, "command_run", checked)
    original_load = setup.load_helper
    monkeypatch.setattr(
        setup,
        "load_helper",
        lambda name: {"Session": session} if name == "mcp_client" else original_load(name),
    )
    report = {"update_policy": {"channel": "auto"}, "host_python": {"path": sys.executable}}
    with pytest.raises(RuntimeError, match="stop after offline validation"):
        setup.doctor(binding(tmp_path), {}, report, None, 5, 5)
    assert commands[0][-3:] == ["--update-channel", "auto", "--check"]
    assert launches[0][-2:] == ["--update-channel", "off"]
    assert report["update_policy"]["channel"] == "auto"
    assert report["doctor"]["probe_update_channel"] == "off"

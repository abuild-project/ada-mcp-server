"""Exercise GUI interpreter selection without Docker or update networking."""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import tomllib

import ada_mcp_setup as setup
import mcp_client
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
    if supported:
        assert metadata["python_version"] == ".".join(map(str, sys.version_info[:3]))
    assert result.returncode == (0 if supported else 2)
    assert not capture.exists() and not marker.exists()


@pytest.mark.parametrize("version", [None, "not-a-version", "3.9.6"])
def test_zero_exit_probe_requires_a_supported_reported_version(gui_launch, tmp_path, version):
    interpreter = "/bin/true"
    if version is not None:
        stub = tmp_path / "zero-exit-python"
        stub.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\nexit 0\n")
        stub.chmod(0o755)
        interpreter = str(stub)
    arguments = ["--python", interpreter, "--update-channel", "auto"]
    checked = launch(gui_launch, [*arguments, "--check"])
    assert checked.returncode == 2 and "Python 3.11+ required" in checked.stderr
    assert "python_status=unavailable-or-unsupported" in checked.stdout
    result = launch(gui_launch, arguments)
    _, _, capture, marker = gui_launch
    assert result.returncode == 0 and result.stdout == '{"jsonrpc":"2.0","id":1}\n'
    assert "Python 3.11+ required" in result.stderr and len(result.stderr) < 256
    assert notice(capture) == "" and not marker.exists()
    if version is None:
        disabled = launch(
            gui_launch, ["--python", interpreter, "--update-channel", "off", "--check"]
        )
        assert disabled.returncode == 0 and disabled.stderr == ""
        assert "python_status=disabled" in disabled.stdout


@pytest.mark.parametrize(
    "trailer",
    [
        pytest.param("not-a-version", id="trailing-text"),
        pytest.param("x" * 128, id="oversized-trailer"),
    ],
)
def test_probe_requires_one_complete_bounded_version_line(gui_launch, tmp_path, trailer):
    interpreter = tmp_path / "trailing-output-python"
    interpreter.write_text(f"#!/bin/sh\nprintf '%s\\n' '3.11.0' '{trailer}'\nexit 0\n")
    interpreter.chmod(0o755)
    arguments = ["--python", str(interpreter), "--update-channel", "auto"]
    checked = launch(gui_launch, [*arguments, "--check"])
    assert checked.returncode == 2 and "Python 3.11+ required" in checked.stderr
    assert "python_status=unavailable-or-unsupported" in checked.stdout
    result = launch(gui_launch, arguments)
    _, _, capture, marker = gui_launch
    assert result.returncode == 0 and result.stdout == '{"jsonrpc":"2.0","id":1}\n'
    assert "Python 3.11+ required" in result.stderr and len(result.stderr) < 256
    assert notice(capture) == "" and not marker.exists()


def test_deliberate_off_needs_no_advisory_python(gui_launch):
    result = launch(gui_launch, ["--python", "/missing/python", "--update-channel", "off"])
    _, _, capture, marker = gui_launch
    assert result.returncode == 0 and result.stderr == "" and notice(capture) == ""
    checked = launch(
        gui_launch, ["--python", "/missing/python", "--update-channel", "off", "--check"]
    )
    assert checked.returncode == 0 and checked.stderr == ""
    assert "python_status=disabled" in checked.stdout and not marker.exists()


@pytest.mark.parametrize("check", [False, True])
def test_hanging_python_probe_is_killed_reaped_and_bounded(gui_launch, tmp_path, check):
    command, environment, capture, marker = gui_launch
    pid_file = tmp_path / "probe.pid"
    interpreter = tmp_path / "hanging-python"
    interpreter.write_text(
        f"#!{sys.executable}\n"
        "import os,signal,time\nfrom pathlib import Path\n"
        f"Path({str(pid_file)!r}).write_text(str(os.getpid()))\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "while True: time.sleep(60)\n"
    )
    interpreter.chmod(0o755)
    scratch = tmp_path / "private-probe-output"
    scratch.mkdir()
    environment["TMPDIR"] = str(scratch)
    arguments = ["--python", str(interpreter)] + (["--check"] if check else [])
    started = time.monotonic()
    process = subprocess.Popen(
        command + arguments,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        try:
            stdout, stderr = process.communicate('{"jsonrpc":"2.0","id":1}\n', timeout=4)
        except subprocess.TimeoutExpired:
            pytest.fail("host Python probe exceeded the independent deadline")
        assert time.monotonic() - started < 4
        assert process.returncode == (2 if check else 0)
        assert "two-second deadline" in stderr and len(stderr) < 256
        if check:
            assert "python_status=timed-out" in stdout and not capture.exists()
        else:
            assert stdout == '{"jsonrpc":"2.0","id":1}\n' and notice(capture) == ""
        with pytest.raises(ProcessLookupError):
            os.kill(int(pid_file.read_text()), 0)
        assert not marker.exists() and list(scratch.iterdir()) == []
    finally:
        if pid_file.exists():
            try:
                os.kill(int(pid_file.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=2)


def test_invalid_inherited_channel_keeps_launcher_usable_but_fails_check(gui_launch):
    _, environment, capture, marker = gui_launch
    environment["ADA_MCP_UPDATE_CHANNEL"] = "disabled"
    result = launch(gui_launch, ["--python", sys.executable])
    assert result.returncode == 0 and result.stdout == '{"jsonrpc":"2.0","id":1}\n'
    assert notice(capture) == "" and not marker.exists()
    assert result.stderr.count("Invalid inherited update channel") == 1
    assert len(result.stderr) < 256
    checked = launch(gui_launch, ["--check", "--python", sys.executable])
    assert checked.returncode == 2 and "invalid update channel" in checked.stderr


def test_invalid_inherited_query_channel_is_disabled_once_while_setup_stays_strict(
    gui_launch, tmp_path, monkeypatch, capsys
):
    command, environment, capture, marker = gui_launch
    environment["ADA_MCP_UPDATE_CHANNEL"] = "disabled"
    monkeypatch.setenv("ADA_MCP_UPDATE_CHANNEL", "disabled")
    monkeypatch.setattr(setup, "verified_manifest", lambda: {})
    monkeypatch.setattr(setup, "read_binding", lambda *_: binding(tmp_path))
    monkeypatch.setattr(setup, "image_present", lambda *_: True)
    monkeypatch.setattr(
        setup, "launcher_arguments", lambda *_: command[1:] + ["--python", sys.executable]
    )

    def client(arguments):
        assert arguments.count("--update-channel") == 1
        assert arguments[arguments.index("--update-channel") + 1] == "off"
        parser = argparse.ArgumentParser()
        mcp_client.add_launch_arguments(parser)
        parser.add_argument("request")
        options = parser.parse_args(["--launcher", command[1], *arguments])
        result = subprocess.run(
            mcp_client.launcher_command(options),
            env=environment,
            input='{"jsonrpc":"2.0","id":1}\n',
            text=True,
            capture_output=True,
            timeout=4,
        )
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        return result.returncode

    monkeypatch.setattr(setup, "load_helper", lambda _: {"main": client})
    monkeypatch.setattr(sys, "argv", ["setup", "query", "tools"])
    assert setup.main() == 0
    streams = capsys.readouterr()
    assert streams.out == '{"jsonrpc":"2.0","id":1}\n'
    assert streams.err.count("Invalid inherited update channel") == 1 and len(streams.err) < 256
    assert notice(capture) == "" and not marker.exists()
    for mode in ["native-config", "doctor"]:
        output = tmp_path / (mode + ".toml")
        arguments = ["setup", mode] + (["--output", str(output)] if mode == "native-config" else [])
        monkeypatch.setattr(sys, "argv", arguments)
        assert setup.main() == 1
        report = json.loads(capsys.readouterr().out)
        assert "invalid update channel" in report["error"] and not output.exists()


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

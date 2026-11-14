"""Real launcher parsing with a Docker argv stub; never mount any host root."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import ada_mcp_setup as setup
import pytest
from test_setup_boundaries import binding
from version import ROOT


@pytest.fixture
def docker_stub(tmp_path):
    binary = tmp_path / "bin"
    binary.mkdir()
    capture = tmp_path / "docker-argv.jsonl"
    stub = binary / "docker"
    stub.write_text("""#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
with Path(os.environ['CAPTURE']).open('a') as stream: stream.write(json.dumps(sys.argv[1:])+'\\n')
if sys.argv[1:3] == ['image','inspect']:
    template=sys.argv[sys.argv.index('--format')+1]
    print('linux/amd64' if 'Architecture' in template else 'sha256:'+'a'*64)
elif sys.argv[1] != 'run': raise SystemExit('unexpected stub invocation')
""")
    stub.chmod(0o755)
    environment = dict(
        os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"], CAPTURE=str(capture)
    )
    return capture, environment


@pytest.mark.parametrize("kind", ["filesystem-alias", "directory-alias", "ancestor-alias"])
def test_symlink_root_is_refused_before_any_docker_use(tmp_path, docker_stub, kind):
    actual = tmp_path / "physical"
    (actual / "child").mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to("/" if kind == "filesystem-alias" else actual, target_is_directory=True)
    root = alias / "child" if kind == "ancestor-alias" else alias
    capture, environment = docker_stub
    result = subprocess.run(
        [str(ROOT / "tooling/ada-mcp-launch"), "--image", "fixture", "--root", str(root)],
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "physical" in result.stderr
    assert not capture.exists()


def test_physical_unicode_and_space_paths_keep_same_path_readonly_mount(tmp_path, docker_stub):
    root = tmp_path / "physical Ω path"
    root.mkdir()
    root = root.resolve()
    capture, environment = docker_stub
    subprocess.run(
        [
            str(ROOT / "tooling/ada-mcp-launch"),
            "--image",
            "fixture",
            "--root",
            str(root),
            "--uid",
            "1000",
            "--gid",
            "1000",
        ],
        env=environment,
        check=True,
    )
    calls = [json.loads(line) for line in capture.read_text().splitlines()]
    assert calls[-1][0] == "run"
    assert "type=bind,src=" + str(root) + ",dst=" + str(root) + ",readonly" in calls[-1]


@pytest.mark.parametrize("reserved", setup.RESERVED_RUNTIME_PATHS)
@pytest.mark.parametrize("suffix", ["", "/synthetic-project"])
def test_reserved_runtime_equal_or_descendant_rejected_before_docker(docker_stub, reserved, suffix):
    capture, environment = docker_stub
    result = subprocess.run(
        [str(ROOT / "tooling/ada-mcp-launch"), "--image", "fixture", "--root", reserved + suffix],
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "reserved runtime" in result.stderr
    assert not capture.exists()


@pytest.mark.parametrize("root", ["/opt", "/usr", "/usr/local"])
def test_reserved_runtime_ancestors_rejected_before_docker(docker_stub, root):
    capture, environment = docker_stub
    result = subprocess.run(
        [str(ROOT / "tooling/ada-mcp-launch"), "--image", "fixture", "--root", root],
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "reserved runtime" in result.stderr
    assert not capture.exists()


@pytest.mark.parametrize(
    "root",
    ["/opt/my-project", "/usr/local/src", "/opt/ada-mcp-extra", "/usr/lib-extra", "/etcetera"],
)
def test_reserved_policy_preserves_component_disjoint_project_paths(docker_stub, root):
    setup.validate_root_placement(Path(root))
    _, environment = docker_stub
    result = subprocess.run(
        [str(ROOT / "tooling/ada-mcp-launch"), "--image", "fixture", "--root", root],
        env=environment,
        capture_output=True,
        text=True,
    )
    assert "reserved runtime" not in result.stderr
    if Path(root).is_dir() and str(Path(root).resolve()) == root:
        assert result.returncode == 0
    else:
        assert result.returncode == 2


@pytest.mark.parametrize(
    "root", ["/opt/ada-mcp", "/opt/ada-mcp/venv/bin", "/opt", "/usr/local/lib", "/etc"]
)
def test_binding_rejects_reserved_roots_before_filesystem_or_docker(tmp_path, root):
    candidate = binding(tmp_path)
    candidate["roots"] = [root]
    manifest = {"image_id": candidate["image_id"], "image_identity": candidate["image_identity"]}
    with pytest.raises(RuntimeError, match="reserved runtime"):
        setup.validate_binding(candidate, manifest)


@pytest.mark.parametrize("failure", [False, True])
def test_notice_is_data_only_and_checker_failure_does_not_stop_launch(
    tmp_path, docker_stub, failure
):
    scripts = tmp_path / "runtime/scripts"
    scripts.mkdir(parents=True)
    launcher = scripts / "ada-mcp-launch"
    shutil.copy2(ROOT / "tooling/ada-mcp-launch", launcher)
    received = tmp_path / "checker-stdin"
    helper = scripts / "release_updates.py"
    helper.write_text(
        "import json,sys\nfrom pathlib import Path\n"
        f"Path({str(received)!r}).write_text(sys.stdin.read())\n"
        + (
            "raise SystemExit(42)\n"
            if failure
            else "print(json.dumps({'available_version':'0.3.0'}))\n"
        )
    )
    root = tmp_path / "physical"
    root.mkdir()
    capture, environment = docker_stub
    result = subprocess.run(
        [
            str(launcher),
            "--image",
            "fixture",
            "--root",
            str(root),
            "--update-channel",
            "stable",
            "--update-cache",
            str(tmp_path / "new-cache"),
        ],
        env=environment,
        input="MCP input must remain for Docker",
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0 and result.stdout == ""
    assert received.read_text() == ""
    command = json.loads(capture.read_text().splitlines()[-1])
    assert command[command.index("--network") + 1] == "none"
    assert "--read-only" in command and "--cap-drop" in command
    assert command.count("--mount") == 1
    payload = next(
        value.split("=", 1)[1] for value in command if value.startswith("ADA_MCP_UPDATE_NOTICE=")
    )
    assert payload == "" if failure else json.loads(payload) == {"available_version": "0.3.0"}

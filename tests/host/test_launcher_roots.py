"""Real launcher parsing with a Docker argv stub; never mount any host root."""

import json
import os
import subprocess

import pytest
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

"""Build guard tests use a Docker sentinel; they do not build a runtime image."""

import hashlib
import io
import os
import shutil
import subprocess
import tarfile

from version import ROOT


def test_dirty_source_never_gets_a_commit_labeled_image(tmp_path):
    repository = tmp_path / "source with spaces"
    (repository / "docker").mkdir(parents=True)
    (repository / "scripts").mkdir()
    (repository / "src/ada_mcp").mkdir(parents=True)
    shutil.copy2(ROOT / "docker/build", repository / "docker/build")
    shutil.copy2(ROOT / "scripts/version.py", repository / "scripts/version.py")
    shutil.copy2(ROOT / "src/ada_mcp/_version.py", repository / "src/ada_mcp/_version.py")

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repository), *args], text=True, capture_output=True, check=True
        ).stdout.strip()

    git("init", "--initial-branch", "codex/guard")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("add", ".")
    git("commit", "-m", "Fixture source")
    binary = tmp_path / "bin"
    binary.mkdir()
    fake = binary / "docker"
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$FAKE_DOCKER_ARGS"\n')
    fake.chmod(0o755)
    arguments = tmp_path / "arguments"
    environment = dict(
        os.environ,
        PATH=str(binary) + os.pathsep + os.environ["PATH"],
        FAKE_DOCKER_ARGS=str(arguments),
    )
    (repository / "untracked-source.py").write_text("changed candidate\n")
    result = subprocess.run(
        [str(repository / "docker/build")], env=environment, text=True, capture_output=True
    )
    assert result.returncode == 2 and "Commit the candidate" in result.stderr
    assert not arguments.exists()
    (repository / "untracked-source.py").unlink()
    subprocess.run(
        [str(repository / "docker/build"), "--tag", "fixture:candidate"],
        env=environment,
        check=True,
    )
    actual = arguments.read_text().splitlines()
    assert "SOURCE_SHA=" + git("rev-parse", "HEAD") in actual
    assert "PROJECT_VERSION=0.2.0-rc.1" in actual
    assert actual[-1] == "-"
    assert actual[actual.index("--file") + 1] == "docker/Dockerfile"


def test_ignored_sentinel_never_enters_the_committed_context(tmp_path):
    repository = tmp_path / "source"
    (repository / "docker").mkdir(parents=True)
    (repository / "src/ada_mcp").mkdir(parents=True)
    for name in ["docker/build", "docker/Dockerfile", ".dockerignore", "src/ada_mcp/_version.py"]:
        shutil.copy2(ROOT / name, repository / name)
    (repository / ".gitignore").write_text("arbitrary-ignored-inputs/\n.env\n")

    def git(*args):
        return subprocess.check_output(["git", "-C", str(repository), *args], text=True).strip()

    git("init", "--initial-branch", "codex/context")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("add", ".")
    git("commit", "-m", "Fixture source")
    ignored = repository / "arbitrary-ignored-inputs"
    ignored.mkdir()
    (ignored / "local-private-sentinel").write_bytes(b"must never enter the image context")
    (repository / ".env").write_bytes(b"SECOND_PRIVATE_SENTINEL=not-a-real-secret\n")
    assert git("status", "--porcelain") == ""
    binary = tmp_path / "bin"
    binary.mkdir()
    fake = binary / "docker"
    fake.write_text("""#!/usr/bin/env python3
import os, sys
from pathlib import Path
if sys.argv[-1] != '-':
    raise SystemExit('directory context rejected by source-boundary control')
Path(os.environ['CAPTURED_CONTEXT']).write_bytes(sys.stdin.buffer.read())
""")
    fake.chmod(0o755)
    capture = tmp_path / "captured.tar"
    environment = dict(
        os.environ,
        PATH=str(binary) + os.pathsep + os.environ["PATH"],
        CAPTURED_CONTEXT=str(capture),
    )
    old_style = subprocess.run(
        [str(fake), "build", str(repository)], env=environment, text=True, capture_output=True
    )
    assert old_style.returncode != 0 and "directory context rejected" in old_style.stderr
    subprocess.run([str(repository / "docker/build")], env=environment, check=True)
    with tarfile.open(fileobj=io.BytesIO(capture.read_bytes())) as archive:
        files = {
            member.name: archive.extractfile(member).read() for member in archive if member.isfile()
        }
    tracked = git("ls-files", "-z").strip("\0").split("\0")
    assert set(files) == set(tracked)
    for name in tracked:
        expected = subprocess.check_output(["git", "-C", str(repository), "show", "HEAD:" + name])
        assert hashlib.sha256(files[name]).digest() == hashlib.sha256(expected).digest()
    assert all(b"PRIVATE_SENTINEL" not in content for content in files.values())


def test_ci_scratch_is_private_executable_and_separate_from_production_tmp():
    check = (ROOT / "docker/check").read_text()
    assert "/tmp:rw,nosuid,nodev,noexec" in check
    assert "/ci-work:rw,nosuid,nodev,exec," in check and "mode=0700" in check
    assert "TMPDIR=/ci-work/tmp" in check
    assert "--network none --read-only" in check
    assert "--cap-drop ALL --security-opt no-new-privileges" in check
    production = (ROOT / "tooling/ada-mcp-launch").read_text()
    assert "/tmp:rw,nosuid,nodev,noexec" in production
    assert "/ci-work" not in production


def test_repeated_check_rejects_existing_output_before_docker_or_writes(tmp_path):
    repository = tmp_path / "source"
    (repository / "docker").mkdir(parents=True)
    shutil.copy2(ROOT / "docker/check", repository / "docker/check")
    (repository / ".gitignore").write_text("build/\n")
    git = ["git", "-C", str(repository)]
    subprocess.run(
        git + ["init", "--initial-branch", "codex/check"], check=True, capture_output=True
    )
    subprocess.run(
        git + ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "add", "."],
        check=True,
    )
    subprocess.run(
        git
        + [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "Fixture source",
        ],
        check=True,
        capture_output=True,
    )
    sha = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    old = repository / "build/check"
    old.mkdir(parents=True)
    evidence = old / "original.txt"
    evidence.write_bytes(b"original frozen evidence")
    binary = tmp_path / "bin"
    binary.mkdir()
    fake = binary / "docker"
    calls = tmp_path / "calls"
    fake.write_text("""#!/usr/bin/env python3
import os,sys
from pathlib import Path
with Path(os.environ['CALLS']).open('a') as stream: stream.write(' '.join(sys.argv[1:])+'\\n')
if sys.argv[1:3] == ['image','inspect']:
    print('sha256:' + 'a'*64 + ' linux/amd64 ' + os.environ['SOURCE_SHA'])
elif sys.argv[1] != 'run': raise SystemExit('unexpected Docker call')
""")
    fake.chmod(0o755)
    environment = dict(
        os.environ,
        PATH=str(binary) + os.pathsep + os.environ["PATH"],
        CALLS=str(calls),
        SOURCE_SHA=sha,
    )
    command = [str(repository / "docker/check"), "fixture:image"]
    result = subprocess.run(command, env=environment, capture_output=True, text=True)
    assert result.returncode == 2 and "prior evidence" in result.stderr
    assert not calls.exists() and evidence.read_bytes() == b"original frozen evidence"
    new = repository / "build/another-check"
    subprocess.run(command + ["--output", str(new)], env=environment, check=True)
    before = calls.read_bytes()
    assert new.is_dir() and evidence.read_bytes() == b"original frozen evidence"
    result = subprocess.run(command + ["--output", str(new)], env=environment, capture_output=True)
    assert result.returncode == 2 and calls.read_bytes() == before

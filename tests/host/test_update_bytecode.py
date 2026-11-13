"""Normal advisory entry paths must neither write nor execute sibling bytecode."""

import hashlib
import importlib.machinery
import importlib.util
import json
import marshal
import os
import py_compile
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

import acquire
import artifacts
import pytest
from image_fixtures import classic_identity
from version import ROOT


def snapshot(root):
    return {
        str(path.relative_to(root)): (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            stat.S_IMODE(path.stat().st_mode),
        )
        for path in root.rglob("*")
        if path.is_file()
    }


def prepare(tmp_path, kind):
    runtime = tmp_path / "runtime"
    if kind == "bundle":
        files = artifacts.tooling_files(
            ROOT,
            "a" * 40,
            classic_identity("sha256:" + "b" * 64),
            {
                "filename": "unused-image.tar.gz",
                "sha256": "c" * 64,
                "bytes": 1,
                "download_url": "https://example.invalid/unused-image.tar.gz",
            },
        )
        acquire.materialize(files, runtime)
        scripts = runtime / "scripts"
        package = scripts / "ada_mcp"
    else:
        scripts = runtime / "tooling"
        package = runtime / "src/ada_mcp"
        scripts.mkdir(parents=True)
        package.mkdir(parents=True)
        for name in ["release_updates.py", "ada-mcp-launch"]:
            shutil.copy2(ROOT / "tooling" / name, scripts / name)
        for name in ["__init__.py", "_version.py", "update_notice.py"]:
            shutil.copy2(ROOT / "src/ada_mcp" / name, package / name)
        (scripts / "runtime-manifest.json").write_text(
            json.dumps({"project_version": "0.2.0-rc.1"})
        )
    return runtime, scripts, package


def poison(source, marker):
    """Seed a valid timestamp/size pyc while keeping the declared source untouched."""
    cache = Path(importlib.util.cache_from_source(str(source)))
    py_compile.compile(str(source), cfile=str(cache), doraise=True)
    header = cache.read_bytes()[:16]
    malicious = compile(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        "raise RuntimeError('unchecked bytecode executed')\n",
        str(source),
        "exec",
    )
    cache.write_bytes(header + marshal.dumps(malicious))
    # This control proves an ordinary loader would accept the poisoned cache.
    loaded = importlib.machinery.SourceFileLoader("_probe", str(source)).get_code("_probe")
    assert str(marker) in loaded.co_consts


def environment(tmp_path):
    return dict(
        os.environ,
        ADA_MCP_UPDATE_CACHE=str(tmp_path / "unused-explicit-cache"),
        HTTPS_PROXY="http://127.0.0.1:1",
        https_proxy="http://127.0.0.1:1",
        HTTP_PROXY="http://127.0.0.1:1",
        http_proxy="http://127.0.0.1:1",
        NO_PROXY="",
        no_proxy="",
        ALL_PROXY="",
        all_proxy="",
    )


def run(arguments, tmp_path, env):
    return subprocess.run(
        arguments, cwd=tmp_path, env=env, text=True, capture_output=True, check=True, timeout=6
    )


@pytest.mark.parametrize("kind", ["source", "bundle"])
@pytest.mark.parametrize("poisoned", [False, True])
def test_direct_status_fetch_child_and_launcher_are_source_only(tmp_path, kind, poisoned):
    runtime, scripts, package = prepare(tmp_path, kind)
    entry = scripts / "release_updates.py"
    marker = tmp_path / "unverified-bytecode-ran"
    if poisoned:
        for source in [
            entry,
            *(package / name for name in ["__init__.py", "_version.py", "update_notice.py"]),
        ]:
            poison(source, marker)
    expected = snapshot(runtime)
    env = environment(tmp_path)
    for channel in ["off", "auto"]:
        result = run(
            [
                sys.executable,
                "-I",
                str(entry),
                "status",
                "--channel",
                channel,
                "--cache",
                str(tmp_path / "unused-status-cache"),
            ],
            tmp_path,
            env,
        )
        assert json.loads(result.stdout)["status"] == (
            "disabled" if channel == "off" else "unknown"
        )
        assert snapshot(runtime) == expected and not marker.exists()

    # Run the actual synchronous fetch child. A closed loopback proxy prevents
    # external API access without substituting the child's import/startup path.
    program = (
        "from pathlib import Path\nimport json\n"
        f"source = Path({str(entry)!r})\n"
        "namespace = {'__name__': '_test_checker', '__file__': str(source)}\n"
        "exec(compile(source.read_bytes(), str(source), 'exec'), namespace)\n"
        "print(json.dumps(namespace['bounded_fetch']()))\n"
    )
    fetched = run([sys.executable, "-I", "-c", program], tmp_path, env)
    assert json.loads(fetched.stdout)["status"] == "offline"
    assert snapshot(runtime) == expected and not marker.exists()

    cache = tmp_path / "private-launch-cache"
    cache.mkdir(mode=0o700)
    now = int(time.time())
    state = {
        "schema": 1,
        "channel": "prerelease",
        "attempted_at": now,
        "checked_at": now,
        "next_check_at": now + 86400,
        "last_status": "ok",
        "complete": True,
        "candidate": "0.3.0",
    }
    (cache / "prerelease.json").write_text(json.dumps(state))
    (cache / "prerelease.json").chmod(0o600)
    binary = tmp_path / "bin"
    binary.mkdir()
    docker = binary / "docker"
    capture = tmp_path / "docker-arguments.json"
    docker.write_text(
        f"#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n"
        "if sys.argv[1:3] == ['image', 'inspect']:\n"
        "    print('linux/amd64' if 'Architecture' in sys.argv[4] else 'sha256:' + 'b'*64)\n"
        "elif sys.argv[1] == 'run':\n"
        f"    Path({str(capture)!r}).write_text(json.dumps(sys.argv[1:]))\n"
        "else: raise SystemExit('unexpected Docker invocation')\n"
    )
    docker.chmod(0o700)
    env["PATH"] = str(binary) + os.pathsep + env["PATH"]
    roots = tmp_path / "physical-projects"
    roots.mkdir()
    launched = run(
        [
            str(scripts / "ada-mcp-launch"),
            "--image",
            "fixture",
            "--root",
            str(roots),
            "--update-channel",
            "auto",
            "--update-cache",
            str(cache),
        ],
        tmp_path,
        env,
    )
    assert launched.stdout == ""
    payload = next(
        arg.split("=", 1)[1]
        for arg in json.loads(capture.read_text())
        if arg.startswith("ADA_MCP_UPDATE_NOTICE=")
    )
    assert json.loads(payload)["available_version"] == "0.3.0"
    assert snapshot(runtime) == expected and not marker.exists()
    assert not (tmp_path / "unused-status-cache").exists()


def test_updates_cli_ignores_a_valid_unverified_checker_cache(tmp_path):
    runtime, scripts, package = prepare(tmp_path, "bundle")
    marker = tmp_path / "unverified-bytecode-ran"
    for source in [scripts / "release_updates.py", package / "update_notice.py"]:
        poison(source, marker)
    expected = snapshot(runtime)
    result = run(
        [
            sys.executable,
            str(scripts / "ada_mcp_setup.py"),
            "updates",
            "status",
            "--channel",
            "off",
            "--cache",
            str(tmp_path / "unused-status-cache"),
        ],
        tmp_path,
        environment(tmp_path),
    )
    assert json.loads(result.stdout)["status"] == "disabled"
    assert snapshot(runtime) == expected and not marker.exists()

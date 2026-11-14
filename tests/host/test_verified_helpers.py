"""Installed CLI paths execute verified siblings, never unchecked bytecode."""

import hashlib
import json
import os
import subprocess
import sys
import tomllib

import acquire
import artifacts
import image_identity
import pytest
from image_fixtures import metadata_archive
from test_update_bytecode import environment, poison, snapshot
from version import ROOT


@pytest.fixture
def installed(tmp_path):
    incoming, config, target = metadata_archive()
    image = incoming.getvalue()
    cache = tmp_path / "private image cache"
    cache.mkdir(mode=0o700)
    archive = cache / "fixture-image.tar"
    archive.write_bytes(image)
    incoming.seek(0)
    identity = image_identity.archive_identity(incoming)
    record = {
        "filename": archive.name,
        "sha256": hashlib.sha256(image).hexdigest(),
        "bytes": len(image),
        "download_url": "https://example.invalid/fixture-image.tar",
    }
    files = artifacts.tooling_files(ROOT, "a" * 40, identity, record)
    runtime = tmp_path / "runtime"
    acquire.materialize(files, runtime)
    scripts = runtime / "scripts"
    roots = tmp_path / "physical projects"
    roots.mkdir()
    binding = tmp_path / "binding.json"
    binding.write_text(
        json.dumps(
            {
                "version": 2,
                "image_id": config,
                "image_identity": identity,
                "roots": [str(roots)],
                "docker_host": None,
                "docker_context": None,
                "uid": 1000,
                "gid": 1000,
                "image_source": None,
            }
        )
    )
    commands = tmp_path / "docker-commands.jsonl"
    binary = tmp_path / "bin"
    binary.mkdir()
    docker = binary / "docker"
    inspected = {"Id": target, "Os": "linux", "Architecture": "amd64", "Labels": {}}
    docker.write_text(
        f"#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n"
        f"with Path({str(commands)!r}).open('a') as stream: "
        "stream.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "if sys.argv[1:3] == ['image','inspect']:\n"
        "    template = sys.argv[sys.argv.index('--format')+1]\n"
        f"    result = {inspected!r}\n"
        "    print('linux/amd64' if template == '{{.Os}}/{{.Architecture}}' "
        "else result['Id'] if template == '{{.Id}}' else json.dumps(result))\n"
        "elif sys.argv[1:3] == ['container','inspect']:\n"
        "    print('No such object: '+sys.argv[-1],file=sys.stderr); raise SystemExit(1)\n"
        "elif sys.argv[1:3] == ['image','save']:\n"
        f"    sys.stdout.buffer.write(Path({str(archive)!r}).read_bytes())\n"
        "elif sys.argv[1] == 'run' or sys.argv[1:3] == ['image','load']:\n"
        "    print('controlled fixture stop',file=sys.stderr); raise SystemExit(70)\n"
        "else: raise SystemExit('unexpected Docker command')\n"
    )
    docker.chmod(0o700)
    env = environment(tmp_path)
    env.update(PATH=str(binary) + os.pathsep + env["PATH"], ADA_MCP_UPDATE_CHANNEL="off")
    return {
        "runtime": runtime,
        "scripts": scripts,
        "binding": binding,
        "roots": roots,
        "cache": cache,
        "commands": commands,
        "env": env,
        "config": config,
        "target": target,
    }


def run(installed, arguments, tmp_path):
    return subprocess.run(
        arguments,
        env=installed["env"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=10,
    )


@pytest.mark.parametrize(
    "command,helper",
    [
        ("updates", "image_identity"),
        ("native-config", "mcp_client"),
        ("doctor", "mcp_client"),
        ("query", "mcp_client"),
        ("bootstrap", "acquire"),
        ("export", "image_identity"),
        ("smoke-help", "ada_mcp_setup"),
    ],
)
def test_real_entry_paths_ignore_valid_sibling_bytecode(installed, tmp_path, command, helper):
    scripts = installed["scripts"]
    marker = tmp_path / "unchecked-bytecode-ran"
    poison(scripts / (helper + ".py"), marker)
    if command == "smoke-help":
        poison(scripts / "mcp_client.py", marker)
    expected = snapshot(installed["runtime"])
    base = [sys.executable, str(scripts / "ada_mcp_setup.py")]
    binding = ["--binding", str(installed["binding"])]
    if command == "updates":
        arguments = base + [
            "updates",
            "status",
            "--channel",
            "off",
            "--cache",
            str(tmp_path / "unused"),
        ]
    elif command == "native-config":
        arguments = base + [command, *binding, "--output", str(tmp_path / "native.toml")]
    elif command == "doctor":
        arguments = base + [command, *binding, "--output", str(tmp_path / "new-doctor")]
    elif command == "query":
        arguments = base + [command, *binding, "--log-dir", str(tmp_path / "new-query"), "tools"]
    elif command == "bootstrap":
        arguments = base + [
            command,
            "--binding",
            str(tmp_path / "new-binding.json"),
            "--root",
            str(installed["roots"]),
            "--uid",
            "1000",
            "--gid",
            "1000",
            "--image-cache",
            str(installed["cache"]),
        ]
    elif command == "smoke-help":
        arguments = [sys.executable, str(scripts / "mac_smoke.py"), "--help"]
    else:
        setup_source = scripts / "ada_mcp_setup.py"
        program = (
            "from pathlib import Path\nimport os,json\n"
            f"source=Path({str(setup_source)!r})\n"
            "ns={'__name__':'_test_setup','__file__':str(source)}\n"
            "exec(compile(source.read_bytes(),str(source),'exec'),ns)\n"
            "ns['verified_manifest']()\n"
            f"result=ns['exported_identity'](['docker'],dict(os.environ),{installed['target']!r},"
            f"{installed['config']!r},{{}},2)\nprint(json.dumps(result))\n"
        )
        arguments = [sys.executable, "-I", "-c", program]
    result = run(installed, arguments, tmp_path)
    assert not marker.exists(), result.stdout + result.stderr
    assert snapshot(installed["runtime"]) == expected
    if command in {"updates", "native-config", "export", "smoke-help"}:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode == 1, result.stdout + result.stderr
        calls = [json.loads(line) for line in installed["commands"].read_text().splitlines()]
        assert any(call[0] == "run" or call[:2] == ["image", "load"] for call in calls)
    if command == "updates":
        assert json.loads(result.stdout)["status"] == "disabled"
    elif command == "bootstrap":
        report = json.loads(result.stdout)
        assert report["download"]["cache_hit"] is True
        assert report["archive"]["image_validation"]["verified_before_load"] is True
    elif command == "export":
        assert json.loads(result.stdout)["image_id"] == installed["config"]


def test_late_helpers_use_the_exact_bytes_checked_by_manifest(installed, tmp_path):
    scripts = installed["scripts"]
    marker = tmp_path / "changed-source-ran"
    program = (
        "from pathlib import Path\nimport json\n"
        f"source=Path({str(scripts / 'ada_mcp_setup.py')!r})\n"
        "ns={'__name__':'_test_setup','__file__':str(source)}\n"
        "exec(compile(source.read_bytes(),str(source),'exec'),ns)\n"
        "ns['verified_manifest']()\n"
        f"bad=\"from pathlib import Path\\nPath({str(marker)!r}).write_text('executed')\\n\"\n"
        f"Path({str(scripts / 'acquire.py')!r}).write_text(bad)\n"
        f"Path({str(scripts / 'mcp_client.py')!r}).write_text(bad)\n"
        f"Path({str(scripts / 'ada_mcp/update_notice.py')!r}).write_text(bad)\n"
        "assert 'ada_project_info' in ns['load_helper']('mcp_client')['READ_TOOLS']\n"
        "assert callable(ns['load_helper']('acquire')['download_file'])\n"
        f"cache=Path({str(tmp_path / 'unused-cache')!r})\n"
        "result=ns['load_helper']('release_updates')['check_updates']('0.2.0','off',cache)\n"
        "assert result['status'] == 'disabled'\n"
        "print(json.dumps({'retained_source_used':True}))\n"
    )
    result = run(installed, [sys.executable, "-I", "-c", program], tmp_path)
    assert result.returncode == 0 and not marker.exists(), result.stdout + result.stderr


@pytest.mark.parametrize("command", ["native-config", "query"])
def test_relative_cache_is_rejected_before_any_output_or_launch(installed, tmp_path, command):
    output = tmp_path / "uncreated-parent/native.toml"
    logs = tmp_path / "uncreated-query-logs"
    arguments = [
        sys.executable,
        str(installed["scripts"] / "ada_mcp_setup.py"),
        command,
        "--binding",
        str(installed["binding"]),
        "--update-channel",
        "off",
        "--update-cache",
        "relative/cache",
    ]
    arguments += (
        ["--output", str(output)]
        if command == "native-config"
        else ["--log-dir", str(logs), "tools"]
    )
    result = run(installed, arguments, tmp_path)
    assert result.returncode == 1
    assert "must be absolute" in json.loads(result.stdout)["error"]
    assert not output.parent.exists() and not logs.exists() and not installed["commands"].exists()
    if command == "native-config":
        output.parent.mkdir()
        output.write_bytes(b"preserve existing config")
        repeated = run(installed, arguments, tmp_path)
        assert repeated.returncode == 1 and output.read_bytes() == b"preserve existing config"
        assert not installed["commands"].exists()


@pytest.mark.parametrize("cache", [None, "private Ω cache"])
def test_native_absolute_or_unspecified_cache_keeps_no_replace(installed, tmp_path, cache):
    output = tmp_path / "native.toml"
    arguments = [
        sys.executable,
        str(installed["scripts"] / "ada_mcp_setup.py"),
        "native-config",
        "--binding",
        str(installed["binding"]),
        "--output",
        str(output),
    ]
    if cache:
        arguments += ["--update-cache", str(tmp_path / cache)]
    result = run(installed, arguments, tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    fragment = tomllib.loads(output.read_text())["mcp_servers"]["ada"]["args"]
    if cache:
        assert fragment[fragment.index("--update-cache") + 1] == str(tmp_path / cache)
    else:
        assert "--update-cache" not in fragment
    saved = output.read_bytes()
    assert run(installed, arguments, tmp_path).returncode == 1
    assert output.read_bytes() == saved


def test_implicit_advisory_failure_does_not_reject_launch(installed, tmp_path):
    installed["env"].update(ADA_MCP_UPDATE_CHANNEL="auto", ADA_MCP_UPDATE_CACHE="relative/cache")
    result = run(
        installed,
        [
            "/bin/bash",
            str(installed["scripts"] / "ada-mcp-launch"),
            "--image",
            installed["target"],
            "--root",
            str(installed["roots"]),
        ],
        tmp_path,
    )
    assert result.returncode == 70 and "controlled fixture stop" in result.stderr
    assert any(
        json.loads(line)[0] == "run" for line in installed["commands"].read_text().splitlines()
    )


def test_direct_query_client_rejects_relative_cache_before_logs(installed, tmp_path):
    logs = tmp_path / "uncreated-client-logs"
    result = run(
        installed,
        [
            sys.executable,
            str(installed["scripts"] / "mcp_client.py"),
            "--image",
            installed["target"],
            "--root",
            str(installed["roots"]),
            "--update-cache",
            "relative/cache",
            "--update-channel",
            "off",
            "--log-dir",
            str(logs),
            "tools",
        ],
        tmp_path,
    )
    assert result.returncode == 1
    assert "must be absolute" in json.loads(result.stderr)["error"]
    assert not logs.exists() and not installed["commands"].exists()


@pytest.mark.parametrize("cache", [None, "private Ω cache"])
def test_valid_query_options_reach_controlled_runtime(installed, tmp_path, cache):
    logs = tmp_path / "query-logs"
    arguments = [
        sys.executable,
        str(installed["scripts"] / "ada_mcp_setup.py"),
        "query",
        "--binding",
        str(installed["binding"]),
        "--update-channel",
        "off",
        "--log-dir",
        str(logs),
    ]
    if cache:
        arguments += ["--update-cache", str(tmp_path / cache)]
    result = run(installed, arguments + ["tools"], tmp_path)
    assert result.returncode == 1 and logs.is_dir()
    launched = json.loads((logs / "command.json").read_text())
    if cache:
        assert launched[launched.index("--update-cache") + 1] == str(tmp_path / cache)
    else:
        assert "--update-cache" not in launched
    assert any(
        json.loads(line)[0] == "run" for line in installed["commands"].read_text().splitlines()
    )


def test_unlisted_sibling_is_not_executed_as_a_contributor_fallback(installed, tmp_path):
    scripts = installed["scripts"]
    source = scripts / "mcp_client.py"
    marker = tmp_path / "unlisted-source-ran"
    source.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n")
    manifest_path = scripts / "runtime-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files_sha256"].pop("scripts/mcp_client.py")
    manifest_path.write_text(json.dumps(manifest))
    result = run(
        installed,
        [
            sys.executable,
            str(scripts / "ada_mcp_setup.py"),
            "native-config",
            "--binding",
            str(installed["binding"]),
            "--output",
            str(tmp_path / "native.toml"),
        ],
        tmp_path,
    )
    assert result.returncode == 1 and not marker.exists()
    assert "has not been verified" in json.loads(result.stdout)["error"]

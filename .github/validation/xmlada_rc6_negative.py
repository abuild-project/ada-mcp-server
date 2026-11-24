#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run an isolated, immutable RC6 negative control without candidate runtime imports."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

SHA = "2872442e1963f1b9c00ffb1eb84bac7f7163aeb5"
REPOSITORY = "ghcr.io/abuild-project/ada-mcp-server"
IMAGE = REPOSITORY + "@sha256:af17ec11ae84c0822acce981454f0d45563a1f05587e18ee30c6a69d3b1ec674"
CONFIG = "sha256:f062a9bd43ef549b63d4a363b36ed7ca3c1aa24aa7a12286a6cd762e62cc3893"
RC6_SOURCE = "876602d264dd4e468b294847360a0ea201128008"


def hashes(root: Path) -> dict[str, str]:
    """Hash the mounted fixture's exact regular input files."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def execute(argv: list[str], **options: Any) -> subprocess.CompletedProcess[str]:
    """Bound a command while preserving its streams for the caller."""
    return subprocess.run(argv, text=True, capture_output=True, timeout=300, **options)


def inside() -> None:
    """Require an actual MCP missing-import failure before any package oracle."""
    output = Path("/evidence")
    fixture = Path("/committed-harness/tests/fixtures/xmlada_project")
    inputs = hashes(fixture)
    assert os.getuid() != 0
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment.pop("GPR_PROJECT_PATH", None)
    command = [
        sys.executable,
        "-B",
        "/committed-harness/scripts/real_xmlada.py",
        "--output",
        "/evidence/control",
    ]
    run = execute(command, env=environment)
    (output / "harness-stdout.log").write_text(run.stdout)
    (output / "harness-stderr.log").write_text(run.stderr)
    summary = json.loads((output / "control/summary.json").read_text())
    assert run.returncode != 0 and summary["status"] == "failed"
    assert summary["failure_stage"] == "select-project"
    assert summary["eof_exit"] == 0 and "cleanup_error" not in summary
    assert "initialize" in summary and len(summary["calls"]) == 1
    assert "package_files" not in summary and "expected_source" not in summary
    assert inputs == summary["input_sha256"] == summary["input_sha256_after"]
    assert inputs == summary["committed_input_sha256_after"]
    messages = []
    for line in (output / "control/mcp/protocol.jsonl").read_text().splitlines():
        message = json.loads(line)["message"]
        messages.append(json.loads(message) if isinstance(message, str) else message)
    initialized = [item for item in messages if item.get("method") == "initialize"]
    assert len(initialized) == 1
    initialize_reply = next(
        item for item in messages if item.get("id") == initialized[0]["id"] and "result" in item
    )
    assert initialize_reply["result"] == summary["initialize"]
    requests = [item for item in messages if item.get("method") == "tools/call"]
    assert len(requests) == 1
    request = requests[0]
    arguments = request["params"]["arguments"]
    assert request["params"]["name"] == "ada_project_info"
    assert arguments == {
        "gpr_file": "/evidence/control/fixture/xmlada_probe.gpr",
        "project_paths": [],
        "scenario_variables": {},
    }
    reply = next(item for item in messages if item.get("id") == request["id"] and "result" in item)
    payload = json.loads(
        next(item["text"] for item in reply["result"]["content"] if item.get("type") == "text")
    )
    (output / "raw-project-reply.json").write_text(json.dumps(reply, indent=2) + "\n")
    assert payload["complete"] is False and payload["reason"] == "project-load-failed"
    compiler = execute(
        [
            "gprbuild",
            "-P",
            arguments["gpr_file"],
            "-p",
            "-c",
            "-u",
            "xmlada_probe.adb",
        ],
        cwd=output / "control/fixture",
        env=environment,
    )
    package_command = ["dpkg-query", "-L"] + [
        "libxmlada-" + name + "-dev" for name in ("schema", "dom", "sax", "input", "unicode")
    ]
    package = execute(package_command)
    observation = {
        "harness_exit": run.returncode,
        "project_payload": payload,
        "compiler": {
            "exit_code": compiler.returncode,
            "stdout": compiler.stdout,
            "stderr": compiler.stderr,
        },
        "package": {
            "argv": package_command,
            "exit_code": package.returncode,
            "stdout": package.stdout,
            "stderr": package.stderr,
        },
        "uid": os.getuid(),
        "gid": os.getgid(),
        "input_sha256": inputs,
    }
    (output / "negative-observation.json").write_text(json.dumps(observation, indent=2) + "\n")
    assert compiler.returncode != 0
    assert 'imported project file "xmlada" not found' in compiler.stderr
    assert not (output / "control/fixture/obj/xmlada_probe.ali").exists()
    assert package.returncode != 0 and not package.stdout
    assert not Path("/usr/share/gpr/xmlada.gpr").exists()
    assert hashes(fixture) == inputs
    assert all(
        hashlib.sha256((output / "control/fixture" / name).read_bytes()).hexdigest() == digest
        for name, digest in inputs.items()
    )
    installed = execute([sys.executable, "-I", "-c", "import ada_mcp;print(ada_mcp.__file__)"])
    assert installed.returncode == 0 and installed.stdout.strip().startswith("/opt/ada-mcp/venv/")
    survivors = []
    for path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            parts = path.read_bytes().split(b"\0")
        except (FileNotFoundError, ProcessLookupError):
            continue
        if parts and (
            Path(os.fsdecode(parts[0])).name == "ada_language_server" or b"ada_mcp" in parts
        ):
            survivors.append(str(path.parent))
    assert not survivors, survivors
    observation.update(
        initialize=summary["initialize"],
        installed_module=installed.stdout.strip(),
        inputs_unchanged=True,
        server_eof_exit=summary["eof_exit"],
        remaining_processes=survivors,
        passed=True,
    )
    (output / "negative-observation.json").write_text(json.dumps(observation, indent=2) + "\n")
    print(json.dumps(observation, indent=2))


def outside(source: Path, output: Path) -> None:
    """Verify public RC6 identity and retain container evidence on every outcome."""
    assert execute(["git", "-C", str(source), "rev-parse", "HEAD"]).stdout.strip() == SHA
    assert not execute(["git", "-C", str(source), "status", "--porcelain"]).stdout
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    pull = execute(["docker", "pull", "--platform", "linux/amd64", IMAGE])
    (output / "pull.log").write_text(pull.stdout + pull.stderr)
    assert pull.returncode == 0
    reference, manifests = IMAGE, []
    for _ in range(3):
        inspected = execute(["docker", "buildx", "imagetools", "inspect", "--raw", reference])
        assert inspected.returncode == 0, inspected.stderr
        manifest = json.loads(inspected.stdout)
        manifests.append({"reference": reference, "manifest": manifest})
        if "config" in manifest:
            assert manifest["config"]["digest"] == CONFIG
            break
        candidates = [
            item
            for item in manifest["manifests"]
            if item.get("platform", {}).get("os") == "linux"
            and item.get("platform", {}).get("architecture") == "amd64"
        ]
        assert len(candidates) == 1
        reference = REPOSITORY + "@" + candidates[0]["digest"]
    else:
        raise AssertionError("no authenticated AMD64 runtime config")
    (output / "registry-identity.json").write_text(json.dumps(manifests, indent=2) + "\n")
    template = (
        '{"id":{{json .Id}},"os":{{json .Os}},'
        '"architecture":{{json .Architecture}},'
        '"source":{{json (index .Config.Labels "org.opencontainers.image.revision")}}}'
    )
    image = execute(["docker", "image", "inspect", "--format", template, IMAGE])
    assert image.returncode == 0, image.stderr
    identity = json.loads(image.stdout)
    assert identity["os"] == "linux" and identity["architecture"] == "amd64"
    assert identity["source"] == RC6_SOURCE
    (output / "image-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    name = "xmlada-rc6-negative-" + uuid.uuid4().hex
    uid, gid = os.getuid(), os.getgid()
    assert uid != 0
    command = [
        "docker",
        "run",
        "--rm",
        "--name",
        name,
        "--platform",
        "linux/amd64",
        "--network",
        "none",
        "--read-only",
        "--user",
        f"{uid}:{gid}",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--env",
        "PYTHONPATH=",
        "--env",
        "GPR_PROJECT_PATH=",
        "--env",
        "ADA_MCP_UPDATE_CHANNEL=off",
        "--tmpfs",
        "/tmp:rw,nosuid,nodev,noexec",
        "--tmpfs",
        f"/home/ada-mcp:rw,nosuid,nodev,uid={uid},gid={gid},mode=0700",
    ]
    for origin, target in [
        (source / "scripts", "/committed-harness/scripts"),
        (source / "tooling/mcp_client.py", "/committed-harness/tooling/mcp_client.py"),
        (
            source / "tests/fixtures/xmlada_project",
            "/committed-harness/tests/fixtures/xmlada_project",
        ),
        (Path(__file__).resolve(), "/validation-driver.py"),
    ]:
        command += ["--mount", f"type=bind,src={origin},dst={target},readonly"]
    command += [
        "--mount",
        f"type=bind,src={output},dst=/evidence",
        "--entrypoint",
        "/opt/ada-mcp/venv/bin/python",
        IMAGE,
        "-I",
        "-B",
        "/validation-driver.py",
        "--inside",
    ]
    (output / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    try:
        result = execute(command)
        (output / "container-stdout.log").write_text(result.stdout)
        (output / "container-stderr.log").write_text(result.stderr)
        assert result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired as error:
        for label, stream in (("stdout", error.stdout), ("stderr", error.stderr)):
            text = stream.decode(errors="replace") if isinstance(stream, bytes) else stream or ""
            (output / ("container-" + label + ".log")).write_text(text)
        raise
    finally:
        remaining = execute(
            ["docker", "container", "inspect", "--format", "{{.Config.Image}}", name]
        )
        if remaining.returncode == 0:
            assert remaining.stdout.strip() == IMAGE
            execute(["docker", "rm", "--force", name])
        absent = execute(["docker", "container", "inspect", name])
        cleanup = {"name": name, "exit_code": absent.returncode, "stderr": absent.stderr}
        (output / "cleanup.json").write_text(json.dumps(cleanup, indent=2) + "\n")
        assert absent.returncode != 0 and name in absent.stderr
    print((output / "negative-observation.json").read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inside", action="store_true")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    if options.inside:
        inside()
    else:
        assert options.source is not None and options.output is not None
        outside(options.source.resolve(), options.output.resolve())

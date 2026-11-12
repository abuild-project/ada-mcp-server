#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run an actual macOS smoke test of the shared launcher and MCP server."""

import argparse
import json
import os
import platform
import subprocess
import uuid
from pathlib import Path
from typing import Any

from mcp_client import Session, add_launch_arguments, create_private_directory, launcher_command

JSON = dict[str, Any]


def require(condition: object, message: str) -> None:
    """Keep checks active even when Python is started with optimization."""
    if not condition:
        raise RuntimeError(message)


def docker_binding(options: argparse.Namespace) -> tuple[list[str], dict[str, str]]:
    """Match the launcher's host/context selection without changing Docker settings."""
    command = ["docker"]
    environment = dict(os.environ)
    if options.docker_host or options.docker_context:
        for key in [
            "DOCKER_HOST",
            "DOCKER_CONTEXT",
            "DOCKER_TLS",
            "DOCKER_TLS_VERIFY",
            "DOCKER_CERT_PATH",
        ]:
            environment.pop(key, None)
        if options.docker_host:
            command.extend(["--host", options.docker_host])
        else:
            command.extend(["--context", options.docker_context])
    return command, environment


def run(
    command: list[str], environment: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Capture one explicit local command without invoking a shell."""
    return subprocess.run(command, env=environment, text=True, capture_output=True, check=True)


def inspect_container(
    command: list[str], environment: dict[str, str], name: str, observations: list[JSON]
) -> JSON | None:
    """Return an exact container, proving absence or failing on unknown state."""
    argv = command + ["container", "inspect", name]
    observation: JSON = {
        "argv": argv,
        "name": name,
        "status": "unknown",
        "rc": None,
        "stdout": "",
        "stderr": "",
    }
    observations.append(observation)
    try:
        result = subprocess.run(argv, env=environment, text=True, capture_output=True)
        observation.update(rc=result.returncode, stdout=result.stdout, stderr=result.stderr)
        if result.returncode == 0:
            states: list[JSON] = json.loads(result.stdout)
            require(
                isinstance(states, list)
                and len(states) == 1
                and isinstance(states[0], dict)
                and states[0].get("Name") == "/" + name,
                "Docker inspect did not return the exact requested container",
            )
            observation["status"] = "present"
            return states[0]
        # Docker's missing-object response is the only nonzero result that
        # establishes absence. Unknown CLI/daemon/context/permission errors fail.
        missing_messages = {
            prefix + kind + name
            for prefix in ["", "Error: ", "Error response from daemon: "]
            for kind in ["No such container: ", "No such object: "]
        }
        if (
            result.returncode == 1
            and result.stdout.strip() in ["", "[]"]
            and result.stderr.strip() in missing_messages
        ):
            observation["status"] = "absent-confirmed"
            return None
        raise RuntimeError(
            "Docker container state is unknown (inspect rc="
            + str(result.returncode)
            + "): "
            + result.stderr.strip()
        )
    except Exception as error:
        observation["error"] = type(error).__name__ + ": " + str(error)
        raise


def read_cases(path: str) -> list[JSON]:
    """Load test inputs; these are not a required project configuration format."""
    cases: list[JSON] = json.loads(Path(path).read_text())
    require(isinstance(cases, list) and len(cases) >= 2, "provide at least two project cases")
    projects = set()
    for case in cases:
        require(isinstance(case, dict), "each case must be an object")
        require(
            set(case)
            == {
                "gpr_file",
                "project_paths",
                "scenario_variables",
                "anchor",
                "query",
                "expected_symbol_file",
            },
            "case fields must match smoke-cases.example.json",
        )
        for key in ["gpr_file", "anchor", "expected_symbol_file"]:
            require(
                isinstance(case[key], str)
                and Path(case[key]).is_absolute()
                and Path(case[key]).is_file(),
                key + " must be an existing absolute file",
            )
        require(
            isinstance(case["project_paths"], list)
            and all(
                isinstance(p, str) and Path(p).is_absolute() and Path(p).is_dir()
                for p in case["project_paths"]
            ),
            "project_paths must be existing absolute directories",
        )
        require(
            isinstance(case["scenario_variables"], dict)
            and all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in case["scenario_variables"].items()
            ),
            "scenario_variables must map strings to strings",
        )
        require(isinstance(case["query"], str) and bool(case["query"]), "query must be nonempty")
        require(
            case["query"].lower() in Path(case["expected_symbol_file"]).read_text().lower(),
            "expected symbol must occur in the independent source file",
        )
        projects.add(str(Path(case["gpr_file"]).resolve()))
    require(len(projects) >= 2, "cases must select at least two distinct GPR files")
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_launch_arguments(parser)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--output", required=True, help="new evidence directory; must not exist")
    options = parser.parse_args()
    if platform.system() != "Darwin":
        parser.error("this packet requires a real macOS host; Linux cannot supply Mac evidence")
    if options.name or options.log_dir:
        parser.error("the smoke packet owns its unique container name and output logs")
    if options.timeout <= 0:
        parser.error("--timeout must be positive")
    options.name = "ada-mcp-mac-smoke-" + uuid.uuid4().hex
    options.log_dir = None
    output = Path(options.output)
    owns_output = False
    session = None
    problem = None
    report: JSON = {
        "status": "failed",
        "container_name": options.name,
        "host_system": platform.system(),
        "host_machine": platform.machine(),
        "caller_uid": os.getuid(),
        "caller_gid": os.getgid(),
        "container_inspections": [],
    }
    docker, environment = docker_binding(options)
    image_id = None
    try:
        cases = read_cases(options.cases)
        create_private_directory(output)
        owns_output = True
        # Exercise Apple's system Bash explicitly, even if Homebrew Bash is on PATH.
        command = ["/bin/bash"] + launcher_command(options)
        check = run(command + ["--check"])
        (output / "launcher-check.txt").write_text(check.stdout)
        image_id = dict(line.split("=", 1) for line in check.stdout.splitlines())["image"]
        require(
            inspect_container(docker, environment, options.name, report["container_inspections"])
            is None,
            "the generated container name already exists",
        )
        report["image_id"] = image_id
        report["docker_version"] = json.loads(
            run(docker + ["version", "--format", "{{json .}}"], environment).stdout
        )
        report["system_bash"] = run(["/bin/bash", "--version"]).stdout
        (output / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
        session = Session(command, options.timeout, output / "mcp")
        report["initialize"] = session.initialize()
        catalog = session.tools()
        names = {tool["name"] for tool in catalog}
        require(
            {"ada_project_info", "ada_workspace_symbols", "ada_diagnostics"} <= names,
            "required real server tools are missing",
        )
        (output / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
        state = inspect_container(
            docker, environment, options.name, report["container_inspections"]
        )
        require(state is not None and state["Image"] == image_id, "running image identity mismatch")
        assert state is not None
        require(
            state["Config"]["Labels"].get("ada-mcp-generic") == "1", "launcher label is missing"
        )
        require(state["HostConfig"]["ReadonlyRootfs"] is True, "root filesystem is writable")
        require(state["HostConfig"]["NetworkMode"] == "none", "container network is enabled")
        (output / "container.json").write_text(json.dumps(state, indent=2) + "\n")
        probe = (
            "import json,os,platform; print(json.dumps(dict(uid=os.getuid(),gid=os.getgid(),"
            'machine=platform.machine(),os_release=open("/etc/os-release").read(),'
            'home_writable=os.access(os.environ["HOME"],os.W_OK))))'
        )
        runtime = json.loads(
            run(docker + ["exec", state["Id"], "python", "-c", probe], environment).stdout
        )
        require(
            runtime["uid"] == (options.uid if options.uid is not None else os.getuid()) != 0,
            "runtime UID does not match the selected nonroot identity",
        )
        require(
            runtime["gid"] == (options.gid if options.gid is not None else os.getgid()) != 0,
            "runtime GID does not match the selected nonroot identity",
        )
        require(
            runtime["machine"] == "x86_64" and "VERSION_CODENAME=trixie" in runtime["os_release"],
            "runtime is not AMD64 Trixie",
        )
        require(runtime["home_writable"], "private HOME is not writable by the runtime identity")
        report["runtime"] = runtime
        results = []
        for case in cases:
            info = session.call(
                "ada_project_info",
                {key: case[key] for key in ["gpr_file", "project_paths", "scenario_variables"]},
            )
            require(
                info.get("complete") is True
                and Path(info["project_file"]).resolve() == Path(case["gpr_file"]).resolve(),
                "project selection was incomplete or selected the wrong GPR",
            )
            symbols = session.call(
                "ada_workspace_symbols",
                {"file": case["anchor"], "query": case["query"], "kind": "all", "limit": 100},
            )
            require(
                symbols.get("complete") is True and not symbols.get("truncated"),
                "symbol index is incomplete or truncated",
            )
            require(
                any(
                    Path(item["file"]).resolve() == Path(case["expected_symbol_file"]).resolve()
                    and case["query"].lower() in item["name"].lower()
                    for item in symbols.get("symbols", [])
                ),
                "expected source-bound symbol was not found",
            )
            diagnostics = session.call(
                "ada_diagnostics", {"file": case["anchor"], "severity": "all"}
            )
            require(
                diagnostics.get("complete") is True and diagnostics.get("scope") == "file",
                "diagnostics were incomplete or came from the unscoped cache",
            )
            results.append(
                {"case": case, "project": info, "symbols": symbols, "diagnostics": diagnostics}
            )
        (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        report["status"] = "passed-container-and-stdio-smoke"
        report["native_desktop_binding"] = "not tested by this script; use the README manual step"
    except Exception as error:
        problem = type(error).__name__ + ": " + str(error)
    finally:
        if session is not None:
            try:
                session.close()
            except Exception as error:
                problem = problem or type(error).__name__ + ": " + str(error)
        if session is not None:
            try:
                state = inspect_container(
                    docker, environment, options.name, report["container_inspections"]
                )
                if state is None:
                    report["cleanup_status"] = "absent-confirmed"
                elif any(item["status"] == "unknown" for item in report["container_inspections"]):
                    report["cleanup_status"] = "unknown-no-removal"
                    problem = problem or "container state was unknown; explicit cleanup refused"
                elif (
                    state["Image"] == image_id
                    and state["Config"].get("Labels", {}).get("ada-mcp-generic") == "1"
                ):
                    try:
                        run(docker + ["container", "rm", "-f", state["Id"]], environment)
                        report["forced_owned_container_cleanup"] = state["Id"]
                        report["cleanup_status"] = "remaining-owned-container-removed"
                        problem = problem or "server did not remove its container on STDIN EOF"
                    except Exception as error:
                        report["cleanup_status"] = "owned-removal-failed"
                        problem = problem or "owned container cleanup failed: " + str(error)
                else:
                    report["cleanup_status"] = "identity-mismatch-no-removal"
                    problem = problem or "container identity changed; cleanup refused"
            except Exception as error:
                report["cleanup_status"] = "unknown-no-removal"
                report["cleanup_error"] = type(error).__name__ + ": " + str(error)
                problem = problem or "cannot verify container cleanup: " + report["cleanup_error"]
        else:
            report["cleanup_status"] = "not-started"
        if problem:
            report["status"] = "failed"
            report["error"] = problem
        if owns_output:
            (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 1 if problem else 0


if __name__ == "__main__":
    raise SystemExit(main())

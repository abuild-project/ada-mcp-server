#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require actual error/repair/error publications in one MCP and ALS process."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from mcp_client import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
JSON = dict[str, Any]
PROC_ROOT = Path("/proc")
BROKEN = "procedure Main is\n Value : Integer := ;\nbegin\n null;\nend Main;\n"
REPAIRED = "procedure Main is\n Value : Integer := 42;\nbegin\n null;\nend Main;\n"


def require_state(result: JSON, source: Path, expect_errors: bool) -> None:
    """Reject empty/stale caches and tie reported syntax errors to actual text."""
    if result.get("complete") is not True or result.get("scope") != "file":
        raise AssertionError("diagnostics must be a complete file publication")
    diagnostics = result.get("diagnostics")
    if not isinstance(diagnostics, list):
        raise AssertionError("diagnostics must be a list")
    if not expect_errors:
        if diagnostics or result.get("errorCount") != 0 or result.get("totalCount") != 0:
            raise AssertionError("the repaired source must clear the diagnostic publication")
        return
    if result.get("errorCount", 0) <= 0 or not diagnostics:
        raise AssertionError("the malformed source must produce nonempty syntax errors")
    line = source.read_text().splitlines()[1]
    matches = []
    for item in diagnostics:
        if (
            item.get("file") == str(source)
            and item.get("line") == 2
            and item.get("severity") == "error"
            and item.get("endLine") == 2
        ):
            start, end = item.get("column", 0), item.get("endColumn", 0)
            if (
                isinstance(start, int)
                and isinstance(end, int)
                and 1 <= start < end <= len(line) + 1
                and line[start - 1 : end - 1] == ";"
                and ";" in item.get("message", "")
            ):
                matches.append(item)
    if not matches:
        raise AssertionError("syntax-error message/location must identify the source semicolon")


class ProcessIdentity(TypedDict):
    """Core procfs identity fields, independent of optional task children files."""

    pid: int
    parent_pid: int
    start_ticks: int
    state: str


def read_identity(directory: Path) -> ProcessIdentity:
    """Parse core Linux stat fields, allowing parentheses inside the comm field."""
    record = (directory / "stat").read_text()
    pid_text, opening, remainder = record.partition(" (")
    _, closing, tail = remainder.rpartition(") ")
    fields = tail.split()
    if not opening or not closing or len(fields) < 20:
        raise RuntimeError("invalid Linux process identity record")
    try:
        pid, parent, started = int(pid_text), int(fields[1]), int(fields[19])
    except ValueError as error:
        raise RuntimeError("invalid numeric Linux process identity") from error
    if (
        pid != int(directory.name)
        or pid <= 0
        or parent < 0
        or started <= 0
        or fields[0] not in {"R", "S", "D", "T", "t", "K", "W", "P", "I", "Z", "X", "x"}
    ):
        raise RuntimeError("invalid Linux process identity fields")
    return {"pid": pid, "parent_pid": parent, "start_ticks": started, "state": fields[0]}


def observe_process_pair(server_pid: int, program: str, proc_root: Path | None = None) -> JSON:
    """Identify one live direct child and reject changed, missing or ambiguous identities."""
    root = proc_root or PROC_ROOT
    server = read_identity(root / str(server_pid))
    if server["state"] in {"Z", "X", "x"}:
        raise RuntimeError("MCP process is not live")
    candidates = []
    for directory in root.iterdir():
        if not directory.name.isdigit():
            continue
        try:
            child = read_identity(directory)
        except FileNotFoundError:
            continue
        if child["parent_pid"] != server_pid:
            continue
        command = (directory / "cmdline").read_bytes().split(b"\0")[0]
        if Path(os.fsdecode(command)).name != program:
            continue
        if child["state"] in {"Z", "X", "x"}:
            raise RuntimeError("Ada Language Server child is not live")
        after = read_identity(directory)
        if (after["pid"], after["parent_pid"], after["start_ticks"]) != (
            child["pid"],
            child["parent_pid"],
            child["start_ticks"],
        ) or after["state"] in {"Z", "X", "x"}:
            raise RuntimeError("Ada Language Server identity changed during observation")
        candidates.append(child)
    if len(candidates) != 1:
        raise RuntimeError("expected one observable Ada Language Server child")
    after_server = read_identity(root / str(server_pid))
    if (after_server["pid"], after_server["start_ticks"]) != (
        server["pid"],
        server["start_ticks"],
    ) or after_server["state"] in {"Z", "X", "x"}:
        raise RuntimeError("MCP identity changed during observation")
    child = candidates[0]
    return {
        "mcp_pid": server_pid,
        "mcp_start_ticks": server["start_ticks"],
        "als_pid": child["pid"],
        "als_start_ticks": child["start_ticks"],
        "als_parent_pid": child["parent_pid"],
        "observation": "proc-stat-parent-and-cmdline",
    }


def process_state(session: Session, errors: Path) -> JSON:
    """Observe actual Linux process identities plus one ALS start without restart."""
    if session.process.poll() is not None:
        raise RuntimeError("MCP process exited during diagnostic control")
    program = Path(os.environ.get("ALS_PATH", "ada_language_server")).name
    observed = observe_process_pair(session.process.pid, program)
    if session.process.poll() is not None:
        raise RuntimeError("MCP process exited during process observation")
    logs = errors.read_text()
    if (
        logs.count("Starting ALS:") != 1
        or "ALS restarted" in logs
        or "Attempting ALS restart" in logs
    ):
        raise RuntimeError("diagnostic control must not start/restart another ALS instance")
    return {**observed, "als_start_count": 1}


def run_control(output: Path) -> JSON:
    """Mutate only a new owned fixture and retain the real protocol and outcomes."""
    from mcp_client import Session

    output.mkdir(parents=True, exist_ok=False)
    fixture = output / "fixture"
    fixture.mkdir()
    source = fixture / "main.adb"
    project = fixture / "diagnostic.gpr"
    project.write_text(
        'project Diagnostic is\n for Source_Dirs use (".");\n'
        ' for Object_Dir use "obj";\nend Diagnostic;\n'
    )
    source.write_text(BROKEN)
    command = [
        "env",
        "ADA_PROJECT_FILE=",
        "ADA_PROJECT_ROOT=",
        "ADA_PROJECT_SCENARIO_VARIABLES={}",
        "ADA_MCP_LOG_LEVEL=INFO",
        sys.executable,
        "-m",
        "ada_mcp",
    ]
    report: JSON = {"status": "failed", "argv": command, "cwd": str(Path.cwd()), "states": []}
    session = None
    problem = None
    try:
        session = Session(command, timeout=90, log_dir=output / "mcp")
        report["initialize"] = session.initialize()
        info = session.call(
            "ada_project_info",
            {"gpr_file": str(project), "project_paths": [], "scenario_variables": {}},
        )
        if info.get("complete") is not True or info.get("project_file") != str(project):
            raise AssertionError("the explicit diagnostic fixture project must load completely")
        report["project"] = info
        for number, text in enumerate([BROKEN, REPAIRED, BROKEN]):
            source.write_text(text)
            (output / f"source-state-{number}.adb").write_text(text)
            result = session.call("ada_diagnostics", {"file": str(source), "severity": "all"})
            record = {
                "state": number,
                "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "result": result,
            }
            report["states"].append(record)
            require_state(result, source, expect_errors=number != 1)
            record["process"] = process_state(session, output / "mcp/server-stderr.log")
        identities = {
            (
                state["process"]["mcp_pid"],
                state["process"]["mcp_start_ticks"],
                state["process"]["als_pid"],
                state["process"]["als_start_ticks"],
            )
            for state in report["states"]
        }
        if len(identities) != 1:
            raise AssertionError("MCP and ALS identities must stay stable across all three states")
        report["stable_mcp_and_als"] = True
    except Exception as error:
        problem = type(error).__name__ + ": " + str(error)
    finally:
        if session is not None:
            try:
                report["eof_exit"] = session.close()
            except Exception as error:
                problem = problem or type(error).__name__ + ": " + str(error)
        report["error"] = problem
        report["status"] = "failed" if problem else "passed"
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    if problem:
        raise RuntimeError(problem)
    return report


def main() -> None:
    """Run this mandatory control inside the documented AMD64 Trixie check chain."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    print(json.dumps(run_control(options.output.resolve()), indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Resolve a fixture's DOM.Core import through the installed XML/Ada sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from real_diagnostics import process_state
from real_reading import require_child_exit, require_location, source_hashes

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
FIXTURE = Path(__file__).resolve().parent.parent / "tests/fixtures/xmlada_project"
JSON = dict[str, Any]


def installed_dom_source(report: JSON, fixture: Path) -> Path:
    """Find the package-owned physical source independently of navigation output."""
    command = ["dpkg-query", "-L", "libxmlada-dom-dev"]
    result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
    report["package_files"] = {
        "argv": command,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode:
        raise AssertionError("the image must include libxmlada-dom-dev")
    sources = {
        Path(line).resolve(strict=True)
        for line in result.stdout.splitlines()
        if Path(line).name == "dom-core.ads"
    }
    if len(sources) != 1:
        raise AssertionError("the package must export exactly one physical dom-core.ads")
    source = sources.pop()
    if not source.is_file() or source.is_relative_to(fixture.resolve()):
        raise AssertionError("DOM.Core must resolve outside the owned fixture")
    report["expected_source"] = {
        "file": str(source),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    return source


def require_dom_definition(result: JSON, expected: Path) -> None:
    """Require the installed declaration's identifier, physical path and exact preview."""
    declarations = []
    for number, line in enumerate(expected.read_text().splitlines(), 1):
        match = re.match(r"\s*package\s+(DOM\.Core)\b", line, re.IGNORECASE)
        if match:
            declarations.append((number, match))
    if len(declarations) != 1:
        raise AssertionError("the installed source must declare exactly one DOM.Core package")
    number, match = declarations[0]
    columns = {
        match.start(1) + 1: match.group(1),
        match.start(1) + len("DOM.") + 1: match.group(1).split(".")[1],
    }
    column = result.get("column")
    if type(column) is not int or column not in columns or not isinstance(result.get("file"), str):
        raise AssertionError("navigation must identify the installed DOM.Core declaration name")
    physical = Path(result["file"]).resolve(strict=True)
    require_location(
        {**result, "file": str(physical)},
        (str(expected), number, column),
        columns[column],
    )


def run_control(output: Path) -> JSON:
    """Retain real STDIO, stderr and unchanged fixture inputs, including failed selection."""
    from mcp_client import Session, create_private_directory

    create_private_directory(output)
    root = output / "fixture"
    shutil.copytree(FIXTURE, root)
    inputs = source_hashes(FIXTURE)
    project, source = root / "xmlada_probe.gpr", root / "src/xmlada_probe.adb"
    command = [
        "env",
        "ADA_PROJECT_FILE=",
        "ADA_PROJECT_ROOT=",
        "ADA_PROJECT_SCENARIO_VARIABLES={}",
        "ADA_MCP_UPDATE_CHANNEL=off",
        "ADA_MCP_LOG_LEVEL=INFO",
        sys.executable,
        "-I",
        "-B",
        "-m",
        "ada_mcp",
    ]
    report: JSON = {"status": "failed", "argv": command, "input_sha256": inputs, "calls": []}
    session = None
    identity = None
    problem = None
    stage = "initialize"

    def call(tool: str, arguments: JSON) -> JSON:
        assert session is not None
        record: JSON = {"tool": tool, "arguments": arguments}
        report["calls"].append(record)
        result: JSON = session.call(tool, arguments)
        record["result"] = result
        return result

    try:
        if source_hashes(root) != inputs:
            raise AssertionError("the owned fixture must match the committed inputs")
        session = Session(command, timeout=90, log_dir=output / "mcp")
        report["initialize"] = session.initialize()
        stage = "select-project"
        info = call(
            "ada_project_info",
            {"gpr_file": str(project), "project_paths": [], "scenario_variables": {}},
        )
        if info.get("complete") is not True or info.get("project_file") != str(project):
            raise AssertionError("the explicit XML/Ada fixture project must load completely")
        identity = process_state(session, output / "mcp/server-stderr.log")
        report["process"] = identity
        stage = "package-source"
        expected = installed_dom_source(report, root)
        anchors = [
            (number, line.index("Core") + 1)
            for number, line in enumerate(source.read_text().splitlines(), 1)
            if line.strip() == "with DOM.Core;"
        ]
        if len(anchors) != 1:
            raise AssertionError("the fixture must contain exactly one DOM.Core import")
        line, column = anchors[0]
        stage = "navigate"
        definition = call(
            "ada_goto_definition", {"file": str(source), "line": line, "column": column}
        )
        require_dom_definition(definition, expected)
    except Exception as error:
        problem = type(error).__name__ + ": " + str(error)
    finally:
        if session is not None:
            try:
                report["eof_exit"] = session.close()
                if identity is not None:
                    report["cleanup"] = require_child_exit(identity)
            except Exception as error:
                report["cleanup_error"] = type(error).__name__ + ": " + str(error)
                problem = problem or report["cleanup_error"]
        try:
            report["input_sha256_after"] = source_hashes(root)
            report["committed_input_sha256_after"] = source_hashes(FIXTURE)
            if report["input_sha256_after"] != inputs or source_hashes(FIXTURE) != inputs:
                raise AssertionError("the probe changed an XML/Ada fixture input")
        except Exception as error:
            problem = problem or type(error).__name__ + ": " + str(error)
        report["error"] = problem
        report["failure_stage"] = stage if problem else None
        report["status"] = "failed" if problem else "passed"
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    if problem:
        raise RuntimeError(problem)
    return report


def main() -> None:
    """Run the same installed-server probe against a candidate or published image."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    print(json.dumps(run_control(parser.parse_args().output.resolve()), indent=2))


if __name__ == "__main__":
    main()

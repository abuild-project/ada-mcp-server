#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require both reference anchors to retain an explicitly selected importer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from real_diagnostics import process_state
from real_reading import require_child_exit, require_references, source_hashes

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
FIXTURE = Path(__file__).resolve().parent.parent / "tests/fixtures/reference_project"
JSON = dict[str, Any]


def run_control(output: Path) -> JSON:
    """Compile an owned fixture and retain real STDIO results and process births."""
    from mcp_client import Session

    output.mkdir(parents=True, exist_ok=False)
    root = output / "fixture"
    shutil.copytree(FIXTURE, root)
    inputs = source_hashes(FIXTURE)
    main, spec, body = (
        root / name for name in ("cli/src/main.adb", "src/shared.ads", "src/shared.adb")
    )
    project = root / "cli/cli.gpr"
    command = [
        "env",
        "ADA_PROJECT_FILE=",
        "ADA_PROJECT_ROOT=",
        "ADA_PROJECT_SCENARIO_VARIABLES={}",
        "ADA_MCP_UPDATE_CHANNEL=off",
        "ADA_MCP_LOG_LEVEL=INFO",
        sys.executable,
        "-m",
        "ada_mcp",
    ]
    report: JSON = {"status": "failed", "input_sha256": inputs, "calls": []}
    session = None
    identity = None
    problem = None

    def call(tool: str, arguments: JSON) -> JSON:
        assert session is not None
        result: JSON = session.call(tool, arguments)
        report["calls"].append({"tool": tool, "arguments": arguments, "result": result})
        return result

    def compile_sources(name: str, compiler: list[str]) -> None:
        """Retain the compiler's actual command and output for an owned source state."""
        environment = dict(os.environ, GPR_PROJECT_PATH=str(root))
        compiled = subprocess.run(
            compiler, env=environment, capture_output=True, text=True, timeout=60, check=False
        )
        report[name] = {
            "argv": compiler,
            "GPR_PROJECT_PATH": str(root),
            "exit_code": compiled.returncode,
            "stdout": compiled.stdout,
            "stderr": compiled.stderr,
        }
        if compiled.returncode:
            raise AssertionError("the importing Ada fixture did not compile")

    try:
        compile_sources("compile", ["gprbuild", "-p", "-P", str(project)])
        session = Session(command, timeout=90, log_dir=output / "mcp")
        report["initialize"] = session.initialize()
        selection = {
            "gpr_file": str(project),
            "project_paths": [str(root)],
            "scenario_variables": {},
        }
        info = call("ada_project_info", selection)
        if info.get("complete") is not True or info.get("project_file") != str(project):
            raise AssertionError("the explicit CLI fixture project must load completely")
        identity = process_state(session, output / "mcp/server-stderr.log")
        report["initial_process"] = identity
        expected = {(str(main), 4, 11), (str(spec), 2, 14), (str(body), 2, 14)}
        imported_alias = spec.parent / ".." / "src" / spec.name
        for source, line, column in ((main, 4, 11), (imported_alias, 2, 14)):
            require_references(
                call(
                    "ada_find_references",
                    {
                        "file": str(source),
                        "line": line,
                        "column": column,
                        "include_declaration": True,
                    },
                ),
                expected,
                "Reference_View_Probe_Increment",
            )
        added = root / "src/late.adb"
        added.write_text(
            "with Shared;\nprocedure Late is\nbegin\n"
            "   Shared.Reference_View_Probe_Increment;\nend Late;\n"
        )
        report["added_input_sha256"] = {
            "src/late.adb": hashlib.sha256(added.read_bytes()).hexdigest()
        }
        compile_sources(
            "added_compile",
            ["gprbuild", "-p", "-P", str(root / "library.gpr"), "-c", "-u", "late.adb"],
        )
        refreshed = call("ada_project_info", selection)
        if refreshed.get("complete") is not True or refreshed.get("project_file") != str(project):
            raise AssertionError("reselection must reevaluate the explicit CLI fixture project")
        expected.add((str(added), 4, 11))
        for source, line, column in ((added, 4, 11), (spec, 2, 14)):
            require_references(
                call(
                    "ada_find_references",
                    {
                        "file": str(source),
                        "line": line,
                        "column": column,
                        "include_declaration": True,
                    },
                ),
                expected,
                "Reference_View_Probe_Increment",
            )
        report["final_importer_process"] = process_state(session, output / "mcp/server-stderr.log")
        if report["final_importer_process"] != identity:
            raise AssertionError("both anchors must use the same MCP and CLI ALS births")

        unrelated = root / "unrelated/src/other.ads"
        for query, count in (
            ("Reference_View_Probe_Increment", 0),
            ("Reference_View_Nonmember_Marker", 1),
        ):
            result = call(
                "ada_workspace_symbols", {"file": str(unrelated), "query": query, "limit": 50}
            )
            if (
                result.get("complete") is not True
                or result.get("truncated") is not False
                or result.get("count") != count
                or len(result.get("symbols", [])) != count
            ):
                raise AssertionError("a nonmember must use its own evaluated project")
            if count and result["symbols"][0].get("file") != str(unrelated):
                raise AssertionError("the nonmember's positive symbol must identify its source")
        after = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs}
        report["input_sha256_after"] = after
        report["added_input_sha256_after"] = {
            "src/late.adb": hashlib.sha256(added.read_bytes()).hexdigest()
        }
        if after != inputs or report["added_input_sha256_after"] != report["added_input_sha256"]:
            raise AssertionError("compilation or read queries changed a fixture input")
    except Exception as error:
        problem = type(error).__name__ + ": " + str(error)
    finally:
        if session is not None:
            try:
                report["eof_exit"] = session.close()
                if identity is not None:
                    report["cleanup"] = require_child_exit(identity)
            except Exception as error:
                problem = problem or type(error).__name__ + ": " + str(error)
        report["error"] = problem
        report["status"] = "failed" if problem else "passed"
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    if problem:
        raise RuntimeError(problem)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    print(json.dumps(run_control(parser.parse_args().output.resolve()), indent=2))

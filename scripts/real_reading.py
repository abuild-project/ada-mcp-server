#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prove bounded reading semantics through MCP and the pinned real ALS."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from real_diagnostics import process_state, read_identity, require_state

if TYPE_CHECKING:
    from mcp_client import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
JSON = dict[str, Any]
Location = tuple[str, int, int]
Symbol = tuple[str, str, str, int, int]
FIXTURE = Path(__file__).resolve().parent.parent / "tests/fixtures/reading_project"


def source_hashes(root: Path) -> dict[str, str]:
    """Hash exact Ada/GPR inputs, excluding ALS-owned build products."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.suffix in {".ads", ".adb", ".gpr"}
    }


def require_location(result: JSON, expected: Location, token: str) -> None:
    """Require a positive result at one exact source token and its preview."""
    actual = (result.get("file"), result.get("line"), result.get("column"))
    if result.get("found") is not True or actual != expected or result.get("error"):
        raise AssertionError(f"expected location {expected!r}, received {result!r}")
    line = Path(expected[0]).read_text().splitlines()[expected[1] - 1]
    if line[expected[2] - 1 : expected[2] - 1 + len(token)] != token:
        raise AssertionError("expected location does not identify the fixture token")
    if result.get("preview") != line.rstrip():
        raise AssertionError("navigation preview must match the exact source line")


def require_references(result: JSON, expected: set[Location], token: str) -> None:
    """Require the complete unordered reference set without duplicates or extras."""
    items = result.get("references")
    if not isinstance(items, list) or result.get("error"):
        raise AssertionError("references must be an error-free list")
    actual = [(item.get("file"), item.get("line"), item.get("column")) for item in items]
    if (
        set(actual) != expected
        or len(actual) != len(expected)
        or result.get("count") != len(expected)
    ):
        raise AssertionError(f"expected reference set {expected!r}, received {result!r}")
    for item in items:
        require_location(
            {**item, "found": True}, (item["file"], item["line"], item["column"]), token
        )


def require_workspace(result: JSON, expected: set[Symbol]) -> None:
    """Require exact complete workspace matches, including kind and location."""
    items = result.get("symbols")
    if (
        result.get("complete") is not True
        or result.get("truncated") is not False
        or result.get("error")
        or not isinstance(items, list)
    ):
        raise AssertionError("workspace symbols must be complete and untruncated")
    actual = [
        (item.get("name"), item.get("kind"), item.get("file"), item.get("line"), item.get("column"))
        for item in items
    ]
    if (
        set(actual) != expected
        or len(actual) != len(expected)
        or result.get("count") != len(expected)
    ):
        raise AssertionError(f"expected workspace set {expected!r}, received {result!r}")


def require_document(result: JSON, object_name: str) -> None:
    """Require the exact Main/child hierarchy, kinds and selection coordinates."""
    if result.get("error") or result.get("complete", True) is not True:
        raise AssertionError("document symbols must not be an error or incomplete result")
    if result.get("truncated", False) is not False:
        raise AssertionError("document symbols must not be truncated")
    actual: list[tuple[tuple[str, ...], str, int, int]] = []

    def visit(items: list[JSON], parents: tuple[str, ...] = ()) -> None:
        for item in items:
            path = (*parents, item.get("name", ""))
            actual.append((path, item.get("kind", ""), item.get("line", 0), item.get("column", 0)))
            visit(item.get("children", []), path)

    items = result.get("symbols")
    if not isinstance(items, list):
        raise AssertionError("document symbols must be a list")
    # The pinned ALS adds a synthetic top-level group for context clauses.
    # Its implementation-specific ranges are outside the semantic subtree.
    envelopes = [item for item in items if item.get("name") == "With clauses"]
    if len(envelopes) != 1 or envelopes[0].get("kind") != "namespace":
        raise AssertionError("expected one ALS With clauses namespace envelope")
    visit([item for item in items if item.get("name") != "With clauses"])
    expected = {
        (("Main",), "function", 2, 11),
        (("Main", object_name), "variable", 3, 4),
        (("Main", "Step"), "function", 4, 14),
    }
    if set(actual) != expected or len(actual) != len(expected):
        raise AssertionError(f"expected document hierarchy {expected!r}, received {actual!r}")


def require_hover(result: JSON, object_name: str, source: Path) -> None:
    """Require the exact fixture declaration and source position emitted by ALS."""
    contents = result.get("contents")
    if result.get("found") is not True or not isinstance(contents, str) or result.get("error"):
        raise AssertionError("hover must contain a positive declaration")
    declaration = f"{object_name} : Reading.Counter := (Value => 0);"
    if source.read_text().splitlines()[2] != "   " + declaration:
        raise AssertionError("the fixture must contain the expected object declaration at 3:4")
    expected = f"{declaration}\nat {source.name} (3:4)"
    if contents != expected:
        raise AssertionError("hover must match the queried object declaration and source position")


def require_absent(result: JSON) -> None:
    """A comment with no semantic target must have an explicit negative result."""
    if result.get("found") is not False or result.get("error"):
        raise AssertionError("a comment must have no navigation or hover target")


def require_project(result: JSON, root: Path) -> None:
    """Require the exact evaluated fixture view, sources and main unit."""
    if (
        result.get("complete") is not True
        or result.get("error")
        or result.get("project_file") != str(root / "reading.gpr")
        or {Path(path) for path in result.get("source_dirs", [])} != {root / "src"}
        or result.get("main_units") != ["main.adb"]
    ):
        raise AssertionError(f"expected the explicit reading GPR view, received {result!r}")


def require_child_exit(identity: JSON) -> JSON:
    """Require the observed ALS birth to disappear after MCP EOF cleanup."""
    deadline = time.monotonic() + 5
    while True:
        try:
            current = read_identity(Path("/proc") / str(identity["als_pid"]))
        except FileNotFoundError:
            return {"als_pid": identity["als_pid"], "observed_child_exited": True}
        if current["start_ticks"] != identity["als_start_ticks"]:
            return {
                "als_pid": identity["als_pid"],
                "observed_child_exited": True,
                "pid_reused": True,
            }
        if time.monotonic() >= deadline:
            raise AssertionError("the observed ALS child survived MCP EOF cleanup")
        time.sleep(0.05)


def run_control(output: Path) -> JSON:
    """Retain real MCP evidence while querying two source states in one session."""
    from mcp_client import Session

    output.mkdir(parents=True, exist_ok=False)
    root = output / "fixture"
    shutil.copytree(FIXTURE, root)
    original_hashes = source_hashes(FIXTURE)
    main = root / "src/main.adb"
    spec = root / "src/reading.ads"
    body = root / "src/reading.adb"
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
    report: JSON = {
        "status": "failed",
        "evidence_kind": "real-mcp-pinned-als",
        "argv": command,
        "cwd": str(Path.cwd()),
        "fixture_sha256": original_hashes,
        "calls": [],
        "states": [],
    }
    session: Session | None = None
    identity: JSON | None = None
    problem = None
    deadline = time.monotonic() + 360

    def call(tool: str, arguments: JSON) -> JSON:
        assert session is not None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("reading control exceeded its total request budget")
        session.timeout = min(90, remaining)
        before = source_hashes(root)
        record: JSON = {"tool": tool, "arguments": arguments, "source_sha256_before": before}
        report["calls"].append(record)
        try:
            result: JSON = session.call(tool, arguments)
            record["result"] = result
        finally:
            after = source_hashes(root)
            record["source_sha256_after"] = after
            record["sources_unchanged"] = before == after
        if before != after:
            raise AssertionError("a read-only query changed its Ada/GPR inputs")
        return result

    try:
        session = Session(command, timeout=90, log_dir=output / "mcp")
        report["initialize"] = session.initialize()
        project_result = call(
            "ada_project_info",
            {
                "gpr_file": str(root / "reading.gpr"),
                "project_paths": [],
                "scenario_variables": {},
            },
        )
        identity = process_state(session, output / "mcp/server-stderr.log")
        require_project(project_result, root)
        require_location(
            call("ada_goto_definition", {"file": str(main), "line": 6, "column": 15}),
            (str(spec), 5, 14),
            "Reading_Probe_Increment",
        )
        require_location(
            call("ada_implementation", {"file": str(spec), "line": 5, "column": 14}),
            (str(body), 2, 14),
            "Reading_Probe_Increment",
        )
        # Both units are open before the workspace check: ALS omits open units
        # from its raw workspace index, so the server must merge live symbols.
        for source in (spec, body):
            call("ada_document_symbols", {"file": str(source)})
        expected_symbols = {
            ("Reading_Probe_Increment", "function", str(spec), 5, 14),
            ("Reading_Probe_Increment", "function", str(body), 2, 14),
        }
        for number, name in enumerate(("Item", "Other")):
            if number:
                main.write_text(main.read_text().replace("Item", "Other"))
            (output / f"main-state-{number}.adb").write_bytes(main.read_bytes())
            require_document(call("ada_document_symbols", {"file": str(main)}), name)
            require_location(
                call("ada_goto_definition", {"file": str(main), "line": 6, "column": 40}),
                (str(main), 3, 4),
                name,
            )
            require_location(
                call("ada_type_definition", {"file": str(main), "line": 6, "column": 40}),
                (str(spec), 2, 9),
                "Counter",
            )
            require_hover(
                call("ada_hover", {"file": str(main), "line": 6, "column": 40}), name, main
            )
            for include in (True, False):
                expected = {(str(main), 6, 40)}
                if include:
                    expected.add((str(main), 3, 4))
                require_references(
                    call(
                        "ada_find_references",
                        {"file": str(main), "line": 3, "column": 4, "include_declaration": include},
                    ),
                    expected,
                    name,
                )
            for query, expected_matches in (
                ("Reading_Probe_Increment", expected_symbols),
                ("No_Such_Reading_Symbol", set()),
            ):
                require_workspace(
                    call(
                        "ada_workspace_symbols",
                        {"file": str(main), "query": query, "kind": "function", "limit": 50},
                    ),
                    expected_matches,
                )
            require_state(
                call("ada_diagnostics", {"file": str(main), "severity": "all"}),
                main,
                expect_errors=False,
            )
            observed = process_state(session, output / "mcp/server-stderr.log")
            if identity is not None and observed != identity:
                raise AssertionError("MCP/ALS identities changed after source mutation")
            identity = observed
            report["states"].append(
                {"object": name, "source_sha256": source_hashes(root), "process": observed}
            )
        for tool in (
            "ada_goto_definition",
            "ada_implementation",
            "ada_type_definition",
            "ada_hover",
        ):
            require_absent(call(tool, {"file": str(main), "line": 10, "column": 7}))
        report["final_process"] = process_state(session, output / "mcp/server-stderr.log")
        if report["final_process"] != identity:
            raise AssertionError("MCP/ALS identities changed during no-target queries")
        report["stable_mcp_and_als"] = True
    except Exception as error:
        problem = type(error).__name__ + ": " + str(error)
    finally:
        if session is not None:
            try:
                report["eof_exit"] = session.close()
            except Exception as error:
                report["eof_error"] = type(error).__name__ + ": " + str(error)
                problem = problem or report["eof_error"]
        if identity is not None:
            try:
                report["cleanup"] = require_child_exit(identity)
            except Exception as error:
                report["cleanup_error"] = type(error).__name__ + ": " + str(error)
                problem = problem or report["cleanup_error"]
        report["original_fixture_unchanged"] = source_hashes(FIXTURE) == original_hashes
        if not report["original_fixture_unchanged"]:
            problem = problem or "AssertionError: the original fixture changed"
        report["error"] = problem
        report["status"] = "failed" if problem else "passed"
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    if problem:
        raise RuntimeError(problem)
    return report


def main() -> None:
    """Run the mandatory reading probe within the full AMD64 Trixie chain."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    print(json.dumps(run_control(options.output.resolve()), indent=2))


if __name__ == "__main__":
    main()

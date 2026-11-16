#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Observe additional native tool capabilities without claiming acceptance."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import additional_support as support
from real_diagnostics import process_state
from real_reading import require_child_exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
JSON = dict[str, Any]


def run_observation(output: Path) -> JSON:
    """Retain one bounded exploratory run and fail on harness boundary errors."""
    from mcp_client import Session, validate_calls

    support.require_no_symlink_ancestors(output)
    output.mkdir(parents=True, exist_ok=False)
    root = output / "fixture"
    original = support.file_hashes(support.FIXTURE)
    shutil.copytree(support.FIXTURE, root, symlinks=True)
    main, spec, body = (root / "src" / name for name in ("main.adb", "probe.ads", "probe.adb"))
    initial_sources = {
        str(path.relative_to(root)): path.read_bytes() for path in (main, spec, body)
    }
    command = [
        "env",
        "ADA_PROJECT_FILE=",
        "ADA_PROJECT_ROOT=" + str(root),
        "ADA_PROJECT_SCENARIO_VARIABLES={}",
        "ADA_MCP_UPDATE_CHANNEL=off",
        "ADA_MCP_LOG_LEVEL=INFO",
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "--serve-trace",
        str(output / "native-requests.jsonl"),
    ]
    report: JSON = {
        "status": "failed",
        "evidence_kind": "exploratory-real-mcp-pinned-als",
        "semantic_acceptance": False,
        "argv": command,
        "cwd": str(Path.cwd()),
        "source_sha": os.environ.get("ADA_MCP_CHECK_SOURCE_SHA"),
        "fixture_sha256": original,
        "calls": [],
        "states": [],
        "client_denials": [],
    }
    session: Session | None = None
    identity: JSON | None = None
    problem = None
    deadline = time.monotonic() + 600

    def call(label: str, tool: str, arguments: JSON, allow_build: bool = False) -> JSON:
        assert session is not None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("additional observation exceeded its total request budget")
        session.timeout = min(90, remaining)
        before = support.file_hashes(root)
        record: JSON = {
            "label": label,
            "tool": tool,
            "arguments": arguments,
            "file_sha256_before": before,
            "input_sha256_before": support.input_hashes(root),
            "allow_owned_build_outputs": allow_build,
        }
        report["calls"].append(record)
        try:
            raw = session.request("tools/call", {"name": tool, "arguments": arguments})
            record["raw_result"] = raw
            result = support.decode_result(raw)
            record["result"] = result
            record["semantic_error"] = bool(raw.get("isError") or result.get("error"))
        except Exception as error:
            record["request_error"] = type(error).__name__ + ": " + str(error)
            raise
        finally:
            try:
                after = support.file_hashes(root)
            except Exception as error:
                record["file_inspection_error"] = type(error).__name__ + ": " + str(error)
                raise
            record["file_sha256_after"] = after
            record["input_sha256_after"] = support.input_hashes(root)
            record["inputs_unchanged"] = (
                record["input_sha256_before"] == record["input_sha256_after"]
            )
            record["changed_files"] = sorted(
                name for name in before.keys() | after.keys() if before.get(name) != after.get(name)
            )
        support.require_changes(before, after, allow_build)
        if identity is not None:
            observed = process_state(session, output / "mcp/server-stderr.log")
            record["process"] = observed
            if observed != identity:
                raise AssertionError("MCP/ALS process births changed during observation")
        return result

    def state(label: str) -> None:
        inputs = support.input_hashes(root)
        report["states"].append(
            {
                "label": label,
                "input_sha256": inputs,
                "files": {name: (root / name).read_text() for name in inputs},
            }
        )

    try:
        state("initial")
        session = Session(command, timeout=90, log_dir=output / "mcp")
        report["initialize"] = session.initialize()
        report["tools"] = session.tools()
        project = call(
            "explicit-project",
            "ada_project_info",
            {
                "gpr_file": str(root / "additional.gpr"),
                "project_paths": [],
                "scenario_variables": {},
            },
        )
        if project.get("complete") is not True or project.get("project_file") != str(
            root / "additional.gpr"
        ):
            raise AssertionError("observation requires the exact evaluated fixture project")
        identity = process_state(session, output / "mcp/server-stderr.log")
        report["initial_process"] = identity
        call(
            "cold-main-calls",
            "ada_call_hierarchy",
            {"file": str(main), "line": 2, "column": 11, "direction": "both"},
        )
        for source in (main, spec, body):
            call("warm-source", "ada_document_symbols", {"file": str(source)})
        for direction in ("incoming", "outgoing", "both"):
            call(
                "increment-" + direction,
                "ada_call_hierarchy",
                {"file": str(body), "line": 2, "column": 14, "direction": direction},
            )
        call(
            "comment-calls",
            "ada_call_hierarchy",
            {"file": str(main), "line": 7, "column": 7, "direction": "both"},
        )
        for target in (root / "src", main, root / "missing.adb"):
            call("dependencies-" + target.name, "ada_dependency_graph", {"file": str(target)})
        for limit in (50, 1):
            call(
                "qualified-completion",
                "ada_completions",
                {
                    "file": str(main),
                    "line": 5,
                    "column": 21,
                    "trigger_character": ".",
                    "limit": limit,
                },
            )
        call("comment-completion", "ada_completions", {"file": str(main), "line": 7, "column": 7})
        for column in (31, 33):
            call(
                "combine-signature",
                "ada_signature_help",
                {"file": str(main), "line": 5, "column": column},
            )
        call("comment-signature", "ada_signature_help", {"file": str(main), "line": 7, "column": 7})
        for line, start, end in ((5, 15, 36), (2, 11, 15), (7, 7, 7)):
            call(
                "actions-at-source",
                "ada_code_actions",
                {
                    "file": str(main),
                    "start_line": line,
                    "start_column": start,
                    "end_line": line,
                    "end_column": end,
                },
            )
        for line, column, name in (
            (3, 4, "Renamed_Counter"),
            (7, 7, "Renamed_Counter"),
            (3, 4, "Invalid__Name"),
        ):
            call(
                "rename-preview",
                "ada_rename_symbol",
                {
                    "file": str(main),
                    "line": line,
                    "column": column,
                    "new_name": name,
                    "preview": True,
                },
            )
        call(
            "uneven-formatting",
            "ada_format_file",
            {"file": str(root / "formatting/uneven.adb"), "tab_size": 3, "insert_spaces": True},
        )
        call(
            "formatted-source",
            "ada_format_file",
            {"file": str(root / "formatting/orphan.adb"), "tab_size": 3, "insert_spaces": True},
        )
        call("semantic-spec", "ada_get_spec", {"file": str(body), "line": 2, "column": 14})
        call("sibling-spec", "ada_get_spec", {"file": str(body)})
        call("missing-spec", "ada_get_spec", {"file": str(root / "formatting/orphan.adb")})
        support.mutate_owned(
            root,
            {
                source: (root / "states" / (source.stem + "-after" + source.suffix)).read_bytes()
                for source in (main, spec, body)
            },
        )
        state("warm-semantic-change")
        # This must precede every handler which synchronizes changed sources.
        call(
            "changed-cold-main-calls",
            "ada_call_hierarchy",
            {"file": str(main), "line": 2, "column": 11, "direction": "both"},
        )
        for source in (main, spec, body):
            call("changed-warm-source", "ada_document_symbols", {"file": str(source)})
        call(
            "changed-advance-calls",
            "ada_call_hierarchy",
            {"file": str(body), "line": 4, "column": 14, "direction": "both"},
        )
        call(
            "changed-qualified-completion",
            "ada_completions",
            {"file": str(main), "line": 7, "column": 21, "trigger_character": "."},
        )
        for column in (29, 31, 34):
            call(
                "changed-merge-signature",
                "ada_signature_help",
                {"file": str(main), "line": 7, "column": column},
            )
        call(
            "changed-rename-preview",
            "ada_rename_symbol",
            {
                "file": str(main),
                "line": 5,
                "column": 4,
                "new_name": "Moved_Counter",
                "preview": True,
            },
        )
        call(
            "changed-semantic-spec",
            "ada_get_spec",
            {"file": str(body), "line": 4, "column": 14},
        )
        call("changed-dependencies", "ada_dependency_graph", {"file": str(root / "src")})
        support.mutate_owned(
            root, {root / name: content for name, content in initial_sources.items()}
        )
        state("restored-for-build")
        for directory in ("manifest", "malformed", "formatting"):
            call("manifest-" + directory, "ada_alire_info", {"project_dir": str(root / directory)})
        for tool, arguments in (
            ("ada_build", {"gpr_file": str(root / "additional.gpr")}),
            ("ada_format_file", {"file": str(main)}),
            ("ada_rename_symbol", {"file": str(main), "preview": False}),
            ("ada_rename_symbol", {"file": str(main)}),
        ):
            try:
                validate_calls([{"tool": tool, "arguments": arguments}])
            except ValueError as error:
                report["client_denials"].append(
                    {"tool": tool, "arguments": arguments, "error": str(error)}
                )
            else:
                raise AssertionError(
                    "the read-only client unexpectedly permitted an owned-only call"
                )
        call(
            "native-rename-application-gap",
            "ada_rename_symbol",
            {
                "file": str(main),
                "line": 3,
                "column": 4,
                "new_name": "Not_Applied",
                "preview": False,
            },
        )
        call(
            "compiler-success",
            "ada_build",
            {"gpr_file": str(root / "additional.gpr"), "extra_args": ["-p"]},
            allow_build=True,
        )
        report["successful_build_files"] = {
            name: digest
            for name, digest in support.file_hashes(root).items()
            if Path(name).parts[0] in support.GENERATED
        }
        support.mutate_owned(root, {main: (root / "states/main-error.adb").read_bytes()})
        state("deliberate-compiler-error")
        call(
            "compiler-error",
            "ada_build",
            {"gpr_file": str(root / "additional.gpr"), "extra_args": ["-p", "-f"]},
            allow_build=True,
        )
        report["final_process"] = process_state(session, output / "mcp/server-stderr.log")
        if report["final_process"] != identity:
            raise AssertionError("MCP/ALS process births changed at the end of observation")
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
        try:
            report["original_fixture_unchanged"] = support.file_hashes(support.FIXTURE) == original
        except Exception as error:
            report["original_fixture_unchanged"] = False
            report["original_fixture_inspection_error"] = type(error).__name__ + ": " + str(error)
        if not report["original_fixture_unchanged"]:
            problem = problem or "AssertionError: the original additional fixture changed"
        report["error"] = problem
        report["status"] = "failed" if problem else "observed"
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    if problem:
        raise RuntimeError(problem)
    return report


def main() -> None:
    """Run exploration or its instrumented child without changing server code."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--serve-trace", type=Path)
    options = parser.parse_args()
    if options.serve_trace is not None:
        support.observed_server(options.serve_trace)
    else:
        print(json.dumps(run_observation(options.output.absolute()), indent=2))


if __name__ == "__main__":
    main()

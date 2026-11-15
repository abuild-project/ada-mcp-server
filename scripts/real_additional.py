#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require bounded additional-tool semantics through MCP and the pinned ALS."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import additional_oracles as oracle
import observe_additional as observation
from real_diagnostics import process_state
from real_reading import require_child_exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tooling"))
JSON = dict[str, Any]
FIXTURE = observation.FIXTURE
Check = Callable[[JSON], Any]
KNOWN_POSITIONAL_CASES = {
    ("positional-initial-1", "src/main.adb", 5, 33, False, 1): 0,
    ("positional-changed-1", "src/main.adb", 7, 31, True, 1): 0,
    ("positional-changed-2", "src/main.adb", 7, 34, True, 2): 1,
}


def native_result(events: list[JSON], method: str) -> Any:
    """Require exactly one successful native reply for a correlated tool call."""
    results = [
        row["result"]
        for row in events
        if row.get("event") == "result" and row.get("method") == method
    ]
    if len(results) != 1 or any(row.get("event") == "error" for row in events):
        raise AssertionError(f"expected one successful native {method} response")
    return results[0]


def require_native_signature(
    events: list[JSON], file: Path, line: int, column: int, result: JSON
) -> None:
    """Reject candidate coordinate or index conversion defects before native triage."""
    requests = [
        row
        for row in events
        if row.get("event") == "request" and row.get("method") == "textDocument/signatureHelp"
    ]
    oracle.require_equal(
        [row.get("params") for row in requests],
        [
            {
                "textDocument": {"uri": file.as_uri()},
                "position": {"line": line - 1, "character": column - 1},
            }
        ],
        "native signature request coordinates",
    )
    native = native_result(events, "textDocument/signatureHelp")
    signatures = native.get("signatures", [])
    if not signatures:
        raise AssertionError("a positive native signature reply must contain signatures")
    raw_active = native.get("activeSignature", 0)
    raw_top_parameter = native.get("activeParameter", 0)
    raw_parameters = [sig["activeParameter"] for sig in signatures if "activeParameter" in sig]
    if any(
        type(value) is not int or value < 0
        for value in (
            raw_active,
            raw_top_parameter,
            *raw_parameters,
            result.get("active_signature"),
            result.get("active_parameter"),
        )
    ):
        raise AssertionError("signature indices must be integers at least zero, excluding booleans")
    active = raw_active if raw_active < len(signatures) else 0
    selected = signatures[active]
    parameters = selected.get("parameters", [])
    if "activeParameter" in selected:
        parameter = selected["activeParameter"]
        if parameters and parameter >= len(parameters):
            raise AssertionError("per-signature parameter outside its list remains unaccepted")
    else:
        parameter = raw_top_parameter
        if parameters and parameter >= len(parameters):
            parameter = 0
    oracle.require_equal(
        (result.get("active_signature"), result.get("active_parameter")),
        (active, parameter),
        "MCP signature indices must equal effective native indices",
    )


def require_known_positional_blocker(
    result: JSON,
    events: list[JSON],
    root: Path,
    label: str,
    file: Path,
    line: int,
    column: int,
    changed: bool,
    parameter: int,
) -> None:
    """Allow assessment only for the three primary-evidenced native defects."""
    key = (label, file.relative_to(root).as_posix(), line, column, changed, parameter)
    if key not in KNOWN_POSITIONAL_CASES:
        raise AssertionError("positional discrepancy is outside the three evidenced native cases")
    require_native_signature(events, file, line, column, result)
    wrong_parameter = KNOWN_POSITIONAL_CASES[key]
    expected_signature = oracle.signature_result(changed, parameter)["signatures"][0]
    expected_native = {
        "signatures": [
            {
                "label": expected_signature["label"],
                "documentation": "",
                "parameters": [
                    {"label": param["label"]} for param in expected_signature["parameters"]
                ],
                "activeParameter": wrong_parameter,
            }
        ],
        "activeSignature": 0,
        "activeParameter": wrong_parameter,
    }
    oracle.require_equal(
        native_result(events, "textDocument/signatureHelp"),
        expected_native,
        "original native defect envelope",
    )
    oracle.require_equal(
        result,
        {
            **oracle.signature_result(changed, parameter),
            "active_parameter": KNOWN_POSITIONAL_CASES[key],
        },
        "known native positional discrepancy",
    )


def require_native_rename(
    events: list[JSON], locations: set[oracle.Location], token: str, replacement: str
) -> None:
    """Check original native edit endpoints and replacements before summarization."""
    result = native_result(events, "textDocument/rename")
    actual = []
    for uri, edits in result.get("changes", {}).items():
        for edit in edits:
            actual.append(
                (
                    uri,
                    edit["range"]["start"]["line"],
                    edit["range"]["start"]["character"],
                    edit["range"]["end"]["line"],
                    edit["range"]["end"]["character"],
                    edit["newText"],
                )
            )
    for change in result.get("documentChanges", []):
        if set(change) != {"textDocument", "edits"}:
            raise AssertionError("rename preview must not propose resource operations")
        for edit in change["edits"]:
            actual.append(
                (
                    change["textDocument"]["uri"],
                    edit["range"]["start"]["line"],
                    edit["range"]["start"]["character"],
                    edit["range"]["end"]["line"],
                    edit["range"]["end"]["character"],
                    edit["newText"],
                )
            )
    expected = {
        (Path(file).as_uri(), line - 1, column - 1, line - 1, column - 1 + len(token), replacement)
        for file, line, column in locations
    }
    if set(actual) != expected or len(actual) != len(expected):
        raise AssertionError(
            "native rename ranges and replacements must match the exact source tokens"
        )


def require_native_action(events: list[JSON], root: Path) -> None:
    """Require the meaningful named-parameter command and exact source arguments."""
    actions = native_result(events, "textDocument/codeAction")
    expected = {
        "title": "Name parameters in the call",
        "kind": "refactor.rewrite",
        "command": {
            "title": "",
            "command": "als-named-parameters",
            "arguments": [
                {
                    "context": (root / "additional.gpr").as_uri(),
                    "where": {
                        "textDocument": {"uri": (root / "src/main.adb").as_uri()},
                        "position": {"line": 4, "character": 29},
                    },
                    "versioned_documents": False,
                }
            ],
        },
    }
    matches = [action for action in actions if action.get("title") == expected["title"]]
    oracle.require_equal(matches, [expected], "native named-parameter action proposal")


def require_native_calls(
    events: list[JSON],
    method: str,
    source: Path,
    sites: dict[str, list[tuple[int, int]]],
    token: str | None = None,
) -> None:
    """Require native call-site ranges, including multiple sites for one edge."""
    calls = native_result(events, "callHierarchy/" + method + "Calls")
    actual = []
    for call in calls or []:
        item = call["to" if method == "outgoing" else "from"]
        for value in call["fromRanges"]:
            actual.append(
                (
                    item["name"],
                    value["start"]["line"],
                    value["start"]["character"],
                    value["end"]["line"],
                    value["end"]["character"],
                )
            )
    expected = [
        (name, line - 1, column - 1, line - 1, column - 1 + len(token or name))
        for name, positions in sites.items()
        for line, column in positions
    ]
    oracle.require_equal(sorted(actual), sorted(expected), "native complete call-site ranges")
    for name, positions in sites.items():
        for line, column in positions:
            oracle.require_token((str(source), line, column), token or name)


def require_no_action_execution(events: list[JSON]) -> None:
    """Allow only the two project-information commands used by this probe."""
    for row in events:
        if (
            row.get("event") == "request"
            and row.get("method") == "workspace/executeCommand"
            and row.get("params", {}).get("command")
            not in {"als-project-view-information", "als-mains"}
        ):
            raise AssertionError("additional queries must not execute action commands")


def require_trace(events: list[JSON], root: Path) -> None:
    """Require intact request/reply correlation and the actual initialized providers."""
    requests = [row for row in events if row.get("event") == "request"]
    responses = [row for row in events if row.get("event") in {"result", "error"}]
    if len(responses) != len(requests) or any(
        row["id"] not in {request["id"] for request in requests} for row in responses
    ):
        raise AssertionError("native trace must not contain orphan or extra replies")
    if len({row["id"] for row in requests}) != len(requests):
        raise AssertionError("native request identifiers must be unique")
    require_no_action_execution(events)
    for request in requests:
        responses = [
            row
            for row in events
            if row.get("id") == request["id"] and row.get("event") in {"result", "error"}
        ]
        if (
            len(responses) != 1
            or responses[0].get("method") != request["method"]
            or responses[0]["event"] != "result"
        ):
            raise AssertionError("every native request must retain one successful matching reply")
    init = [row for row in requests if row["method"] == "initialize"]
    if (
        len(init) != 1
        or init[0]["params"]["rootUri"] != root.as_uri()
        or init[0]["params"]["initializationOptions"]
        != {"projectFile": str(root / "additional.gpr")}
    ):
        raise AssertionError("native initialize must select the exact owned GPR view")
    capabilities = native_result(events, "initialize")["capabilities"]
    for provider in (
        "callHierarchyProvider",
        "codeActionProvider",
        "declarationProvider",
        "documentFormattingProvider",
    ):
        if capabilities.get(provider) is not True:
            raise AssertionError("the pinned ALS must advertise the exercised native provider")
    if (
        not isinstance(capabilities.get("completionProvider"), dict)
        or not isinstance(capabilities.get("signatureHelpProvider"), dict)
        or capabilities.get("renameProvider") != {"prepareProvider": True}
    ):
        raise AssertionError(
            "native completion, signature and prepared rename capabilities are required"
        )


def run_control(output: Path, allow_positional_blocker: bool = False) -> JSON:
    """Retain strict live results, explicit native blockers and all failure evidence."""
    from mcp_client import Session, validate_calls

    output.mkdir(parents=True, exist_ok=False)
    root = output / "fixture"
    original = observation.file_hashes(FIXTURE)
    shutil.copytree(FIXTURE, root)
    main, spec, body = (root / "src" / name for name in ("main.adb", "probe.ads", "probe.adb"))
    named = root / "formatting/named.adb"
    initial_sources = {path: path.read_bytes() for path in (main, spec, body, named)}
    trace = output / "native-requests.jsonl"
    command = [
        "env",
        "ADA_PROJECT_FILE=",
        "ADA_PROJECT_ROOT=" + str(root),
        "ADA_PROJECT_SCENARIO_VARIABLES={}",
        "ADA_MCP_UPDATE_CHANNEL=off",
        "ADA_MCP_LOG_LEVEL=INFO",
        sys.executable,
        "-B",
        str(Path(observation.__file__).resolve()),
        "--serve-trace",
        str(trace),
    ]
    report: JSON = {
        "status": "failed",
        "evidence_kind": "real-mcp-pinned-als",
        "argv": command,
        "cwd": str(Path.cwd()),
        "source_sha": os.environ.get("ADA_MCP_CHECK_SOURCE_SHA"),
        "checked_image_target": os.environ.get("ADA_MCP_CHECK_IMAGE_TARGET"),
        "checked_image_platform": os.environ.get("ADA_MCP_CHECK_IMAGE_PLATFORM"),
        "fixture_sha256": original,
        "calls": [],
        "states": [],
        "native_blockers": [],
        "semantic_acceptance": False,
        "allow_positional_blocker": allow_positional_blocker,
    }
    session: Session | None = None
    identity: JSON | None = None
    problem = None
    deadline = time.monotonic() + 600

    def trace_rows() -> list[JSON]:
        return (
            [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
        )

    def call(
        label: str,
        tool: str,
        arguments: JSON,
        check: Check,
        build: bool = False,
        native_check: Callable[[list[JSON]], None] | None = None,
    ) -> JSON:
        assert session is not None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("additional control exceeded its total request budget")
        session.timeout = min(90, remaining)
        before = observation.file_hashes(root)
        native_before = len(trace_rows())
        record: JSON = {
            "label": label,
            "tool": tool,
            "arguments": arguments,
            "file_sha256_before": before,
            "input_sha256_before": observation.input_hashes(root),
            "allow_owned_build_outputs": build,
            "accepted": False,
        }
        report["calls"].append(record)
        try:
            raw = session.request("tools/call", {"name": tool, "arguments": arguments})
            record["raw_result"] = raw
            result = observation.decode_result(raw)
            record["result"] = result
        except Exception as error:
            record["request_error"] = type(error).__name__ + ": " + str(error)
            raise
        finally:
            after = observation.file_hashes(root)
            record["file_sha256_after"] = after
            record["input_sha256_after"] = observation.input_hashes(root)
            record["inputs_unchanged"] = (
                record["input_sha256_before"] == record["input_sha256_after"]
            )
            record["changed_files"] = sorted(
                name for name in before.keys() | after.keys() if before.get(name) != after.get(name)
            )
            record["native_events"] = trace_rows()[native_before:]
        observation.require_changes(before, after, build)
        if raw.get("isError"):
            raise AssertionError("MCP tool transport reported isError")
        if identity is not None:
            observed = process_state(session, output / "mcp/server-stderr.log")
            record["process"] = observed
            if observed != identity:
                raise AssertionError("MCP/ALS process births changed during additional control")
        try:
            check(result)
            if native_check is not None:
                native_check(record["native_events"])
            require_no_action_execution(record["native_events"])
        except Exception as error:
            record["oracle_error"] = type(error).__name__ + ": " + str(error)
            raise
        record["accepted"] = True
        return result

    def state(label: str) -> None:
        inputs = observation.input_hashes(root)
        report["states"].append(
            {
                "label": label,
                "input_sha256": inputs,
                "files": {name: (root / name).read_text() for name in inputs},
            }
        )

    def mutate(label: str, changes: dict[Path, bytes]) -> None:
        for path, text in changes.items():
            if not path.is_relative_to(root) or path.is_relative_to(FIXTURE):
                raise AssertionError("source mutation must stay in the fresh owned fixture")
            path.write_bytes(text)
        state(label)

    def equal(expected: JSON, purpose: str) -> Check:
        return lambda result: oracle.require_equal(result, expected, purpose)

    def rename(
        label: str,
        file: Path,
        line: int,
        column: int,
        old: str,
        new: str,
        locations: set[oracle.Location],
    ) -> None:
        call(
            label,
            "ada_rename_symbol",
            {"file": str(file), "line": line, "column": column, "new_name": new, "preview": True},
            lambda result: oracle.require_rename(result, old, new, locations),
            native_check=lambda events: require_native_rename(events, locations, old, new),
        )

    def signature(
        label: str,
        file: Path,
        line: int,
        column: int,
        changed: bool,
        parameter: int,
        positional: bool,
    ) -> None:
        def check(result: JSON) -> None:
            events = report["calls"][-1]["native_events"]
            require_native_signature(events, file, line, column, result)
            expected = oracle.signature_result(changed, parameter)
            try:
                oracle.require_signature(result, changed, parameter)
                return
            except AssertionError:
                if not (allow_positional_blocker and positional):
                    raise
                require_known_positional_blocker(
                    result, events, root, label, file, line, column, changed, parameter
                )
                report["native_blockers"].append(
                    {
                        "label": label,
                        "file": str(file),
                        "line": line,
                        "column": column,
                        "expected_correct": expected,
                        "actual": result,
                        "native": native_result(events, "textDocument/signatureHelp"),
                        "reason": "pinned ALS decrements unnamed actual parameter indices",
                        "semantic_acceptance": False,
                    }
                )
                return

        call(
            label, "ada_signature_help", {"file": str(file), "line": line, "column": column}, check
        )
        if report["native_blockers"] and report["native_blockers"][-1]["label"] == label:
            report["calls"][-1]["accepted"] = False
            report["calls"][-1]["blocked_native_positional_selection"] = True

    def hierarchy(
        label: str,
        file: Path,
        line: int,
        column: int,
        name: str,
        outgoing: set[oracle.Edge],
        incoming: set[oracle.Edge],
        direction: str = "both",
        sites: dict[str, list[tuple[int, int]]] | None = None,
    ) -> None:
        def native_check(events: list[JSON]) -> None:
            if direction in ("outgoing", "both"):
                require_native_calls(
                    events, "outgoing", file, (sites or {}) if name == "Main" else {}
                )
            if direction in ("incoming", "both"):
                require_native_calls(
                    events,
                    "incoming",
                    main,
                    {"Main": (sites or {}).get(name, [])} if incoming else {},
                    token=name,
                )

        call(
            label,
            "ada_call_hierarchy",
            {"file": str(file), "line": line, "column": column, "direction": direction},
            lambda result: oracle.require_hierarchy(result, name, outgoing, incoming),
            native_check=native_check,
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
            lambda result: oracle.require_project(result, root),
        )
        report["project"] = project
        identity = process_state(session, output / "mcp/server-stderr.log")
        report["initial_process"] = identity
        initial_edges = {("Combine", 12, str(spec), 3, 13), ("Increment", 12, str(spec), 2, 14)}
        caller = {("Main", 12, str(main), 2, 11)}
        hierarchy(
            "cold-main-calls",
            main,
            2,
            11,
            "Main",
            initial_edges,
            set(),
            sites={"Combine": [(5, 21)], "Increment": [(6, 10)]},
        )
        for source in (spec, body):
            call(
                "synchronize-package",
                "ada_document_symbols",
                {"file": str(source)},
                lambda result: (
                    None
                    if isinstance(result.get("symbols"), list) and result["symbols"]
                    else oracle.require_equal(result, {"nonempty": True}, "package synchronization")
                ),
            )
        for direction in ("incoming", "outgoing", "both"):
            hierarchy(
                "increment-" + direction,
                body,
                2,
                14,
                "Increment",
                set(),
                caller if direction != "outgoing" else set(),
                direction,
                sites={"Increment": [(6, 10)]},
            )
        call(
            "comment-calls",
            "ada_call_hierarchy",
            {"file": str(main), "line": 7, "column": 7, "direction": "both"},
            equal(
                {"found": False, "outgoing_calls": [], "incoming_calls": []}, "comment hierarchy"
            ),
        )
        for label, target, count in (
            ("directory", root / "src", 3),
            ("file", main, 1),
            ("missing", root / "missing.adb", 0),
        ):
            call(
                "dependencies-" + label,
                "ada_dependency_graph",
                {"file": str(target)},
                lambda result: oracle.require_dependencies(
                    result, root, count, ["Probe"] if count else []
                ),
            )
        for limit in (50, 1):
            call(
                "qualified-completion-" + str(limit),
                "ada_completions",
                {
                    "file": str(main),
                    "line": 5,
                    "column": 21,
                    "trigger_character": ".",
                    "limit": limit,
                },
                lambda result: oracle.require_completions(result, False, limit),
            )
        call(
            "comment-completion",
            "ada_completions",
            {"file": str(main), "line": 7, "column": 7},
            equal({"completions": [], "count": 0, "is_incomplete": False}, "comment completion"),
        )
        for index, column in enumerate((30, 33)):
            signature("positional-initial-" + str(index), main, 5, column, False, index, True)
        for index, column in enumerate((36, 48)):
            signature("named-initial-" + str(index), named, 5, column, False, index, False)
        call(
            "comment-signature",
            "ada_signature_help",
            {"file": str(main), "line": 7, "column": 7},
            equal(
                {"found": False, "signatures": [], "active_signature": 0, "active_parameter": 0},
                "comment signature",
            ),
        )
        for location, line, start, end in (
            ("call", 5, 15, 36),
            ("declaration", 2, 11, 15),
            ("comment", 7, 7, 7),
        ):
            call(
                "actions-" + location,
                "ada_code_actions",
                {
                    "file": str(main),
                    "start_line": line,
                    "start_column": start,
                    "end_line": line,
                    "end_column": end,
                },
                lambda result: oracle.require_actions(result, location),
                native_check=(lambda events: require_native_action(events, root))
                if location == "call"
                else None,
            )
        rename(
            "rename-initial",
            main,
            3,
            4,
            "Counter",
            "Renamed_Counter",
            {(str(main), 3, 4), (str(main), 5, 4), (str(main), 6, 21)},
        )
        rename(
            "rename-cross-unit",
            spec,
            2,
            14,
            "Increment",
            "Next_Increment",
            {(str(spec), 2, 14), (str(body), 2, 14), (str(body), 5, 8), (str(main), 6, 10)},
        )
        for label, line, column, new, error in (
            ("comment", 7, 7, "Renamed_Counter", "Cannot rename symbol at this location"),
            ("invalid", 3, 4, "Invalid__Name", "Invalid Ada identifier: 'Invalid__Name'"),
        ):
            call(
                "rename-" + label,
                "ada_rename_symbol",
                {
                    "file": str(main),
                    "line": line,
                    "column": column,
                    "new_name": new,
                    "preview": True,
                },
                equal(
                    {"success": False, "error": error, "changes": [], "total_changes": 0},
                    "negative rename",
                ),
            )
        uneven = root / "formatting/uneven.adb"
        call(
            "uneven-formatting",
            "ada_format_file",
            {"file": str(uneven), "tab_size": 3, "insert_spaces": True},
            lambda result: oracle.require_formatting(result, uneven, oracle.FORMATTED_UNEVEN),
        )
        mutate("owned-formatted-source", {uneven: oracle.FORMATTED_UNEVEN.encode()})
        call(
            "already-formatted",
            "ada_format_file",
            {"file": str(uneven), "tab_size": 3, "insert_spaces": True},
            equal(
                {"formatted": False, "file": str(uneven), "changes": 0, "edits": []},
                "native already-formatted null",
            ),
        )
        call(
            "semantic-spec",
            "ada_get_spec",
            {"file": str(body), "line": 2, "column": 14},
            lambda result: oracle.require_spec(
                result, spec, 2, 14, "procedure Increment (Item : in out Integer);"
            ),
        )
        call(
            "sibling-spec",
            "ada_get_spec",
            {"file": str(body)},
            lambda result: oracle.require_spec(result, spec, 1, 1, "package Probe is"),
        )
        call(
            "missing-spec",
            "ada_get_spec",
            {"file": str(root / "formatting/orphan.adb")},
            equal(
                {
                    "found": False,
                    "spec_file": None,
                    "line": None,
                    "column": None,
                    "preview": "",
                    "error": "No spec file found",
                },
                "missing spec",
            ),
        )
        mutate("main-only-call-change", {main: (root / "states/main-calls.adb").read_bytes()})
        hierarchy(
            "main-only-changed-calls",
            main,
            2,
            11,
            "Main",
            {("Increment", 12, str(spec), 2, 14)},
            set(),
            sites={"Increment": [(7, 10)]},
        )
        call(
            "removed-call-actions",
            "ada_code_actions",
            {
                "file": str(main),
                "start_line": 5,
                "start_column": 15,
                "end_line": 5,
                "end_column": 36,
            },
            lambda result: oracle.require_actions(result, "comment"),
        )
        mutate(
            "full-semantic-change",
            {
                main: (root / "states/main-after.adb").read_bytes(),
                spec: (root / "states/probe-after.ads").read_bytes(),
                body: (root / "states/probe-after.adb").read_bytes(),
                named: (root / "states/named-after.adb").read_bytes(),
            },
        )
        for source in (spec, body):
            call(
                "synchronize-changed-package",
                "ada_document_symbols",
                {"file": str(source)},
                lambda result: (
                    None
                    if isinstance(result.get("symbols"), list) and result["symbols"]
                    else oracle.require_equal(result, {"nonempty": True}, "package synchronization")
                ),
            )
        hierarchy(
            "changed-main-calls",
            main,
            2,
            11,
            "Main",
            {("Merge", 12, str(spec), 5, 13), ("Advance", 12, str(spec), 4, 14)},
            set(),
            sites={"Merge": [(7, 21)], "Advance": [(8, 10), (9, 10)]},
        )
        hierarchy(
            "changed-advance-calls",
            body,
            4,
            14,
            "Advance",
            set(),
            caller,
            sites={"Advance": [(8, 10), (9, 10)]},
        )
        call(
            "changed-completions",
            "ada_completions",
            {"file": str(main), "line": 7, "column": 21, "trigger_character": "."},
            lambda result: oracle.require_completions(result, True),
        )
        for index, column in enumerate((28, 31, 34)):
            signature("positional-changed-" + str(index), main, 7, column, True, index, True)
        for index, column in enumerate((34, 46, 58)):
            signature("named-changed-" + str(index), named, 5, column, True, index, False)
        rename(
            "rename-changed",
            main,
            5,
            4,
            "Counter",
            "Moved_Counter",
            {(str(main), 5, 4), (str(main), 7, 4), (str(main), 8, 19), (str(main), 9, 19)},
        )
        call(
            "changed-spec",
            "ada_get_spec",
            {"file": str(body), "line": 4, "column": 14},
            lambda result: oracle.require_spec(
                result, spec, 4, 14, "procedure Advance (Item : in out Natural);"
            ),
        )
        mutate(
            "changed-import",
            {main: main.read_bytes().replace(b"with Probe;", b"with Probe, Ada.Text_IO;")},
        )
        call(
            "changed-dependencies",
            "ada_dependency_graph",
            {"file": str(root / "src")},
            lambda result: oracle.require_dependencies(result, root, 3, ["Ada.Text_IO", "Probe"]),
        )
        call(
            "manifest-initial",
            "ada_alire_info",
            {"project_dir": str(root / "manifest")},
            lambda result: oracle.require_manifest(result, root),
        )
        mutate(
            "changed-manifest",
            {root / "manifest/alire.toml": (root / "states/alire-after.toml").read_bytes()},
        )
        call(
            "manifest-changed",
            "ada_alire_info",
            {"project_dir": str(root / "manifest")},
            lambda result: oracle.require_manifest(result, root, True),
        )
        for directory, message in (
            ("malformed", "Failed to parse alire.toml:"),
            ("formatting", "No alire.toml found in "),
        ):
            call(
                "manifest-" + directory,
                "ada_alire_info",
                {"project_dir": str(root / directory)},
                lambda result: oracle.require_equal(
                    (
                        result.get("is_alire_project"),
                        isinstance(result.get("error"), str)
                        and result["error"].startswith(message),
                    ),
                    (False, True),
                    "negative manifest",
                ),
            )
        report["client_denials"] = []
        for tool, arguments in (
            ("ada_build", {"gpr_file": str(root / "additional.gpr")}),
            ("ada_format_file", {"file": str(main)}),
            ("ada_rename_symbol", {"file": str(main)}),
            ("ada_rename_symbol", {"file": str(main), "preview": False}),
        ):
            try:
                validate_calls([{"tool": tool, "arguments": arguments}])
            except ValueError as error:
                report["client_denials"].append(
                    {"tool": tool, "arguments": arguments, "error": str(error)}
                )
            else:
                raise AssertionError("read-only client unexpectedly permitted an owned-only call")
        mutate("restored-for-build", initial_sources)
        call(
            "compiler-success",
            "ada_build",
            {"gpr_file": str(root / "additional.gpr"), "extra_args": ["-p"]},
            lambda result: oracle.require_build(result, root, True),
            build=True,
        )
        report["successful_build_files"] = {
            name: digest
            for name, digest in observation.file_hashes(root).items()
            if Path(name).parts[0] in observation.GENERATED
        }
        mutate("deliberate-compiler-error", {main: (root / "states/main-error.adb").read_bytes()})
        call(
            "compiler-error",
            "ada_build",
            {"gpr_file": str(root / "additional.gpr"), "extra_args": ["-p", "-f"]},
            lambda result: oracle.require_build(result, root, False),
            build=True,
        )
        report["final_process"] = process_state(session, output / "mcp/server-stderr.log")
        if report["final_process"] != identity:
            raise AssertionError("MCP/ALS process births changed at the end of additional control")
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
            require_trace(trace_rows(), root)
            report["native_trace_complete"] = True
        except Exception as error:
            report["native_trace_error"] = type(error).__name__ + ": " + str(error)
            problem = problem or report["native_trace_error"]
        report["original_fixture_unchanged"] = observation.file_hashes(FIXTURE) == original
        if not report["original_fixture_unchanged"]:
            problem = problem or "AssertionError: the original additional fixture changed"
        report["error"] = problem
        report["status"] = (
            "failed"
            if problem
            else ("assessed-with-native-blocker" if report["native_blockers"] else "passed")
        )
        report["semantic_acceptance"] = problem is None and not report["native_blockers"]
        (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    if problem:
        raise RuntimeError(problem)
    return report


def main() -> None:
    """Run strict checks; any native blocker needs an explicit scope decision."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-native-positional-blocker", action="store_true")
    options = parser.parse_args()
    print(
        json.dumps(
            run_control(options.output.resolve(), options.allow_native_positional_blocker), indent=2
        )
    )


if __name__ == "__main__":
    main()

"""Reach strict runner boundaries with mocked semantics; no real ALS evidence."""

import copy
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import additional_support as support
import mcp_client
import pytest
import real_additional as real

from tests.host.test_additional_control import (
    completions,
    format_result,
    manifest_result,
    rename_result,
)
from tests.host.test_signature_precedence import known_native


def signature_result(changed, parameter):
    names = ["Left", "Right", "Extra"] if changed else ["Left", "Right"]
    label = (
        "function Merge (Left : Natural; Right : Natural; Extra : Natural) return Natural"
        if changed
        else "function Combine (Left : Integer; Right : Integer) return Integer"
    )
    return {
        "found": True,
        "signatures": [
            {
                "label": label,
                "documentation": "",
                "parameters": [{"label": name, "documentation": ""} for name in names],
            }
        ],
        "active_signature": 0,
        "active_parameter": parameter,
    }


def actions(location):
    titles = {
        "call": [
            ("Name parameters in the call", "refactor.rewrite"),
            ("Extract Procedure", "refactor.extract"),
            ("Extract Function", "refactor.extract"),
        ],
        "declaration": [("Extract Variable", "refactor.extract")],
        "comment": [],
    }[location]
    return {
        "actions": [
            {
                "title": title,
                "kind": kind,
                "is_preferred": False,
                "has_edit": False,
                "files_affected": 0,
                "command": "",
            }
            for title, kind in titles
        ],
        "count": len(titles),
    }


@pytest.fixture
def runner(tmp_path, monkeypatch):
    original = tmp_path / "original-fixture"
    shutil.copytree(support.FIXTURE, original)
    monkeypatch.setattr(support, "FIXTURE", original)
    control = SimpleNamespace(
        output=tmp_path / "run",
        original=original,
        on_call=None,
        native_mutation=None,
        request_error=False,
        identity_change={},
        close_error=None,
        cleanup_error=None,
        close_count=0,
        cleanup_count=0,
        calls=[],
        final_birth=False,
        final_observations=0,
        last_compiler_error=False,
    )
    identity = {
        "mcp_pid": 701,
        "mcp_start_ticks": 71,
        "als_pid": 702,
        "als_start_ticks": 72,
        "als_parent_pid": 701,
        "als_start_count": 1,
    }

    class SemanticSession:
        def __init__(self, command, timeout, log_dir):
            self.root = Path(log_dir).parent / "fixture"
            self.trace = Path(log_dir).parent / "native-requests.jsonl"
            self.timeout = timeout
            self.serial = 0
            Path(log_dir).mkdir()
            (Path(log_dir) / "server-stderr.log").write_text("mock process evidence\n")

        def emit(self, method, value, params=None):
            self.serial += 1
            value = copy.deepcopy(value)
            if control.native_mutation:
                control.native_mutation(method, value)
            with self.trace.open("a") as stream:
                for row in (
                    {
                        "event": "request",
                        "id": self.serial,
                        "method": method,
                        "params": params or {},
                    },
                    {"event": "result", "id": self.serial, "method": method, "result": value},
                ):
                    stream.write(json.dumps(row) + "\n")

        def initialize_native(self):
            self.emit(
                "initialize",
                {
                    "capabilities": {
                        "callHierarchyProvider": True,
                        "codeActionProvider": True,
                        "declarationProvider": True,
                        "documentFormattingProvider": True,
                        "completionProvider": {},
                        "signatureHelpProvider": {},
                        "renameProvider": {"prepareProvider": True},
                    }
                },
                {
                    "rootUri": self.root.as_uri(),
                    "initializationOptions": {"projectFile": str(self.root / "additional.gpr")},
                },
            )
            return {"mock_initialize": True}

        def initialize(self):
            return {"mock_initialize": True}

        def tools(self):
            return [{"name": "mock catalog"}]

        def request(self, method, params):
            assert method == "tools/call"
            tool, arguments = params["name"], params["arguments"]
            control.calls.append(copy.deepcopy(params))
            if control.request_error and tool == "ada_call_hierarchy":
                raise TimeoutError("mock request timeout")
            result = self.response(tool, arguments)
            if control.on_call:
                control.on_call(self.root, tool, arguments, result)
            return {"content": [{"type": "text", "text": json.dumps(result)}]}

        def response(self, tool, args):
            main = self.root / "src/main.adb"
            spec = self.root / "src/probe.ads"
            changed = "Probe.Merge" in main.read_text()
            document = (
                {"textDocument": {"uri": Path(args["file"]).as_uri()}} if "file" in args else {}
            )
            located = {
                **document,
                "position": {
                    "line": args.get("line", 1) - 1,
                    "character": args.get("column", 1) - 1,
                },
            }
            if tool == "ada_project_info":
                self.initialize_native()
                self.emit(
                    "workspace/executeCommand",
                    {
                        "tree": {"root-project": {"id": "fixture-root"}},
                        "projects": [
                            {
                                "project": {
                                    "id": "fixture-root",
                                    "name": "Additional",
                                    "file-name": str(self.root / "additional.gpr"),
                                    "source-directories": [
                                        str(self.root / "src"),
                                        str(self.root / "formatting"),
                                    ],
                                    "object-directory": str(self.root / "obj") + "/",
                                    "executable-directory": str(self.root / "bin"),
                                }
                            }
                        ],
                    },
                    {"command": "als-project-view-information", "arguments": []},
                )
                self.emit(
                    "workspace/executeCommand",
                    [str(main)],
                    {"command": "als-mains", "arguments": []},
                )
                return {
                    "complete": True,
                    "project_file": str(self.root / "additional.gpr"),
                    "project_name": "Additional",
                    "object_dir": str(self.root / "obj") + "/",
                    "exec_dir": str(self.root / "bin"),
                    "source_dirs": [str(self.root / "src"), str(self.root / "formatting")],
                    "main_units": ["main.adb"],
                }
            if tool == "ada_document_symbols":
                self.emit(
                    "textDocument/documentSymbol",
                    [
                        {
                            "name": "Probe",
                            "kind": 4,
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 0, "character": 16},
                            },
                            "selectionRange": {
                                "start": {"line": 0, "character": 8},
                                "end": {"line": 0, "character": 13},
                            },
                        }
                    ],
                    document,
                )
                return {
                    "symbols": [
                        {
                            "name": "Probe",
                            "kind": "package",
                            "line": 1,
                            "column": 9,
                            "range": {"start": 1, "end": 1},
                        }
                    ]
                }
            if tool == "ada_call_hierarchy":
                if args.get("line") == 7 and args.get("column") == 7:
                    self.emit("textDocument/prepareCallHierarchy", None, located)
                    return {"found": False, "outgoing_calls": [], "incoming_calls": []}
                is_main = args["file"] == str(main)
                name = "Main" if is_main else "Advance" if changed else "Increment"
                names = (
                    (
                        ["Merge", "Advance"]
                        if changed
                        else ["Combine", "Increment"]
                        if "Probe.Combine" in main.read_text()
                        else ["Increment"]
                    )
                    if is_main
                    else []
                )
                positions = {
                    "Combine": (3, 13),
                    "Increment": (2, 14),
                    "Merge": (5, 13),
                    "Advance": (4, 14),
                }
                outgoing = [
                    {
                        "name": member,
                        "kind": 12,
                        "file": str(spec),
                        "line": positions[member][0],
                        "column": positions[member][1],
                    }
                    for member in names
                ]
                incoming = (
                    []
                    if is_main
                    else [{"name": "Main", "kind": 12, "file": str(main), "line": 2, "column": 11}]
                )
                item = {
                    "name": name,
                    "kind": 12,
                    "uri": Path(args["file"]).as_uri(),
                    "range": {
                        "start": located["position"],
                        "end": {
                            "line": args["line"] - 1,
                            "character": args["column"] - 1 + len(name),
                        },
                    },
                }
                self.emit("textDocument/prepareCallHierarchy", [item], located)

                def endpoint(value):
                    start = {"line": value["line"] - 1, "character": value["column"] - 1}
                    return {
                        "name": value["name"],
                        "kind": value["kind"],
                        "uri": Path(value["file"]).as_uri(),
                        "range": {
                            "start": start,
                            "end": {**start, "character": start["character"] + len(value["name"])},
                        },
                    }

                def ranges(member):
                    values = []
                    for line, text in enumerate(main.read_text().splitlines(), 1):
                        marker = "Probe." + member
                        if marker in text and not text.lstrip().startswith("--"):
                            column = text.index(marker) + len("Probe.")
                            values.append(
                                {
                                    "start": {"line": line - 1, "character": column},
                                    "end": {"line": line - 1, "character": column + len(member)},
                                }
                            )
                    return values

                direction = args["direction"]
                if direction in ("outgoing", "both"):
                    self.emit(
                        "callHierarchy/outgoingCalls",
                        [
                            {"to": endpoint(item), "fromRanges": ranges(item["name"])}
                            for item in outgoing
                        ]
                        or None,
                        {"item": item},
                    )
                else:
                    outgoing = []
                if direction in ("incoming", "both"):
                    self.emit(
                        "callHierarchy/incomingCalls",
                        [{"from": endpoint(incoming[0]), "fromRanges": ranges(name)}]
                        if incoming
                        else None,
                        {"item": item},
                    )
                else:
                    incoming = []
                return {
                    "found": True,
                    "symbol": name,
                    "outgoing_calls": outgoing,
                    "incoming_calls": incoming,
                    "outgoing_count": len(outgoing),
                    "incoming_count": len(incoming),
                }
            if tool == "ada_dependency_graph":
                if not Path(args["file"]).exists():
                    return {"dependencies": [], "package_count": 0}
                return {
                    "dependencies": [
                        {
                            "package": "Main",
                            "file": str(main),
                            "depends_on": ["Ada.Text_IO", "Probe"]
                            if "with Probe, Ada.Text_IO;" in main.read_text()
                            else ["Probe"],
                        }
                    ],
                    "package_count": 3 if Path(args["file"]).is_dir() else 1,
                }
            if tool == "ada_completions":
                if args["line"] == 7 and args["column"] == 7:
                    self.emit(
                        "textDocument/completion", None, {**located, "context": {"triggerKind": 1}}
                    )
                    return {"completions": [], "count": 0, "is_incomplete": False}
                result = completions(changed)
                self.emit(
                    "textDocument/completion",
                    {
                        "items": [
                            {
                                "label": row["label"],
                                "kind": 3,
                                "detail": row["detail"],
                                "documentation": row["documentation"],
                                "insertText": row["insert_text"],
                                "sortText": row["sort_text"],
                            }
                            for row in result["completions"]
                        ],
                        "isIncomplete": False,
                    },
                    {
                        **located,
                        "context": {
                            "triggerKind": 2,
                            "triggerCharacter": args["trigger_character"],
                        },
                    },
                )
                if args.get("limit") == 1:
                    result["completions"] = result["completions"][:1]
                    result["count"] = 1
                return result
            if tool == "ada_signature_help":
                if args["column"] == 7:
                    self.emit(
                        "textDocument/signatureHelp",
                        {"signatures": [], "activeSignature": 0},
                        located,
                    )
                    return {
                        "found": False,
                        "signatures": [],
                        "active_signature": 0,
                        "active_parameter": 0,
                    }
                named = Path(args["file"]).name == "named.adb"
                columns = (
                    (34, 46, 58)
                    if changed and named
                    else (36, 48)
                    if named
                    else (28, 31, 34)
                    if changed
                    else (30, 33)
                )
                index = columns.index(args["column"])
                result = signature_result(changed, index if named else max(0, index - 1))
                native_parameter = result["active_parameter"]
                self.emit(
                    "textDocument/signatureHelp",
                    {
                        "signatures": [
                            {
                                "label": result["signatures"][0]["label"],
                                "documentation": "",
                                "parameters": [
                                    {"label": param["label"]}
                                    for param in result["signatures"][0]["parameters"]
                                ],
                                "activeParameter": native_parameter,
                            }
                        ],
                        "activeSignature": result["active_signature"],
                        "activeParameter": native_parameter,
                    },
                    {
                        "textDocument": {"uri": Path(args["file"]).as_uri()},
                        "position": {"line": args["line"] - 1, "character": args["column"] - 1},
                    },
                )
                return result
            if tool == "ada_code_actions":
                text = main.read_text().splitlines()[args["start_line"] - 1]
                location = (
                    "comment"
                    if text.lstrip().startswith("--")
                    else "call"
                    if args["start_line"] == 5
                    else "declaration"
                )
                params = {
                    **document,
                    "range": {
                        "start": {
                            "line": args["start_line"] - 1,
                            "character": args["start_column"] - 1,
                        },
                        "end": {"line": args["end_line"] - 1, "character": args["end_column"] - 1},
                    },
                    "context": {"diagnostics": []},
                }
                extras = [
                    {
                        "title": row["title"],
                        "kind": row["kind"],
                        "command": {"title": "", "command": "mock-extract"},
                    }
                    for row in actions(location)["actions"]
                ]
                if location == "call":
                    self.emit(
                        "textDocument/codeAction",
                        [
                            {
                                "title": "Name parameters in the call",
                                "kind": "refactor.rewrite",
                                "command": {
                                    "title": "",
                                    "command": "als-named-parameters",
                                    "arguments": [
                                        {
                                            "context": (self.root / "additional.gpr").as_uri(),
                                            "where": {
                                                "textDocument": {"uri": main.as_uri()},
                                                "position": {"line": 4, "character": 29},
                                            },
                                            "versioned_documents": False,
                                        }
                                    ],
                                },
                            }
                        ]
                        + extras[1:],
                        params,
                    )
                else:
                    self.emit("textDocument/codeAction", extras, params)
                return actions(location)
            if tool == "ada_rename_symbol":
                if args["new_name"] == "Invalid__Name":
                    return {
                        "success": False,
                        "error": "Invalid Ada identifier: 'Invalid__Name'",
                        "changes": [],
                        "total_changes": 0,
                    }
                if args["line"] == 7 and args["column"] == 7:
                    self.emit("textDocument/prepareRename", None, located)
                    return {
                        "success": False,
                        "error": "Cannot rename symbol at this location",
                        "changes": [],
                        "total_changes": 0,
                    }
                result = rename_result(
                    self.root, args["new_name"], changed, args["file"] == str(spec)
                )
                self.emit(
                    "textDocument/prepareRename", {"placeholder": result["old_name"]}, located
                )
                edits = {}
                for item in result["changes"]:
                    edits.setdefault(Path(item["file"]).as_uri(), []).append(
                        {
                            "range": {
                                "start": {
                                    "line": item["line"] - 1,
                                    "character": item["column"] - 1,
                                },
                                "end": {
                                    "line": item["line"] - 1,
                                    "character": item["column"] - 1 + len(item["old_text"]),
                                },
                            },
                            "newText": item["new_text"],
                        }
                    )
                self.emit(
                    "textDocument/rename",
                    {"changes": edits},
                    {**located, "newName": args["new_name"]},
                )
                return result
            if tool == "ada_format_file":
                params = {
                    **document,
                    "options": {"tabSize": args["tab_size"], "insertSpaces": args["insert_spaces"]},
                }
                if Path(args["file"]).read_text().splitlines()[2].startswith("   "):
                    self.emit("textDocument/formatting", None, params)
                    return {"formatted": False, "file": args["file"], "changes": 0, "edits": []}
                self.emit(
                    "textDocument/formatting",
                    [
                        {
                            "range": {
                                "start": {"line": 2, "character": 0},
                                "end": {"line": 3, "character": 0},
                            },
                            "newText": "   null;\n",
                        }
                    ],
                    params,
                )
                return format_result(self.root)
            if tool == "ada_get_spec":
                if Path(args["file"]).name == "orphan.adb":
                    return {
                        "found": False,
                        "spec_file": None,
                        "line": None,
                        "column": None,
                        "preview": "",
                        "error": "No spec file found",
                    }
                line, column = (args["line"], 14) if "line" in args else (1, 1)
                if "line" in args:
                    self.emit(
                        "textDocument/declaration",
                        {
                            "uri": spec.as_uri(),
                            "range": {
                                "start": {"line": line - 1, "character": column - 1},
                                "end": {
                                    "line": line - 1,
                                    "character": column
                                    - 1
                                    + len("Advance" if changed else "Increment"),
                                },
                            },
                        },
                        located,
                    )
                return {
                    "found": True,
                    "spec_file": str(spec),
                    "line": line,
                    "column": column,
                    "preview": spec.read_text().splitlines()[line - 1].strip(),
                }
            if tool == "ada_alire_info":
                directory = Path(args["project_dir"])
                if directory.name == "malformed":
                    return {
                        "is_alire_project": False,
                        "error": "Failed to parse alire.toml: mock syntax failure",
                    }
                if directory.name != "manifest":
                    return {
                        "is_alire_project": False,
                        "error": "No alire.toml found in " + str(directory),
                    }
                return manifest_result(
                    self.root, 'version = "2.0.0"' in (directory / "alire.toml").read_text()
                )
            if tool == "ada_build":
                base = {
                    "gpr_file": str(self.root / "additional.gpr"),
                    "warnings": [],
                    "warning_count": 0,
                    "hints": [],
                }
                if "deliberate compiler type error" not in main.read_text():
                    for filename, data in (
                        ("bin/main", b"\x7fELFmock"),
                        ("obj/b__main.adb", b"mock binder source\n"),
                    ):
                        path = self.root / filename
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(data)
                        path.chmod(0o700)
                    return {
                        **base,
                        "success": True,
                        "exit_code": 0,
                        "errors": [],
                        "error_count": 0,
                        "output": "",
                    }
                control.last_compiler_error = True
                return {
                    **base,
                    "success": False,
                    "exit_code": 4,
                    "errors": [
                        {
                            "file": "main.adb",
                            "line": 3,
                            "column": 25,
                            "severity": "error",
                            "message": message,
                        }
                        for message in ('expected type "Standard.Integer"', "found a string type")
                    ],
                    "error_count": 2,
                    "output": (
                        'main.adb:3:25: error: expected type "Standard.Integer"\n'
                        "main.adb:3:25: error: found a string type\n"
                    ),
                }
            raise AssertionError("unexpected tool " + tool)

        def close(self):
            control.close_count += 1
            if control.close_error:
                raise RuntimeError(control.close_error)
            return 0

    def process(*_args):
        if control.last_compiler_error:
            control.final_observations += 1
            if control.final_birth and control.final_observations >= 2:
                return {**identity, "als_start_ticks": 999}
        return {**identity, **control.identity_change}

    def cleanup(_identity):
        control.cleanup_count += 1
        if control.cleanup_error:
            raise RuntimeError(control.cleanup_error)
        return {"observed_child_exited": True}

    monkeypatch.setattr(mcp_client, "Session", SemanticSession)
    monkeypatch.setattr(real, "process_state", process)
    monkeypatch.setattr(real, "require_child_exit", cleanup)
    return control


def report(runner):
    return json.loads((runner.output / "summary.json").read_text())


def test_provisional_runner_keeps_positional_discrepancies_unaccepted(runner):
    result = real.run_control(runner.output, allow_positional_blocker=True)
    assert (
        result["status"] == "assessed-with-native-blocker"
        and result["semantic_acceptance"] is False
    )
    assert len(result["native_blockers"]) == 3
    blocked = [row for row in result["calls"] if not row["accepted"]]
    assert [row["label"] for row in blocked] == [
        "positional-initial-1",
        "positional-changed-1",
        "positional-changed-2",
    ]
    assert all(row["blocked_native_positional_selection"] for row in blocked)
    assert (
        len(result["calls"]) == 53 and sum(row["accepted"] is True for row in result["calls"]) == 50
    )
    labels = [row["label"] for row in result["calls"]]
    assert labels[1] == "cold-main-calls"
    assert labels.index("main-only-changed-calls") + 1 == labels.index("removed-call-actions")
    assert result["native_trace_complete"] is True and result["original_fixture_unchanged"] is True
    assert runner.close_count == runner.cleanup_count == 1


def test_strict_default_fails_native_wrong_positional_selection(runner):
    with pytest.raises(RuntimeError, match="signature selection"):
        real.run_control(runner.output)
    result = report(runner)
    assert result["status"] == "failed" and result["native_blockers"] == []
    assert result["calls"][-1]["accepted"] is False
    assert result["calls"][-1]["result"]["active_parameter"] == 0
    assert runner.close_count == runner.cleanup_count == 1


def test_wrong_mcp_index_with_correct_native_index_is_never_a_native_blocker(runner):
    def correct_native(method, value):
        if (
            method == "textDocument/signatureHelp"
            and runner.calls[-1]["arguments"].get("column") == 33
        ):
            value["signatures"][0]["activeParameter"] = 1

    runner.native_mutation = correct_native
    with pytest.raises(
        RuntimeError, match="MCP signature indices must equal effective native indices"
    ):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["native_blockers"] == [] and result["calls"][-1]["accepted"] is False


def test_differing_native_fields_with_correct_effective_mcp_pass_normally(runner):
    def correct_native(method, value):
        if (
            method == "textDocument/signatureHelp"
            and runner.calls[-1]["arguments"].get("column") == 33
        ):
            value["signatures"][0]["activeParameter"] = 1

    def correct_mcp(_root, tool, args, result):
        if tool == "ada_signature_help" and args.get("column") == 33:
            result["active_parameter"] = 1

    runner.native_mutation, runner.on_call = correct_native, correct_mcp
    result = real.run_control(runner.output, True)
    row = next(row for row in result["calls"] if row["label"] == "positional-initial-1")
    assert row["accepted"] is True and result["semantic_acceptance"] is False
    assert len(result["native_blockers"]) == 2
    assert sum(row["accepted"] is True for row in result["calls"]) == 51
    native = real.native_result(row["native_events"], "textDocument/signatureHelp")
    assert native["activeParameter"] == 0 and native["signatures"][0]["activeParameter"] == 1


def test_semantically_correct_mcp_cannot_hide_wrong_effective_native(runner):
    def alter_mcp(_root, tool, args, result):
        if tool == "ada_signature_help" and args.get("column") == 33:
            result["active_parameter"] = 1

    runner.on_call = alter_mcp
    with pytest.raises(
        RuntimeError, match="MCP signature indices must equal effective native indices"
    ):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["native_blockers"] == [] and result["calls"][-1]["accepted"] is False


@pytest.mark.parametrize(
    "variation", ["different-top", "missing-top", "missing-per", "missing-selected"]
)
def test_new_raw_native_variation_cannot_use_original_blocker(runner, variation):
    def alter_native(method, value):
        if (
            method != "textDocument/signatureHelp"
            or runner.calls[-1]["arguments"].get("column") != 33
        ):
            return
        if variation == "different-top":
            value["activeParameter"] = 1
        elif variation == "missing-top":
            del value["activeParameter"]
        elif variation == "missing-per":
            del value["signatures"][0]["activeParameter"]
        else:
            del value["activeSignature"]

    runner.native_mutation = alter_native
    with pytest.raises(RuntimeError, match="original native defect envelope"):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["native_blockers"] == [] and result["calls"][-1]["accepted"] is False


def test_native_zero_with_mcp_false_is_never_a_native_blocker(runner):
    def convert_index(_root, tool, args, result):
        if tool == "ada_signature_help" and args.get("column") == 33:
            result["active_parameter"] = False

    runner.on_call = convert_index
    with pytest.raises(RuntimeError, match="signature indices must be integers"):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["native_blockers"] == [] and result["calls"][-1]["accepted"] is False


def test_unused_oversized_native_top_is_rejected_before_healthy_classification(runner):
    def alter_native(method, value):
        if (
            method == "textDocument/signatureHelp"
            and runner.calls[-1]["arguments"].get("column") == 30
        ):
            value["activeParameter"] = 2147483648

    runner.native_mutation = alter_native
    with pytest.raises(RuntimeError, match="signature indices must be integers"):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["native_blockers"] == [] and result["calls"][-1]["accepted"] is False


def test_action_execution_is_rejected_inside_the_call_acceptance_boundary(runner):
    injected = False

    def execute(root, tool, args, _result):
        nonlocal injected
        if not injected and tool == "ada_code_actions" and args.get("start_line") == 5:
            injected = True
            with (root.parent / "native-requests.jsonl").open("a") as stream:
                for row in (
                    {
                        "event": "request",
                        "id": 999,
                        "method": "workspace/executeCommand",
                        "params": {"command": "als-named-parameters"},
                    },
                    {
                        "event": "result",
                        "id": 999,
                        "method": "workspace/executeCommand",
                        "result": None,
                    },
                ):
                    stream.write(json.dumps(row) + "\n")

    runner.on_call = execute
    with pytest.raises(RuntimeError, match="must not execute action commands"):
        real.run_control(runner.output, True)
    row = report(runner)["calls"][-1]
    assert row["accepted"] is False and "oracle_error" in row


def test_build_call_rejects_generation_outside_owned_obj_bin(runner):
    def generate(root, tool, _args, _result):
        if tool == "ada_build":
            (root / "stray.o").write_bytes(b"unowned generated output")

    runner.on_call = generate
    with pytest.raises(RuntimeError, match="outside its allowed owned build outputs"):
        real.run_control(runner.output, True)
    row = report(runner)["calls"][-1]
    assert row["tool"] == "ada_build" and row["changed_files"]
    assert row["accepted"] is False


@pytest.mark.parametrize("alteration", ["label", "file", "line", "column", "state", "parameter"])
def test_native_blocker_allowance_rejects_unevidenced_case(tmp_path, alteration):
    root = tmp_path / "fixture"
    file = root / "src/main.adb"
    context = {
        "label": "positional-initial-1",
        "file": file,
        "line": 5,
        "column": 33,
        "changed": False,
        "parameter": 1,
    }
    result = signature_result(False, 0)
    events = [
        {
            "event": "request",
            "id": 1,
            "method": "textDocument/signatureHelp",
            "params": {
                "textDocument": {"uri": file.as_uri()},
                "position": {"line": 4, "character": 32},
            },
        },
        {
            "event": "result",
            "id": 1,
            "method": "textDocument/signatureHelp",
            "result": known_native(),
        },
    ]
    real.require_known_positional_blocker(result, events, root, **context)
    key = "changed" if alteration == "state" else alteration
    context[key] = {
        "label": "another-position",
        "file": root / "formatting/named.adb",
        "line": 6,
        "column": 34,
        "changed": True,
        "parameter": 2,
    }[key]
    with pytest.raises(AssertionError, match="outside the three evidenced native cases"):
        real.require_known_positional_blocker(result, events, root, **context)


@pytest.mark.parametrize(
    "method", ["textDocument/rename", "textDocument/codeAction", "callHierarchy/outgoingCalls"]
)
def test_native_corruption_is_unaccepted_even_with_healthy_mcp_summary(runner, method):
    injected = False

    def corrupt(native_method, value):
        nonlocal injected
        if native_method != method or injected:
            return
        injected = True
        if method == "textDocument/rename":
            next(iter(value["changes"].values()))[0]["newText"] = "WRONG"
        elif method == "textDocument/codeAction":
            value[0]["command"]["command"] = "wrong-command"
        else:
            value[0]["fromRanges"][0]["start"]["line"] += 1

    runner.native_mutation = corrupt
    with pytest.raises(
        RuntimeError,
        match=(
            "native rename ranges|native named-parameter action proposal|"
            "native complete call-site ranges|native/MCP result fidelity for ada_rename_symbol"
        ),
    ):
        real.run_control(runner.output, True)
    row = report(runner)["calls"][-1]
    assert row["accepted"] is False and "oracle_error" in row and row["inputs_unchanged"] is True
    assert row["raw_result"] and row["native_events"]
    assert runner.close_count == runner.cleanup_count == 1


@pytest.mark.parametrize(
    "filename",
    ["src/main.adb", "additional.gpr", "manifest/alire.toml", "states/main-after.adb", "stray.o"],
)
def test_runner_rejects_and_retains_unexpected_input_changes(runner, filename):
    def change(root, tool, _args, _result):
        if tool == "ada_call_hierarchy":
            (root / filename).write_text("unexpected change\n")

    runner.on_call = change
    with pytest.raises(RuntimeError, match="outside its allowed owned build outputs"):
        real.run_control(runner.output, True)
    row = report(runner)["calls"][-1]
    assert row["accepted"] is False and row["changed_files"] == [filename] and row["raw_result"]
    assert runner.close_count == runner.cleanup_count == 1


@pytest.mark.parametrize(
    "filename", ["src/main.adb", "additional.gpr", "manifest/alire.toml", "states/main-after.adb"]
)
def test_runner_rejects_input_deletion_with_available_results(runner, filename):
    def delete(root, tool, _args, _result):
        if tool == "ada_call_hierarchy":
            (root / filename).unlink()

    runner.on_call = delete
    with pytest.raises(RuntimeError, match="outside its allowed owned build outputs"):
        real.run_control(runner.output, True)
    row = report(runner)["calls"][-1]
    assert row["accepted"] is False and row["raw_result"]
    assert filename in row["file_sha256_before"] and filename not in row["file_sha256_after"]


def test_runner_budget_uses_a_private_clock_and_keeps_eof_evidence(runner, monkeypatch):
    times = iter([0])
    monkeypatch.setattr(real, "time", SimpleNamespace(monotonic=lambda: next(times, 601)))
    with pytest.raises(RuntimeError, match="exceeded its total request budget"):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["calls"] == [] and result["eof_exit"] == 0
    assert runner.close_count == 1


def test_runner_never_replaces_existing_evidence(runner):
    runner.output.mkdir()
    marker = runner.output / "retained"
    marker.write_text("previous evidence\n")
    with pytest.raises(FileExistsError):
        real.run_control(runner.output, True)
    assert marker.read_text() == "previous evidence\n" and runner.close_count == 0


@pytest.mark.parametrize(
    "field", ["mcp_pid", "mcp_start_ticks", "als_pid", "als_start_ticks", "als_parent_pid"]
)
def test_runner_retains_changed_process_birth_before_rejection(runner, field):
    def change(_root, tool, _args, _result):
        if tool == "ada_call_hierarchy":
            runner.identity_change[field] = 999

    runner.on_call = change
    with pytest.raises(RuntimeError, match="process births changed during additional control"):
        real.run_control(runner.output, True)
    row = report(runner)["calls"][-1]
    assert row["process"][field] == 999 and row["accepted"] is False
    assert runner.close_count == runner.cleanup_count == 1


def test_runner_checks_final_process_birth(runner):
    runner.final_birth = True
    with pytest.raises(RuntimeError, match="at the end of additional control"):
        real.run_control(runner.output, True)
    assert report(runner)["final_process"]["als_start_ticks"] == 999


@pytest.mark.parametrize("failure", ["close", "cleanup", "original", "transport"])
def test_runner_retains_lifecycle_original_and_transport_failures(runner, failure):
    if failure == "close":
        runner.close_error = "mock EOF failure"
    elif failure == "cleanup":
        runner.cleanup_error = "mock child survived"
    elif failure == "transport":
        runner.request_error = True
    else:

        def change(_root, tool, _args, _result):
            if tool == "ada_call_hierarchy":
                (runner.original / "additional.gpr").write_text("changed original\n")

        runner.on_call = change
    with pytest.raises(RuntimeError):
        real.run_control(runner.output, True)
    result = report(runner)
    assert result["status"] == "failed" and result["error"]
    if failure == "close":
        assert result["eof_error"] == "RuntimeError: mock EOF failure"
    elif failure == "cleanup":
        assert result["cleanup_error"] == "RuntimeError: mock child survived"
    elif failure == "original":
        assert result["original_fixture_unchanged"] is False
    else:
        assert result["calls"][-1]["request_error"] == "TimeoutError: mock request timeout"
    assert runner.close_count == runner.cleanup_count == 1

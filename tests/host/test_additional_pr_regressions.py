"""Reject missing native proof and link escapes in the bounded fixture harness."""

import asyncio
import json
from pathlib import Path

import observe_additional as observation
import pytest
import real_additional as real
from additional_native import native_pairs

from ada_mcp.tools.project import handle_dependency_graph
from tests.host import test_additional_runner as runner_tests

runner = runner_tests.runner


@pytest.mark.parametrize("kind", ["root", "file", "directory", "dangling", "ancestor", "generated"])
def test_inspection_rejects_every_symlink(tmp_path, kind):
    owned = tmp_path / "owned"
    owned.mkdir()
    (owned / "src").mkdir()
    (owned / "src/main.adb").write_text("same bytes\n")
    external = tmp_path / "external"
    external.mkdir()
    (external / "main.adb").write_text("same bytes\n")
    if kind == "root":
        link = tmp_path / "root-link"
        link.symlink_to(owned, target_is_directory=True)
        inspected = link
    elif kind == "file":
        (owned / "src/main.adb").unlink()
        (owned / "src/main.adb").symlink_to(external / "main.adb")
        inspected = owned
    elif kind == "directory":
        (owned / "linked-dir").symlink_to(external, target_is_directory=True)
        inspected = owned
    elif kind == "dangling":
        (owned / "dangling").symlink_to(external / "missing")
        inspected = owned
    elif kind == "ancestor":
        link = tmp_path / "parent-link"
        link.symlink_to(tmp_path, target_is_directory=True)
        inspected = link / "owned"
    else:
        (owned / "obj").symlink_to(external, target_is_directory=True)
        inspected = owned
    with pytest.raises(AssertionError, match="symlink"):
        observation.file_hashes(inspected)


def test_same_byte_link_substitution_cannot_evade_change_guard(tmp_path):
    root = tmp_path / "owned"
    root.mkdir()
    path = root / "main.adb"
    path.write_text("same bytes\n")
    before = observation.file_hashes(root)
    external = tmp_path / "external.adb"
    external.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(external)
    with pytest.raises(AssertionError, match="symlink"):
        observation.require_changes(before, observation.file_hashes(root), allow_build=False)


def test_owned_mutation_never_follows_same_byte_external_link(runner, tmp_path):
    external = tmp_path / "external-format.adb"
    before = None

    def replace(root, tool, arguments, _result):
        nonlocal before
        if tool == "ada_format_file" and not external.exists():
            path = Path(arguments["file"])
            before = path.read_bytes()
            external.write_bytes(before)
            path.unlink()
            path.symlink_to(external)

    runner.on_call = replace
    failure = None
    try:
        real.run_control(runner.output, allow_positional_blocker=True)
    except RuntimeError as error:
        failure = str(error)
    finally:
        (tmp_path / "external-write-observation.json").write_text(
            json.dumps(
                {
                    "rejected": failure,
                    "before": before.decode() if before else None,
                    "after": external.read_text() if external.exists() else None,
                },
                indent=2,
            )
            + "\n"
        )
    assert failure is not None and "symlink" in failure
    assert external.read_bytes() == before


@pytest.mark.parametrize(
    "tool",
    [
        "ada_project_info",
        "ada_document_symbols",
        "ada_completions",
        "ada_format_file",
        "ada_get_spec",
    ],
)
def test_healthy_mcp_without_per_call_native_pair_is_rejected(runner, tool):
    def strip(root, current, arguments, _result):
        if current != tool or (tool == "ada_get_spec" and "line" not in arguments):
            return
        trace = root.parent / "native-requests.jsonl"
        rows = [json.loads(line) for line in trace.read_text().splitlines()]
        methods = {
            "ada_project_info": {"workspace/executeCommand"},
            "ada_document_symbols": {"textDocument/documentSymbol"},
            "ada_completions": {"textDocument/completion"},
            "ada_format_file": {"textDocument/formatting"},
            "ada_get_spec": {"textDocument/declaration"},
        }[tool]
        trace.write_text(
            "".join(json.dumps(row) + "\n" for row in rows if row.get("method") not in methods)
        )

    runner.on_call = strip
    with pytest.raises(RuntimeError, match="native"):
        real.run_control(runner.output, allow_positional_blocker=True)


@pytest.mark.parametrize(
    "character",
    [
        "Character'('\"')",
        "Character '('\"')",
        "Character' ( '\"' )",
        "'\"'",
        "Character'('(')",
        "Character'First",
    ],
)
def test_qualified_quote_character_keeps_following_string_masked(tmp_path, character):
    path = tmp_path / "actual.adb"
    text = (
        f"pragma Compile_Time_Warning ({character} = Character'First, "
        '"procedure False_Unit");\nwith Visible;\n'
        "procedure Actual is begin null; end Actual;\n"
    )
    path.write_text(text)
    assert asyncio.run(handle_dependency_graph(str(path))) == {
        "dependencies": [{"package": "Actual", "file": str(path), "depends_on": ["Visible"]}],
        "package_count": 1,
    }
    assert path.read_text() == text


def test_mutation_checks_entire_batch_before_first_write(tmp_path):
    root = tmp_path / "owned"
    root.mkdir()
    first, second = root / "first.adb", root / "second.adb"
    first.write_bytes(b"first\n")
    external = tmp_path / "external.adb"
    external.write_bytes(b"second\n")
    second.symlink_to(external)
    with pytest.raises(AssertionError, match="symlink"):
        observation.mutate_owned(root, {first: b"changed first\n", second: b"changed second\n"})
    assert first.read_bytes() == b"first\n" and external.read_bytes() == b"second\n"


@pytest.mark.parametrize("ident", range(1, 58))
def test_each_native_pair_is_mandatory_inside_its_call(runner, ident):
    injected = False

    def remove(root, _tool, _arguments, _result):
        nonlocal injected
        path = root.parent / "native-requests.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if injected or not any(row["id"] == ident for row in rows):
            return
        path.write_text("".join(json.dumps(row) + "\n" for row in rows if row["id"] != ident))
        injected = True

    runner.on_call = remove
    with pytest.raises(RuntimeError, match="native"):
        real.run_control(runner.output, allow_positional_blocker=True)
    report = runner_tests.report(runner)
    assert injected and report["calls"][-1]["accepted"] is False
    assert report["calls"][-1]["oracle_error"]


@pytest.mark.parametrize("ident", [17, 33, 35, 7, 24, 26, 32])
def test_wrong_native_reply_never_inherits_a_healthy_mcp_result(runner, ident):
    def corrupt(root, _tool, _arguments, _result):
        path = root.parent / "native-requests.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for row in rows:
            if row["event"] == "result" and row["id"] == ident:
                row["result"] = {"deliberately_wrong_native_result": True}
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    runner.on_call = corrupt
    with pytest.raises(RuntimeError):
        real.run_control(runner.output, allow_positional_blocker=True)
    report = runner_tests.report(runner)
    assert report["calls"][-1]["accepted"] is False
    assert report["calls"][-1]["oracle_error"]


@pytest.mark.parametrize(
    "method",
    [
        "workspace/executeCommand",
        "textDocument/documentSymbol",
        "textDocument/completion",
        "textDocument/formatting",
        "textDocument/declaration",
        "textDocument/codeAction",
        "textDocument/prepareRename",
    ],
)
def test_valid_native_shape_with_wrong_fields_fails_mcp_fidelity(runner, method):
    def corrupt(current, value):
        if current != method:
            return
        if method == "workspace/executeCommand":
            if isinstance(value, dict):
                value["projects"][0]["project"]["name"] = "Wrong_Project"
        elif method == "textDocument/documentSymbol":
            value[0]["name"] = "Wrong_Package"
        elif method == "textDocument/completion":
            value["items"][0]["label"] = "Wrong_Member"
        elif method == "textDocument/formatting":
            if value:
                value[0]["newText"] = "      null;\n"
        elif method == "textDocument/declaration":
            value["range"]["start"]["character"] += 1
        elif method == "textDocument/codeAction":
            if value:
                value[0]["kind"] = "quickfix"
        elif value is not None:
            value["placeholder"] = "Wrong_Token"

    runner.native_mutation = corrupt
    with pytest.raises(RuntimeError, match="native.*fidelity"):
        real.run_control(runner.output, allow_positional_blocker=True)
    report = runner_tests.report(runner)
    assert report["calls"][-1]["accepted"] is False
    assert report["calls"][-1]["oracle_error"]


@pytest.mark.parametrize(
    "method",
    [
        "textDocument/completion",
        "textDocument/formatting",
        "textDocument/declaration",
        "callHierarchy/outgoingCalls",
    ],
)
def test_native_request_parameters_must_match_the_actual_call(runner, method):
    def corrupt(root, _tool, _arguments, _result):
        path = root.parent / "native-requests.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for row in rows:
            if row["event"] == "request" and row["method"] == method:
                row["params"] = {"wrong_request_parameters": True}
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    runner.on_call = corrupt
    with pytest.raises(RuntimeError, match="native.*request"):
        real.run_control(runner.output, allow_positional_blocker=True)
    report = runner_tests.report(runner)
    assert report["calls"][-1]["accepted"] is False


@pytest.mark.parametrize("defect", ["request-bool", "reply-bool", "method", "error", "orphan"])
def test_native_pairs_reject_bad_correlation_before_semantic_use(defect):
    rows = [
        {"event": "request", "id": 1, "method": "fixture", "params": {}},
        {"event": "result", "id": 1, "method": "fixture", "result": None},
    ]
    if defect == "request-bool":
        rows[0]["id"] = True
    elif defect == "reply-bool":
        rows[1]["id"] = True
    elif defect == "method":
        rows[1]["method"] = "different"
    elif defect == "error":
        rows[1]["event"] = "error"
    else:
        rows.pop()
    with pytest.raises(AssertionError, match="native.*pairs"):
        native_pairs(rows)

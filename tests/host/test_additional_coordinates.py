"""Reject malformed native coordinates before Python arithmetic or set aliases."""

import copy
import json

import additional_native as native
import additional_oracles as oracle
import pytest
import real_additional as real

from tests.host import test_additional_runner as runner_tests

runner = runner_tests.runner

BAD_NATIVE = [False, True, 0.0, 1.0, None, "0", -1, 2_147_483_648]


def coordinate_events(position, context):
    """Build protocol data only; these are domain controls, not native execution."""
    request = {"event": "request", "id": 1, "method": "fixture", "params": {}}
    reply = {"event": "result", "id": 1, "method": "fixture", "result": None}
    if context == "request":
        request["params"] = {"position": position}
    elif context == "selection-end":
        reply["result"] = [
            {"selectionRange": {"start": {"line": 0, "character": 0}, "end": position}}
        ]
    elif context == "action-argument":
        reply["result"] = [
            {
                "command": {
                    "command": "als-named-parameters",
                    "arguments": [{"where": {"position": position}}],
                }
            }
        ]
    elif context == "completion-edit":
        reply["result"] = {
            "items": [
                {
                    "additionalTextEdits": [
                        {"range": {"start": position, "end": {"line": 0, "character": 0}}}
                    ]
                }
            ]
        }
    else:
        reply["result"] = {
            "documentChanges": [
                {"edits": [{"range": {"start": {"line": 0, "character": 0}, "end": position}}]}
            ]
        }
    return [request, reply]


@pytest.mark.parametrize(
    "context",
    [
        "request",
        "selection-end",
        "action-argument",
        "completion-edit",
        "rename-end",
    ],
)
@pytest.mark.parametrize("field", ["line", "character"])
@pytest.mark.parametrize("value", BAD_NATIVE)
def test_all_nested_raw_positions_reject_malformed_coordinates(context, field, value):
    position = {"line": 0, "character": 0, field: value}
    with pytest.raises(AssertionError, match="native coordinates"):
        native.native_pairs(coordinate_events(position, context))


@pytest.mark.parametrize(
    "context",
    [
        "request",
        "selection-end",
        "action-argument",
        "completion-edit",
        "rename-end",
    ],
)
@pytest.mark.parametrize("line,character", [(0, 0), (0, 2_147_483_647), (2_147_483_647, 0)])
def test_zero_and_max_remain_valid_raw_coordinates(context, line, character):
    assert (
        len(native.native_pairs(coordinate_events({"line": line, "character": character}, context)))
        == 1
    )


@pytest.mark.parametrize("context", ["request", "selection-end"])
@pytest.mark.parametrize("field", ["line", "character"])
def test_positions_require_both_raw_fields(context, field):
    with pytest.raises(AssertionError, match="native coordinates"):
        native.native_pairs(coordinate_events({field: 0}, context))


@pytest.mark.parametrize("value", [0, 2_147_483_647])
def test_valid_raw_boundaries_convert_to_one_based_symbol_and_edge_metadata(tmp_path, value):
    item = {
        "name": "Token",
        "kind": 12,
        "uri": (tmp_path / "source.adb").as_uri(),
        "range": {
            "start": {"line": value, "character": value},
            "end": {"line": value, "character": value},
        },
    }
    native.require_native_coordinates(item)
    expected = 1 if value == 0 else 2_147_483_648
    assert native._symbol(item)["line"] == native._edge(item)["line"] == expected
    assert native._symbol(item)["column"] == native._edge(item)["column"] == expected
    assert native._symbol(item)["range"] == {"start": expected, "end": expected}


@pytest.mark.parametrize("value", [0, 2_147_483_647])
def test_valid_raw_formatting_boundaries_retain_public_max_plus_one(tmp_path, value):
    path = tmp_path / "source.adb"
    position = {"line": value, "character": value}
    events = [
        {
            "event": "request",
            "id": 1,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {"uri": path.as_uri()},
                "options": {"tabSize": 3, "insertSpaces": True},
            },
        },
        {
            "event": "result",
            "id": 1,
            "method": "textDocument/formatting",
            "result": [{"range": {"start": position, "end": position}, "newText": "text"}],
        },
    ]
    expected = 1 if value == 0 else 2_147_483_648
    result = {
        "formatted": True,
        "file": str(path),
        "changes": 1,
        "edits": [
            {
                "start_line": expected,
                "start_column": expected,
                "end_line": expected,
                "end_column": expected,
                "new_text": "text",
            }
        ],
    }
    native.require_call_native(
        events,
        "ada_format_file",
        {"file": str(path)},
        result,
        tmp_path,
        real.require_native_signature,
    )


@pytest.mark.parametrize("shape", ["changes", "documentChanges"])
def test_standalone_native_rename_checks_endpoint_domain_before_set_alias(shape, tmp_path):
    path = tmp_path / "source.adb"
    path.write_text("T\n")
    edit = {
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": True}},
        "newText": "U",
    }
    workspace = (
        {"changes": {path.as_uri(): [edit]}}
        if shape == "changes"
        else {"documentChanges": [{"textDocument": {"uri": path.as_uri()}, "edits": [edit]}]}
    )
    events = [{"event": "result", "id": 1, "method": "textDocument/rename", "result": workspace}]
    with pytest.raises(AssertionError, match="native coordinates"):
        real.require_native_rename(events, {(str(path), 1, 1)}, "T", "U")


def test_standalone_call_sites_validate_unused_callee_extent(tmp_path):
    path = tmp_path / "source.adb"
    path.write_text("T\n")
    extent = {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 1}}
    item = {"name": "T", "range": copy.deepcopy(extent)}
    item["range"]["start"]["line"] = False
    events = [
        {
            "event": "result",
            "id": 1,
            "method": "callHierarchy/outgoingCalls",
            "result": [{"to": item, "fromRanges": [extent]}],
        }
    ]
    with pytest.raises(AssertionError, match="native coordinates"):
        real.require_native_calls(events, "outgoing", path, {"T": [(1, 1)]})


@pytest.mark.parametrize("value", [True, False, 0, 1.0, None, "1", -1, 2_147_483_649])
def test_one_based_set_oracle_domain_has_its_own_offset(value):
    with pytest.raises(AssertionError, match="one-based source coordinates"):
        oracle._require_mcp_location({"line": value, "column": 1})


def test_one_based_max_plus_one_is_valid_before_physical_source_checks(tmp_path):
    oracle._require_mcp_location({"line": 2_147_483_648, "column": 2_147_483_648})
    path = tmp_path / "one.adb"
    path.write_text("Token\n")
    with pytest.raises(AssertionError, match="exact source token"):
        oracle.require_token((str(path), 2_147_483_648, 1), "Token")


def test_completion_data_stays_opaque_even_with_coordinate_named_fields(runner):
    def metadata(method, value):
        if method == "textDocument/completion" and isinstance(value, dict):
            for item in value["items"]:
                item["data"] = {"line": "opaque", "character": None, "range": {"start": "opaque"}}

    runner.native_mutation = metadata
    report = real.run_control(runner.output, allow_positional_blocker=True)
    assert len(report["calls"]) == 53 and sum(row["accepted"] for row in report["calls"]) == 50
    assert len(report["native_blockers"]) == 3


def test_unknown_command_arguments_are_opaque_protocol_data():
    value = {
        "command": "third-party-command",
        "arguments": [
            {
                "line": "opaque",
                "character": None,
                "position": {"line": "opaque"},
                "where": {"position": {"line": "opaque"}},
                "range": {"start": "opaque"},
            }
        ],
    }
    native.require_native_coordinates(value)


@pytest.mark.parametrize("key", ["targetRange", "targetSelectionRange", "originSelectionRange"])
def test_location_link_unused_endpoints_keep_the_same_domain(key):
    extent = {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 2_147_483_648}}
    with pytest.raises(AssertionError, match="native coordinates"):
        native.require_native_coordinates({"targetUri": "file:///source.ads", key: extent})


@pytest.mark.parametrize(
    "method",
    [
        "textDocument/documentSymbol",
        "callHierarchy/outgoingCalls",
        "textDocument/rename",
        "textDocument/formatting",
        "textDocument/declaration",
    ],
)
def test_native_boolean_coordinates_cannot_become_healthy_integer_outputs(runner, method):
    altered = False

    def corrupt(current, value):
        nonlocal altered
        if current != method or altered:
            return
        if method == "textDocument/documentSymbol":
            value[0]["range"]["start"]["line"] = False
        elif method == "callHierarchy/outgoingCalls":
            value[1]["to"]["range"]["start"]["line"] = True
        elif method == "textDocument/rename":
            first = next(iter(value["changes"].values()))[0]["range"]["start"]
            if first["line"] != 1:
                return
            first["line"] = True
        elif method == "textDocument/formatting":
            value[0]["range"]["start"]["character"] = False
        else:
            value["range"]["start"]["line"] = True
        altered = True

    runner.native_mutation = corrupt
    with pytest.raises(RuntimeError):
        real.run_control(runner.output, allow_positional_blocker=True)
    assert altered
    report = runner_tests.report(runner)
    assert report["calls"][-1]["accepted"] is False


def test_one_based_rename_set_comparison_cannot_accept_true_as_one(tmp_path):
    source = tmp_path / "one.adb"
    source.write_text("Token\n")
    result = {
        "success": True,
        "applied": False,
        "old_name": "Token",
        "new_name": "Other",
        "changes": [
            {
                "file": str(source),
                "line": True,
                "column": True,
                "old_text": "Token",
                "new_text": "Other",
            }
        ],
        "total_changes": 1,
        "files_affected": 1,
    }
    with pytest.raises(AssertionError):
        oracle.require_rename(result, "Token", "Other", {(str(source), 1, 1)})


def test_one_based_hierarchy_set_comparison_cannot_accept_true_as_one(tmp_path):
    source = tmp_path / "one.adb"
    source.write_text("Token\n")
    result = {
        "found": True,
        "symbol": "Main",
        "outgoing_count": 1,
        "incoming_count": 0,
        "outgoing_calls": [
            {"name": "Token", "kind": 12, "file": str(source), "line": True, "column": True}
        ],
        "incoming_calls": [],
    }
    with pytest.raises(AssertionError):
        oracle.require_hierarchy(result, "Main", {("Token", 12, str(source), 1, 1)}, set())


def test_existing_strict_request_equality_rejects_bool_alias(runner):
    def corrupt(root, tool, args, _result):
        if tool != "ada_code_actions" or args["start_line"] != 2:
            return
        p = root.parent / "native-requests.jsonl"
        rows = [json.loads(line) for line in p.read_text().splitlines()]
        for row in rows:
            if row["event"] == "request" and row["method"] == "textDocument/codeAction":
                row["params"]["range"]["start"]["line"] = True
        p.write_text("".join(json.dumps(row) + "\n" for row in rows))

    runner.on_call = corrupt
    with pytest.raises(RuntimeError):
        real.run_control(runner.output, allow_positional_blocker=True)

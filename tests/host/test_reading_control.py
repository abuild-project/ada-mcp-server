"""Mocked guards for the live reading probe's oracles; no real ALS proof here."""

import copy
import json
import shutil

import mcp_client
import pytest
import real_reading as reading


@pytest.fixture
def fixture(tmp_path):
    root = tmp_path / "fixture"
    shutil.copytree(reading.FIXTURE, root)
    return root


def location(source, line, column):
    return {
        "found": True,
        "file": str(source),
        "line": line,
        "column": column,
        "preview": source.read_text().splitlines()[line - 1].rstrip(),
    }


@pytest.mark.parametrize(
    ("relative", "line", "column", "token"),
    [
        ("reading.ads", 5, 14, "Reading_Probe_Increment"),
        ("reading.adb", 2, 14, "Reading_Probe_Increment"),
        ("reading.ads", 2, 9, "Counter"),
        ("main.adb", 3, 4, "Item"),
        ("main.adb", 6, 40, "Item"),
        ("main.adb", 6, 15, "Reading_Probe_Increment"),
    ],
)
def test_navigation_oracle_binds_fixture_token_and_rejects_displaced_target(
    fixture, relative, line, column, token
):
    source = fixture / "src" / relative
    result = location(source, line, column)
    expected = (str(source), line, column)
    reading.require_location(result, expected, token)
    for change in ({"found": False}, {"column": column + 1}, {"preview": "unrelated"}):
        with pytest.raises(AssertionError):
            reading.require_location({**result, **change}, expected, token)


def test_reference_oracle_checks_declaration_flag_duplicates_and_unrelated_name(fixture):
    main = fixture / "src/main.adb"
    declaration = location(main, 3, 4)
    usage = location(main, 6, 40)
    expected = {(str(main), 3, 4), (str(main), 6, 40)}
    result = {"references": [usage, declaration], "count": 2}
    reading.require_references(result, expected, "Item")
    reading.require_references({"references": [usage], "count": 1}, {(str(main), 6, 40)}, "Item")
    unrelated = location(fixture / "src/unrelated.adb", 2, 4)
    for wrong in (
        {"references": [], "count": 0},
        {"references": [usage], "count": 1},
        {"references": [usage, declaration, declaration], "count": 3},
        {"references": [usage, unrelated], "count": 2},
        {"references": [usage, declaration], "count": 1},
    ):
        with pytest.raises(AssertionError, match="reference set"):
            reading.require_references(wrong, expected, "Item")
    with pytest.raises(AssertionError, match="reference set"):
        reading.require_references(result, {(str(main), 6, 40)}, "Item")


def document(object_name="Item"):
    return {
        "symbols": [
            {
                "name": "Main",
                "kind": "function",
                "line": 2,
                "column": 11,
                "children": [
                    {"name": object_name, "kind": "variable", "line": 3, "column": 4},
                    {"name": "Step", "kind": "function", "line": 4, "column": 14},
                ],
            },
            {"name": "With clauses", "kind": "namespace"},
        ]
    }


@pytest.mark.parametrize("corruption", ["empty", "kind", "position", "hierarchy", "duplicate"])
def test_document_oracle_rejects_wrong_structure(corruption):
    result = document()
    reading.require_document(result, "Item")
    wrong = copy.deepcopy(result)
    if corruption == "empty":
        wrong["symbols"] = []
    elif corruption == "kind":
        wrong["symbols"][0]["children"][0]["kind"] = "function"
    elif corruption == "position":
        wrong["symbols"][0]["children"][0]["column"] = 5
    elif corruption == "hierarchy":
        wrong["symbols"].append(wrong["symbols"][0]["children"].pop())
    else:
        wrong["symbols"].append(copy.deepcopy(wrong["symbols"][0]))
    with pytest.raises(AssertionError, match="document hierarchy|namespace envelope"):
        reading.require_document(wrong, "Item")


def test_mutated_source_rejects_old_document_hover_and_reference_payloads(fixture):
    main = fixture / "src/main.adb"
    old = {"references": [location(main, 6, 40)], "count": 1}
    main.write_text(main.read_text().replace("Item", "Other"))
    reading.require_document(document("Other"), "Other")
    reading.require_hover(
        {
            "found": True,
            "contents": "Other : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
        },
        "Other",
        main,
    )
    with pytest.raises(AssertionError, match="document hierarchy"):
        reading.require_document(document(), "Other")
    with pytest.raises(AssertionError, match="queried object"):
        reading.require_hover(
            {
                "found": True,
                "contents": "Item : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
            },
            "Other",
            main,
        )
    with pytest.raises(AssertionError, match="preview"):
        reading.require_references(old, {(str(main), 6, 40)}, "Other")


@pytest.mark.parametrize("name", ["Item", "Other"])
def test_hover_oracle_accepts_exact_pinned_als_source_payload(fixture, name):
    """Replay the two captured presentation shapes as mocked guard evidence."""
    main = fixture / "src/main.adb"
    main.write_text(main.read_text().replace("Item", name))
    reading.require_hover(
        {
            "found": True,
            "contents": f"{name} : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
        },
        name,
        main,
    )


@pytest.mark.parametrize(
    "contents",
    [
        "OtherItem : Reading.Counter",
        "Item : Reading.Counterfeit",
        "Item : Integer; -- Counter",
        "OtherItem : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
        "ItemOther : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
        "Item : Reading.Counterfeit := (Value => 0);\nat main.adb (3:4)",
        "Item : Reading.OtherCounter := (Value => 0);\nat main.adb (3:4)",
        "Item : OtherReading.Counter := (Value => 0);\nat main.adb (3:4)",
        "Item : Integer; -- Reading.Counter\nat main.adb (3:4)",
        "-- Item : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
        "Item : Reading.Counter := (Value => 1);\nat main.adb (3:4)",
        "Item : Reading.Counter;\nat main.adb (3:4)",
        "Item : Reading.Counter := (Value => 0);\nat other.adb (3:4)",
        "Item : Reading.Counter := (Value => 0);\nat main.adb (4:4)",
        "Item : Reading.Counter := (Value => 0);\nat main.adb (3:5)",
        "Item : Reading.Counter := (Value => 0);",
        "Item : Reading.Counter := (Value => 0);\nat main.adb (3:4)\nOther text",
    ],
)
def test_hover_oracle_rejects_wrong_tokens_declaration_or_source_position(fixture, contents):
    with pytest.raises(AssertionError, match="queried object declaration and source position"):
        reading.require_hover(
            {"found": True, "contents": contents}, "Item", fixture / "src/main.adb"
        )


def test_hover_oracle_rejects_payload_unbound_from_fixture_source(fixture):
    main = fixture / "src/main.adb"
    main.write_text(main.read_text().replace("Reading.Counter", "Reading.Counterfeit"))
    with pytest.raises(AssertionError, match="fixture must contain"):
        reading.require_hover(
            {
                "found": True,
                "contents": "Item : Reading.Counter := (Value => 0);\nat main.adb (3:4)",
            },
            "Item",
            main,
        )


def test_workspace_oracle_rejects_wrong_set_and_incomplete_index(fixture):
    source = str(fixture / "src/reading.ads")
    symbol = {
        "name": "Reading_Probe_Increment",
        "kind": "function",
        "file": source,
        "line": 5,
        "column": 14,
    }
    expected = {("Reading_Probe_Increment", "function", source, 5, 14)}
    result = {"complete": True, "truncated": False, "symbols": [symbol], "count": 1}
    reading.require_workspace(result, expected)
    for change in (
        {"symbols": [], "count": 0},
        {"symbols": [symbol, symbol], "count": 2},
        {"symbols": [{**symbol, "kind": "variable"}]},
        {"symbols": [{**symbol, "line": 6}]},
        {"complete": False},
        {"truncated": True},
    ):
        with pytest.raises(AssertionError):
            reading.require_workspace({**result, **change}, expected)
    reading.require_workspace({**result, "symbols": [], "count": 0}, set())
    with pytest.raises(AssertionError):
        reading.require_workspace(result, set())


def test_negative_target_does_not_accept_found_or_error():
    reading.require_absent({"found": False})
    for wrong in ({}, {"found": True}, {"found": False, "error": "ALS failed"}):
        with pytest.raises(AssertionError, match="no navigation or hover target"):
            reading.require_absent(wrong)


def test_hashes_capture_only_source_changes(fixture):
    before = reading.source_hashes(fixture)
    (fixture / "generated.log").write_text("ALS log")
    assert reading.source_hashes(fixture) == before
    main = fixture / "src/main.adb"
    main.write_text(main.read_text().replace("Item", "Other"))
    after = reading.source_hashes(fixture)
    assert {name for name in before if before[name] != after[name]} == {"src/main.adb"}


def test_cleanup_checks_process_birth_and_rejects_a_surviving_zombie(monkeypatch):
    identity = {"als_pid": 42, "als_start_ticks": 100}
    monkeypatch.setattr(reading, "read_identity", lambda _: {"start_ticks": 101})
    assert reading.require_child_exit(identity)["pid_reused"] is True
    monkeypatch.setattr(reading, "read_identity", lambda _: {"start_ticks": 100, "state": "Z"})
    samples = iter((0, 6))
    monkeypatch.setattr(reading.time, "monotonic", lambda: next(samples))
    with pytest.raises(AssertionError, match="survived MCP EOF cleanup"):
        reading.require_child_exit(identity)


def test_failed_live_oracle_retains_result_summary_and_closes_session(tmp_path, monkeypatch):
    """A mocked empty definition fails the actual runner and retains its evidence."""
    closed = []

    class EmptyDefinition:
        def __init__(self, command, timeout, log_dir):
            pass

        def initialize(self):
            return {}

        def call(self, tool, arguments):
            if tool == "ada_project_info":
                root = tmp_path / "run/fixture"
                return {
                    "complete": True,
                    "project_file": str(root / "reading.gpr"),
                    "source_dirs": [str(root / "src")],
                    "main_units": ["main.adb"],
                }
            return {"found": False}

        def close(self):
            closed.append(True)
            return 0

    monkeypatch.setattr(mcp_client, "Session", EmptyDefinition)
    monkeypatch.setattr(reading, "process_state", lambda *_: {"als_pid": 42})
    monkeypatch.setattr(reading, "require_child_exit", lambda _: {"observed_child_exited": True})
    with pytest.raises(RuntimeError, match="expected location"):
        reading.run_control(tmp_path / "run")
    report = json.loads((tmp_path / "run/summary.json").read_text())
    assert report["status"] == "failed"
    assert report["calls"][-1]["result"] == {"found": False}
    assert report["calls"][-1]["sources_unchanged"] is True
    assert report["original_fixture_unchanged"] is True
    assert report["cleanup"]["observed_child_exited"] is True
    assert closed == [True]
    with pytest.raises(FileExistsError):
        reading.run_control(tmp_path / "run")

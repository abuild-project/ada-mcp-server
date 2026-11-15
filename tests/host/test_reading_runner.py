"""Full-runner guard controls with mocked semantics, never live ALS evidence."""

import copy
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import mcp_client
import pytest
import real_reading as reading

from tests.host.test_reading_control import document, location, project


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """Supply valid semantic replies while exposing owned mutation boundaries."""
    original = tmp_path / "original-fixture"
    shutil.copytree(reading.FIXTURE, original)
    monkeypatch.setattr(reading, "FIXTURE", original)
    control = SimpleNamespace(
        original=original,
        output=tmp_path / "run",
        calls=[],
        close_count=0,
        close_error=None,
        on_call=None,
        observations=[],
        identity_change={},
        identity_at=2,
        cleanup=[],
    )
    baseline = {
        "mcp_pid": 7001,
        "mcp_start_ticks": 100,
        "als_pid": 7002,
        "als_start_ticks": 200,
        "als_parent_pid": 7001,
        "observation": "proc-stat-parent-and-cmdline",
        "als_start_count": 1,
    }

    class SemanticSession:
        def __init__(self, command, timeout, log_dir):
            self.root = Path(log_dir).parent / "fixture"
            self.timeout = timeout
            Path(log_dir).mkdir()
            (Path(log_dir) / "server-stderr.log").write_text("INFO Starting ALS: mock\n")

        def initialize(self):
            return {"mock_initialize": True}

        def call(self, tool, arguments):
            result = self.response(tool, arguments)
            control.calls.append({"tool": tool, "arguments": copy.deepcopy(arguments)})
            if control.on_call is not None:
                control.on_call(self.root, tool, arguments)
            return result

        def response(self, tool, arguments):
            main = self.root / "src/main.adb"
            spec, body = self.root / "src/reading.ads", self.root / "src/reading.adb"
            state = (
                reading.CHANGED_STATE
                if "Alternate_Counter" in main.read_text()
                else reading.INITIAL_STATE
            )
            if tool == "ada_project_info":
                return project(self.root)
            if arguments.get("line") == state.comment_line:
                assert (
                    main.read_text().splitlines()[state.comment_line - 1].lstrip().startswith("--")
                )
                return {"found": False}
            if tool == "ada_goto_definition":
                if arguments["column"] == 15:
                    return location(spec, 5, 14)
                return location(main, state.declaration_line, 4)
            if tool == "ada_implementation":
                return location(body, 2, 14)
            if tool == "ada_document_symbols":
                return document(state) if arguments["file"] == str(main) else {"symbols": []}
            if tool == "ada_type_definition":
                return location(spec, state.type_line, 9)
            if tool == "ada_hover":
                return {
                    "found": True,
                    "contents": (
                        f"{state.object_name} : Reading.{state.type_name} := (Value => 0);\n"
                        f"at main.adb ({state.declaration_line}:4)"
                    ),
                }
            if tool == "ada_find_references":
                positions = list(state.references)
                if arguments["include_declaration"]:
                    positions.append((state.declaration_line, 4))
                return {
                    "references": [location(main, *position) for position in positions],
                    "count": len(positions),
                }
            if tool == "ada_workspace_symbols":
                symbols = []
                if arguments["query"] == "Reading_Probe_Increment":
                    symbols = [
                        {
                            "name": "Reading_Probe_Increment",
                            "kind": "function",
                            "file": str(source),
                            "line": line,
                            "column": 14,
                        }
                        for source, line in ((spec, 5), (body, 2))
                    ]
                return {
                    "complete": True,
                    "truncated": False,
                    "symbols": symbols,
                    "count": len(symbols),
                }
            assert tool == "ada_diagnostics"
            return {
                "complete": True,
                "scope": "file",
                "diagnostics": [],
                "errorCount": 0,
                "totalCount": 0,
            }

        def close(self):
            control.close_count += 1
            if control.close_error:
                raise RuntimeError(control.close_error)
            return 0

    def observe(_session, errors):
        assert errors.read_text() == "INFO Starting ALS: mock\n"
        observed = dict(baseline)
        if len(control.observations) >= control.identity_at:
            observed.update(control.identity_change)
        control.observations.append(observed)
        return observed

    def cleanup(identity):
        control.cleanup.append(identity)
        return {"als_pid": identity["als_pid"], "observed_child_exited": True}

    monkeypatch.setattr(mcp_client, "Session", SemanticSession)
    monkeypatch.setattr(reading, "process_state", observe)
    monkeypatch.setattr(reading, "require_child_exit", cleanup)
    return control


def summary(runner):
    return json.loads((runner.output / "summary.json").read_text())


def test_mocked_full_runner_passes_both_states_and_closes_once(runner):
    report = reading.run_control(runner.output)
    assert json.loads(json.dumps(report)) == summary(runner)
    assert report["status"] == "passed" and report["error"] is None
    assert report["original_fixture_unchanged"] is True
    assert report["stable_mcp_and_als"] is True
    assert len(report["calls"]) == 27
    assert len(report["states"]) == 2 and len(runner.observations) == 4
    for number, state in enumerate(reading.STATES):
        assert (runner.output / f"main-state-{number}.adb").read_bytes() == (
            runner.original / state.template
        ).read_bytes()
    assert all(call["sources_unchanged"] for call in report["calls"])
    assert runner.close_count == 1 and report["eof_exit"] == 0
    assert len(runner.cleanup) == 1 and report["cleanup"]["observed_child_exited"] is True


@pytest.mark.parametrize("mutation", ["ada", "gpr", "template", "add", "delete", "ada-eof-error"])
def test_call_source_mutation_fails_exact_hash_guard_and_retains_partial_evidence(runner, mutation):
    def mutate(root, tool, _arguments):
        if tool != "ada_goto_definition" or mutate.done:
            return
        mutate.done = True
        paths = {
            "ada": "src/unrelated.adb",
            "gpr": "reading.gpr",
            "template": "states/main-after.adb",
        }
        if mutation == "add":
            (root / "src/added.ads").write_text("package Added is end Added;\n")
        elif mutation == "delete":
            (root / "src/unrelated.adb").unlink()
        else:
            target = root / paths.get(mutation, "src/unrelated.adb")
            target.write_text(target.read_text() + "-- injected change\n")

    mutate.done = False
    runner.on_call = mutate
    if mutation == "ada-eof-error":
        runner.close_error = "injected EOF failure"
    expected = "AssertionError: a read-only query changed its Ada/GPR inputs"
    with pytest.raises(RuntimeError) as caught:
        reading.run_control(runner.output)
    assert str(caught.value) == expected
    report = summary(runner)
    assert report["status"] == "failed" and report["error"] == expected
    call = report["calls"][-1]
    assert call["tool"] == "ada_goto_definition"
    assert call["arguments"] == {
        "file": str(runner.output / "fixture/src/main.adb"),
        "line": 6,
        "column": 15,
    }
    assert call["result"]["found"] is True
    assert call["sources_unchanged"] is False
    assert call["source_sha256_before"] != call["source_sha256_after"]
    assert runner.close_count == 1 and report["cleanup"]["observed_child_exited"] is True
    assert report["original_fixture_unchanged"] is True
    if runner.close_error:
        assert report["eof_error"] == "RuntimeError: injected EOF failure"
    else:
        assert report["eof_exit"] == 0


@pytest.mark.parametrize(
    "changed",
    [
        {"mcp_pid": 8001, "als_parent_pid": 8001},
        {"mcp_start_ticks": 101},
        {"als_pid": 8002},
        {"als_start_ticks": 201},
    ],
)
def test_post_mutation_identity_comparison_rejects_each_changed_birth_field(runner, changed):
    runner.identity_change = changed
    expected = "AssertionError: MCP/ALS identities changed after source mutation"
    with pytest.raises(RuntimeError) as caught:
        reading.run_control(runner.output)
    assert str(caught.value) == expected
    report = summary(runner)
    assert report["error"] == expected and report["status"] == "failed"
    assert [state["object"] for state in report["states"]] == ["Item", "Other"]
    assert report["states"][0]["process"] != report["states"][1]["process"]
    assert len(runner.observations) == 3
    assert all(observed["als_start_count"] == 1 for observed in runner.observations)
    assert runner.close_count == 1 and report["eof_exit"] == 0
    assert report["cleanup"]["observed_child_exited"] is True


def test_final_no_target_identity_comparison_is_required(runner):
    runner.identity_at = 3
    runner.identity_change = {"als_start_ticks": 201}
    expected = "AssertionError: MCP/ALS identities changed during no-target queries"
    with pytest.raises(RuntimeError) as caught:
        reading.run_control(runner.output)
    assert str(caught.value) == expected
    report = summary(runner)
    assert report["final_process"] != report["states"][-1]["process"]
    assert report["error"] == expected and runner.close_count == 1


def test_mutating_only_owned_original_fixture_fails_finalization(runner):
    before = reading.source_hashes(runner.original)

    def mutate(_root, tool, _arguments):
        if tool == "ada_goto_definition" and not mutate.done:
            mutate.done = True
            source = runner.original / "src/unrelated.adb"
            source.write_text(source.read_text() + "-- changed original copy\n")

    mutate.done = False
    runner.on_call = mutate
    expected = "AssertionError: the original fixture changed"
    with pytest.raises(RuntimeError) as caught:
        reading.run_control(runner.output)
    assert str(caught.value) == expected
    report = summary(runner)
    assert report["status"] == "failed" and report["error"] == expected
    assert report["original_fixture_unchanged"] is False
    assert report["stable_mcp_and_als"] is True
    assert all(call["sources_unchanged"] for call in report["calls"])
    assert reading.source_hashes(runner.original) != before
    assert (
        reading.source_hashes(runner.output / "fixture")["src/unrelated.adb"]
        == before["src/unrelated.adb"]
    )
    assert runner.close_count == 1 and report["eof_exit"] == 0
    assert report["cleanup"]["observed_child_exited"] is True

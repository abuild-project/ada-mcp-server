"""Guard exploratory evidence boundaries without claiming live ALS semantics."""

import asyncio
import copy
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import mcp_client
import observe_additional as observation
import pytest


def test_input_hashes_include_templates_and_manifest_but_not_generated_sources(tmp_path):
    for name in (
        "src/main.adb",
        "additional.gpr",
        "manifest/alire.toml",
        "states/after.adb",
        "obj/b__main.adb",
        "bin/main",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    assert set(observation.input_hashes(tmp_path)) == {
        "src/main.adb",
        "additional.gpr",
        "manifest/alire.toml",
        "states/after.adb",
    }
    assert set(observation.file_hashes(tmp_path)) == {
        "src/main.adb",
        "additional.gpr",
        "manifest/alire.toml",
        "states/after.adb",
        "obj/b__main.adb",
        "bin/main",
    }


@pytest.mark.parametrize(
    "name", ["src/main.adb", "additional.gpr", "manifest/alire.toml", "states/after.adb", "stray.o"]
)
@pytest.mark.parametrize("operation", ["add", "change", "delete"])
def test_build_boundary_rejects_changes_outside_owned_outputs(name, operation):
    before = {} if operation == "add" else {name: "old"}
    after = {} if operation == "delete" else {name: "new"}
    with pytest.raises(AssertionError, match="outside its allowed owned build outputs"):
        observation.require_changes(before, after, allow_build=True)


@pytest.mark.parametrize("name", ["obj/main.o", "obj/b__main.adb", "bin/main"])
def test_only_build_calls_allow_owned_generated_changes(name):
    assert observation.require_changes({}, {name: "new"}, allow_build=True) == [name]
    with pytest.raises(AssertionError, match="outside its allowed owned build outputs"):
        observation.require_changes({}, {name: "new"}, allow_build=False)


@pytest.mark.parametrize(
    "payload", [{"found": False}, {"error": "method not found"}, {"actions": []}]
)
def test_decode_preserves_empty_and_error_observations(payload):
    assert observation.decode_result({"structuredContent": payload}) == payload
    assert (
        observation.decode_result({"content": [{"type": "text", "text": json.dumps(payload)}]})
        == payload
    )


@pytest.mark.parametrize(
    "raw", [{}, {"content": []}, {"content": [{"type": "text", "text": "not JSON"}]}]
)
def test_decode_rejects_missing_payload(raw):
    with pytest.raises(ValueError, match="no JSON object payload"):
        observation.decode_result(raw)


def test_native_trace_delegates_initialize_and_preserves_exception(tmp_path, monkeypatch):
    from ada_mcp import __main__ as entry
    from ada_mcp.als.client import ALSClient, LSPError

    calls = []
    capabilities = {"capabilities": {"renameProvider": {"prepareProvider": True}}}
    native_error = LSPError(-32601, "unsupported", {"native": "detail"})
    client = object.__new__(ALSClient)

    async def native(self, method, params=None):
        assert self is client
        calls.append((method, copy.deepcopy(params)))
        if method == "initialize":
            return capabilities
        raise native_error

    async def protocol():
        assert (
            await client.send_request("initialize", {"capabilities": {"unchanged": True}})
            is capabilities
        )
        with pytest.raises(LSPError) as caught:
            await client.send_request("textDocument/formatting", {"options": {"tabSize": 3}})
        assert caught.value is native_error

    monkeypatch.setattr(ALSClient, "send_request", native)
    monkeypatch.setattr(entry, "main", lambda: asyncio.run(protocol()))
    trace = tmp_path / "native.jsonl"
    observation.observed_server(trace)
    rows = [json.loads(line) for line in trace.read_text().splitlines()]
    assert calls == [
        ("initialize", {"capabilities": {"unchanged": True}}),
        ("textDocument/formatting", {"options": {"tabSize": 3}}),
    ]
    assert rows == [
        {"event": "request", "id": 1, "method": "initialize", "params": calls[0][1]},
        {"event": "result", "id": 1, "method": "initialize", "result": capabilities},
        {"event": "request", "id": 2, "method": "textDocument/formatting", "params": calls[1][1]},
        {
            "event": "error",
            "id": 2,
            "method": "textDocument/formatting",
            "type": "LSPError",
            "message": str(native_error),
            "code": -32601,
            "data": {"native": "detail"},
        },
    ]
    with pytest.raises(FileExistsError):
        observation.observed_server(trace)


@pytest.fixture
def runner(tmp_path, monkeypatch):
    original = tmp_path / "original-fixture"
    shutil.copytree(observation.FIXTURE, original)
    monkeypatch.setattr(observation, "FIXTURE", original)
    control = SimpleNamespace(
        output=tmp_path / "run",
        original=original,
        on_call=None,
        calls=[],
        close_count=0,
        cleanup_count=0,
        identity_change={},
        close_error=None,
    )
    identity = {"mcp_pid": 701, "mcp_start_ticks": 71, "als_pid": 702, "als_start_ticks": 72}

    class ExploratorySession:
        def __init__(self, command, timeout, log_dir):
            self.root = Path(log_dir).parent / "fixture"
            self.timeout = timeout
            Path(log_dir).mkdir()
            (Path(log_dir) / "server-stderr.log").write_text("mock process evidence\n")

        def initialize(self):
            return {"mock_initialize": True}

        def tools(self):
            return [{"name": "mock catalog"}]

        def request(self, method, params):
            assert method == "tools/call"
            tool, arguments = params["name"], params["arguments"]
            control.calls.append(copy.deepcopy(params))
            if control.on_call is not None:
                control.on_call(self.root, tool, arguments)
            payload = (
                {"complete": True, "project_file": str(self.root / "additional.gpr")}
                if tool == "ada_project_info"
                else {"error": "deliberately unaccepted mock capability"}
            )
            return {"content": [{"type": "text", "text": json.dumps(payload)}]}

        def close(self):
            control.close_count += 1
            if control.close_error:
                raise RuntimeError(control.close_error)
            return 0

    def process(*_args):
        return {**identity, **control.identity_change}

    def cleanup(_identity):
        control.cleanup_count += 1
        return {"observed_child_exited": True}

    monkeypatch.setattr(mcp_client, "Session", ExploratorySession)
    monkeypatch.setattr(observation, "process_state", process)
    monkeypatch.setattr(observation, "require_child_exit", cleanup)
    return control


def test_full_observation_keeps_semantic_failures_unaccepted(runner):
    report = observation.run_observation(runner.output)
    assert report["status"] == "observed" and report["semantic_acceptance"] is False
    assert len(report["calls"]) > 40 and all(row["inputs_unchanged"] for row in report["calls"])
    assert all(row["semantic_error"] for row in report["calls"][1:])
    assert report["original_fixture_unchanged"] is True
    assert "ADA_PROJECT_ROOT=" + str(runner.output / "fixture") in report["argv"]
    assert runner.close_count == runner.cleanup_count == 1
    labels = [row["label"] for row in report["calls"]]
    assert labels[1] == "cold-main-calls"
    assert labels.index("changed-cold-main-calls") + 1 == labels.index("changed-warm-source")
    assert [row["label"] for row in report["states"]] == [
        "initial",
        "warm-semantic-change",
        "restored-for-build",
        "deliberate-compiler-error",
    ]
    assert (
        report["states"][0]["files"]["src/main.adb"] == report["states"][2]["files"]["src/main.adb"]
    )
    assert len(report["client_denials"]) == 4
    assert json.loads((runner.output / "summary.json").read_text()) == report


@pytest.mark.parametrize(
    "name",
    ["src/main.adb", "additional.gpr", "manifest/alire.toml", "states/main-after.adb", "stray.o"],
)
def test_full_observation_rejects_and_preserves_unexpected_changes(runner, name):
    def mutate(root, tool, _arguments):
        if tool == "ada_call_hierarchy":
            (root / name).write_text("unexpected change\n")

    runner.on_call = mutate
    with pytest.raises(RuntimeError, match="outside its allowed owned build outputs"):
        observation.run_observation(runner.output)
    report = json.loads((runner.output / "summary.json").read_text())
    row = report["calls"][-1]
    assert row["tool"] == "ada_call_hierarchy" and row["changed_files"] == [name]
    assert "raw_result" in row and row["file_sha256_before"] != row["file_sha256_after"]
    assert runner.close_count == runner.cleanup_count == 1


def test_full_observation_allows_only_owned_compiler_products(runner):
    def generate(root, tool, _arguments):
        if tool == "ada_build":
            for name in ("obj/b__main.adb", "bin/main"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("mock compiler output\n")

    runner.on_call = generate
    report = observation.run_observation(runner.output)
    assert set(report["successful_build_files"]) == {"obj/b__main.adb", "bin/main"}
    assert report["calls"][-2]["inputs_unchanged"] is True


@pytest.mark.parametrize("field", ["mcp_pid", "mcp_start_ticks", "als_pid", "als_start_ticks"])
def test_full_observation_records_changed_process_birth_before_failure(runner, field):
    def change_birth(_root, tool, _arguments):
        if tool == "ada_call_hierarchy":
            runner.identity_change[field] = 999

    runner.on_call = change_birth
    with pytest.raises(RuntimeError, match="process births changed"):
        observation.run_observation(runner.output)
    report = json.loads((runner.output / "summary.json").read_text())
    assert report["calls"][-1]["process"][field] == 999
    assert runner.close_count == runner.cleanup_count == 1


def test_full_observation_rejects_original_fixture_change(runner):
    def change_original(_root, tool, _arguments):
        if tool == "ada_build":
            (runner.original / "additional.gpr").write_text("changed original\n")

    runner.on_call = change_original
    with pytest.raises(RuntimeError, match="original additional fixture changed"):
        observation.run_observation(runner.output)
    report = json.loads((runner.output / "summary.json").read_text())
    assert report["original_fixture_unchanged"] is False
    assert runner.close_count == runner.cleanup_count == 1


def test_full_observation_keeps_eof_failure(runner):
    runner.close_error = "mock EOF failure"
    with pytest.raises(RuntimeError, match="mock EOF failure"):
        observation.run_observation(runner.output)
    report = json.loads((runner.output / "summary.json").read_text())
    assert report["eof_error"] == "RuntimeError: mock EOF failure"
    assert runner.close_count == runner.cleanup_count == 1


def test_existing_output_is_never_replaced(runner):
    runner.output.mkdir()
    marker = runner.output / "previous-evidence"
    marker.write_text("retain\n")
    with pytest.raises(FileExistsError):
        observation.run_observation(runner.output)
    assert marker.read_text() == "retain\n" and runner.close_count == 0

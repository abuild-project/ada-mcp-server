"""Guard shared fixture evidence, native tracing and its retained CLI."""

import asyncio
import copy
import json
import sys
from pathlib import Path

import additional_support as support
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
    assert set(support.input_hashes(tmp_path)) == {
        "src/main.adb",
        "additional.gpr",
        "manifest/alire.toml",
        "states/after.adb",
    }
    assert set(support.file_hashes(tmp_path)) == {
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
        support.require_changes(before, after, allow_build=True)


@pytest.mark.parametrize("name", ["obj/main.o", "obj/b__main.adb", "bin/main"])
def test_only_build_calls_allow_owned_generated_changes(name):
    assert support.require_changes({}, {name: "new"}, allow_build=True) == [name]
    with pytest.raises(AssertionError, match="outside its allowed owned build outputs"):
        support.require_changes({}, {name: "new"}, allow_build=False)


@pytest.mark.parametrize(
    "payload", [{"found": False}, {"error": "method not found"}, {"actions": []}]
)
def test_decode_preserves_empty_and_error_observations(payload):
    assert support.decode_result({"structuredContent": payload}) == payload
    assert (
        support.decode_result({"content": [{"type": "text", "text": json.dumps(payload)}]})
        == payload
    )


@pytest.mark.parametrize(
    "raw", [{}, {"content": []}, {"content": [{"type": "text", "text": "not JSON"}]}]
)
def test_decode_rejects_missing_payload(raw):
    with pytest.raises(ValueError, match="no JSON object payload"):
        support.decode_result(raw)


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
    support.observed_server(trace)
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
        support.observed_server(trace)


def test_trace_cli_rejects_retired_output_before_dispatch_or_write(tmp_path, monkeypatch, capsys):
    output = tmp_path / "retired-output"

    def forbidden(*_args, **_kwargs):
        pytest.fail("retired --output must fail before dispatch or filesystem writes")

    monkeypatch.setattr(sys, "argv", ["observe_additional.py", "--output", str(output)])
    with monkeypatch.context() as guarded:
        guarded.setattr(support, "observed_server", forbidden)
        guarded.setattr(Path, "mkdir", forbidden)
        guarded.setattr(Path, "open", forbidden)
        with pytest.raises(SystemExit) as caught:
            observation.main()
    assert caught.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "error:" in captured.err
    assert list(tmp_path.iterdir()) == []


def test_trace_cli_dispatches_without_nonprotocol_stdout(tmp_path, monkeypatch, capsys):
    trace = tmp_path / "native.jsonl"
    calls = []
    protocol = '{"jsonrpc":"2.0","id":1,"result":{}}\n'

    def serve(path):
        calls.append(path)
        sys.stdout.write(protocol)

    monkeypatch.setattr(sys, "argv", ["observe_additional.py", "--serve-trace", str(trace)])
    monkeypatch.setattr(support, "observed_server", serve)
    observation.main()
    captured = capsys.readouterr()
    assert calls == [trace]
    assert captured.out == protocol and captured.err == ""

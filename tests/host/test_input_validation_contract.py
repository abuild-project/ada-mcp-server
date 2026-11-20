"""Pin SDK input validation through the real stdio server without running ALS."""

import json
import re
import shlex
import sys

import pytest
from mcp_client import Session

PREFIX = "Input validation error: "


@pytest.fixture
def server(tmp_path, monkeypatch):
    """Own a real server and an executable that only records attempted ALS startup."""
    source = tmp_path / "probe.adb"
    source.write_text("procedure Probe is begin null; end Probe;\n")
    gpr = tmp_path / "probe.gpr"
    gpr.write_text("project Probe is end Probe;\n")
    marker = tmp_path / "als-started"
    sentinel = tmp_path / "als-sentinel"
    sentinel.write_text("#!/bin/sh\nprintf 'started\\n' >> " + shlex.quote(str(marker)) + "\n")
    sentinel.chmod(0o700)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("ALS_PATH", str(sentinel))
    monkeypatch.setenv("ADA_PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("ADA_PROJECT_FILE", str(gpr))
    monkeypatch.setenv("ADA_PROJECT_SCENARIO_VARIABLES", "{}")
    monkeypatch.delenv("GPR_PROJECT_PATH", raising=False)
    logs = tmp_path / "protocol"
    session = Session([sys.executable, "-m", "ada_mcp"], timeout=15, log_dir=logs)
    try:
        initialized = session.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "input-validation-contract", "version": "1"},
            },
        )
        assert initialized["serverInfo"]["name"]
        session._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        yield session, source, gpr, marker
    finally:
        session.close()
        # Session rejects non-JSON stdout during requests. Check the complete
        # recorded stream too, including output received after the last reply.
        messages = [json.loads(line) for line in (logs / "protocol.jsonl").read_text().splitlines()]
        stdout = [
            json.loads(item["message"]) for item in messages if item["direction"] == "server-line"
        ]
        assert stdout
        assert all(
            isinstance(item, dict)
            and item.get("jsonrpc") == "2.0"
            and (
                isinstance(item.get("method"), str)
                or ("id" in item and ("result" in item or "error" in item))
            )
            for item in stdout
        )


@pytest.mark.parametrize(
    ("tool", "changes", "offending"),
    [
        ("ada_find_references", {"line": "5"}, r"line|\b5\b"),
        ("ada_find_references", {"include_declaration": "yes"}, r"include_declaration|yes"),
        ("ada_project_info", {"refresh": "true"}, r"refresh|true"),
        ("ada_hover", {"file": None}, r"file"),
        ("ada_document_symbols", None, r"file"),
        ("ada_call_hierarchy", {"direction": "sideways"}, r"direction|sideways"),
        ("ada_project_info", {"project_paths": [1]}, r"project_paths|\b1\b"),
        ("ada_project_info", {"scenario_variables": {"MODE": 1}}, r"MODE|\b1\b"),
    ],
)
def test_invalid_arguments_stop_before_als_and_keep_stdio_alive(server, tool, changes, offending):
    session, source, gpr, marker = server
    catalog = session.request("tools/list", {})
    assert tool in {item["name"] for item in catalog["tools"]}
    arguments = (
        {"gpr_file": str(gpr)}
        if tool == "ada_project_info"
        else {"file": str(source), "line": 5, "column": 1}
    )
    params = {"name": tool}
    if changes is not None:
        arguments.update(changes)
        if arguments.get("file") is None:
            arguments.pop("file", None)
        params["arguments"] = arguments
    # In particular, document-symbol arguments are omitted, not an empty object.
    # The handler's own strict refresh Boolean guard is currently shadowed by
    # SDK validation. Preserve it; this test observes the earlier stdio boundary.
    result = session.request("tools/call", params)
    assert result.get("isError") is True
    assert len(result["content"]) == 1
    content = result["content"][0]
    assert content["type"] == "text"
    assert content["text"].startswith(PREFIX)
    assert re.search(offending, content["text"][len(PREFIX) :])
    assert not marker.exists()
    assert session.process.poll() is None
    assert session.request("tools/list", {}) == catalog
    assert not marker.exists()


@pytest.mark.parametrize("case", ["valid", "extra-property", "refresh-false", "unknown-tool"])
def test_non_validation_controls_reach_existing_server_error(server, case):
    session, source, gpr, marker = server
    tool = "ada_project_info" if case == "refresh-false" else "ada_hover"
    arguments = (
        {"gpr_file": str(gpr), "refresh": False}
        if case == "refresh-false"
        else {"file": str(source), "line": 1, "column": 1}
    )
    catalog = session.request("tools/list", {})
    if case == "extra-property":
        schema = next(item["inputSchema"] for item in catalog["tools"] if item["name"] == tool)
        assert "additionalProperties" not in schema
        arguments["unused_contract_probe"] = True
    if case == "unknown-tool":
        tool = "ada_unknown_contract_probe"
    result = session.request("tools/call", {"name": tool, "arguments": arguments})
    assert result.get("isError", False) is False
    assert len(result["content"]) == 1
    content = result["content"][0]
    assert content["type"] == "text"
    assert not content["text"].startswith(PREFIX)
    payload = json.loads(content["text"])
    assert payload["error"]
    assert payload["context"]["tool"] == tool
    assert marker.read_text() == "started\n"
    assert session.process.poll() is None
    assert session.request("tools/list", {}) == catalog

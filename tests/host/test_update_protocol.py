"""Exercise notice delivery through real MCP stdio with mocked Ada semantics."""

import json
import sys
import time

import mcp_client
import pytest
from version import ROOT

from ada_mcp.update_notice import RELEASES


@pytest.mark.parametrize("kind", ["available", "absent", "forged", "oversized"])
def test_stdio_instructions_and_project_result_preserve_existing_payloads(
    tmp_path, monkeypatch, kind
):
    notice = {
        "schema": 1,
        "current_version": "0.2.0-rc.1",
        "available_version": "0.3.0",
        "channel": "prerelease",
        "checked_at": int(time.time()),
        "freshness": "fresh",
        "release_url": RELEASES + "0.3.0",
    }
    if kind == "forged":
        notice["release_url"] = "https://evil.invalid/"
    raw = "" if kind == "absent" else "x" * 3000 if kind == "oversized" else json.dumps(notice)
    monkeypatch.setenv("ADA_MCP_UPDATE_NOTICE", raw)
    monkeypatch.setenv("PYTHONPATH", str(ROOT / "src"))
    # No Docker, release checker or ALS is run: only the actual MCP transport.
    program = """
import asyncio
from unittest.mock import AsyncMock
import ada_mcp.server as module
module.server.instructions = 'Existing instructions are preserved.'
module.get_als_client = AsyncMock(return_value=object())
module.handle_project_info = AsyncMock(return_value={
    'complete': True, 'project_file': '/source/project.gpr', 'source_dirs': ['/source/src']})
module._als_pool.select_client = AsyncMock()
asyncio.run(module.run_server())
"""
    session = mcp_client.Session(
        [sys.executable, "-c", program], timeout=5, log_dir=tmp_path / "protocol"
    )
    try:
        initialized = session.initialize()
        result = session.call("ada_project_info", {"gpr_file": "/source/project.gpr"})
        assert len(session.tools()) == 19
        assert initialized["instructions"].startswith("Existing instructions are preserved.")
        assert result["complete"] is True
        assert result["project_file"] == "/source/project.gpr"
        assert result["source_dirs"] == ["/source/src"]
        if kind == "available":
            assert "0.3.0" in initialized["instructions"]
            assert "once per chat" in initialized["instructions"]
            assert result["update_notice"]["available_version"] == "0.3.0"
            assert result["update_notice"]["current_version"] == "0.2.0-rc.1"
            assert result["update_notice"]["release_url"] == RELEASES + "0.3.0"
        else:
            assert initialized["instructions"] == "Existing instructions are preserved."
            assert "update_notice" not in result
        assert "error" not in result
    finally:
        session.close()
    # The protocol reader would fail on an announcement printed outside JSON.
    events = [
        json.loads(line) for line in (tmp_path / "protocol/protocol.jsonl").read_text().splitlines()
    ]
    assert all(
        isinstance(json.loads(event["message"]), dict)
        for event in events
        if event["direction"] == "server-line"
    )

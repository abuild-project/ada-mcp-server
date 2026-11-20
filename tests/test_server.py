"""Tests for the MCP server module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_list_tools():
    """Test that list_tools returns expected tools."""
    from ada_mcp.server import list_tools

    tools = await list_tools()

    assert len(tools) >= 3
    tool_names = [t.name for t in tools]
    assert "ada_goto_definition" in tool_names
    assert "ada_hover" in tool_names
    assert "ada_diagnostics" in tool_names

    workspace_symbols = next(tool for tool in tools if tool.name == "ada_workspace_symbols")
    assert workspace_symbols.inputSchema["required"] == ["file", "query"]

    project_info = next(tool for tool in tools if tool.name == "ada_project_info")
    assert project_info.inputSchema["required"] == ["gpr_file"]
    assert "reuse the validated selection" in project_info.description
    assert project_info.inputSchema["properties"]["project_paths"] == {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "Ordered absolute GPR search directories; when provided, "
            "replace the inherited GPR_PROJECT_PATH"
        ),
    }
    assert project_info.inputSchema["properties"]["scenario_variables"]["additionalProperties"] == {
        "type": "string"
    }
    assert project_info.inputSchema["properties"]["refresh"]["type"] == "boolean"
    assert project_info.inputSchema["properties"]["refresh"]["default"] is False
    assert "without reload or readiness reset" in project_info.description
    assert "indexing_complete" in project_info.description


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Reject unknown tools before acquiring an ALS client."""
    from ada_mcp.server import call_tool

    with patch("ada_mcp.server.get_als_client", new_callable=AsyncMock) as acquire:
        result = await call_tool("unknown_tool", {})

    acquire.assert_not_called()
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data["error"] == "Unknown tool: unknown_tool"
    assert data["context"]["tool"] == "unknown_tool"
    assert data["available_tools"]


@pytest.mark.asyncio
async def test_call_tool_goto_definition():
    """Test ada_goto_definition tool call."""
    from ada_mcp.server import call_tool

    result = await call_tool(
        "ada_goto_definition",
        {
            "file": "/some/path/test.adb",
            "line": 10,
            "column": 5,
        },
    )

    assert len(result) == 1
    data = json.loads(result[0].text)
    # Currently returns "not implemented" - update when ALS is integrated
    assert "found" in data or "error" in data


@pytest.mark.asyncio
async def test_signature_help_serializes_malformed_selection_diagnostic(tmp_path):
    """Independent selection diagnostics and exact raw types reach the MCP payload."""
    from ada_mcp.server import call_tool

    source = tmp_path / "main.adb"
    source.write_text("procedure Main is begin null; end Main;\n")
    client = AsyncMock()
    client.send_request.return_value = {
        "signatures": [
            {"label": "First", "parameters": [{"label": "Only"}], "activeParameter": None},
            {"label": "Second", "parameters": [{"label": "Other"}], "activeParameter": 0},
        ],
        "activeSignature": True,
        "activeParameter": 1,
    }
    with (
        patch("ada_mcp.server.get_als_client", new_callable=AsyncMock, return_value=client),
        patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock),
    ):
        response = await call_tool(
            "ada_signature_help", {"file": str(source), "line": 1, "column": 1}
        )

    assert len(response) == 1 and response[0].type == "text"
    result = json.loads(response[0].text)
    assert result["found"] is True and type(result["active_signature"]) is int
    assert result["active_signature"] == result["active_parameter"] == 0
    assert result["selection_diagnostic"] == {
        "reason": "malformed-active-signature",
        "raw_active_signature": True,
        "fallback": "first-signature",
    }
    assert result["selection_diagnostic"]["raw_active_signature"] is True
    assert type(result["active_parameter"]) is int
    assert result["parameter_selection_diagnostic"] == {
        "reason": "malformed-active-parameter",
        "raw_active_parameter": None,
        "source": "selected-signature",
        "fallback": "zero",
    }
    assert result["parameter_selection_diagnostic"]["raw_active_parameter"] is None


@pytest.mark.asyncio
async def test_project_load_failure_discards_cached_client():
    """A failed project view must not remain cached after the request."""
    from ada_mcp.server import call_tool

    client = MagicMock()
    incomplete = {
        "complete": False,
        "reason": "project-load-failed",
        "project_file": "/test/project/abuild.gpr",
    }

    with (
        patch(
            "ada_mcp.server.get_als_client",
            new_callable=AsyncMock,
            return_value=client,
        ) as get_client,
        patch(
            "ada_mcp.server.handle_project_info",
            new_callable=AsyncMock,
            return_value=incomplete,
        ),
        patch(
            "ada_mcp.server._als_pool.discard_client",
            new_callable=AsyncMock,
        ) as discard,
    ):
        result = await call_tool(
            "ada_project_info",
            {"gpr_file": "/test/project/abuild.gpr"},
        )

    get_client.assert_awaited_once_with(
        file_path="/test/project/abuild.gpr",
        gpr_file="/test/project/abuild.gpr",
        project_paths=None,
        scenario_variables=None,
    )
    discard.assert_awaited_once_with("/test/project/abuild.gpr", client)
    assert json.loads(result[0].text) == incomplete


@pytest.mark.asyncio
async def test_project_info_selects_validated_client():
    """A validated explicit project becomes the source-tool project view."""
    from ada_mcp.server import call_tool

    client = MagicMock()
    complete = {
        "complete": True,
        "project_file": "/test/project/spawn_manager.gpr",
    }
    with (
        patch(
            "ada_mcp.server.get_als_client",
            new_callable=AsyncMock,
            return_value=client,
        ),
        patch(
            "ada_mcp.server.handle_project_info",
            new_callable=AsyncMock,
            return_value=complete,
        ) as handler,
        patch(
            "ada_mcp.server._als_pool.select_client",
            new_callable=AsyncMock,
        ) as select,
    ):
        result = await call_tool(
            "ada_project_info",
            {"gpr_file": "/test/project/spawn_manager.gpr"},
        )

    select.assert_awaited_once_with(client)
    handler.assert_awaited_once_with(
        client, gpr_file="/test/project/spawn_manager.gpr", refresh=False
    )
    assert json.loads(result[0].text) == complete


@pytest.mark.asyncio
async def test_project_info_forwards_project_context():
    """An explicit project environment reaches the ALS pool unchanged."""
    from ada_mcp.server import call_tool

    client = MagicMock()
    complete = {
        "complete": True,
        "project_file": "/test/project/spawn_manager.gpr",
    }
    arguments = {
        "gpr_file": "/test/project/spawn_manager.gpr",
        "project_paths": ["/test/project/anet"],
        "scenario_variables": {"OS": "linux", "VERSION": ""},
        "refresh": True,
    }
    with (
        patch(
            "ada_mcp.server.get_als_client",
            new_callable=AsyncMock,
            return_value=client,
        ) as get_client,
        patch(
            "ada_mcp.server.handle_project_info",
            new_callable=AsyncMock,
            return_value=complete,
        ) as handler,
        patch(
            "ada_mcp.server._als_pool.select_client",
            new_callable=AsyncMock,
        ),
    ):
        await call_tool("ada_project_info", arguments)

    get_client.assert_awaited_once_with(
        file_path=arguments["gpr_file"],
        gpr_file=arguments["gpr_file"],
        project_paths=arguments["project_paths"],
        scenario_variables=arguments["scenario_variables"],
    )
    handler.assert_awaited_once_with(client, gpr_file=arguments["gpr_file"], refresh=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid", ["false", None, 1])
async def test_invalid_refresh_has_no_client_or_selection_side_effects(invalid):
    from ada_mcp.server import call_tool

    with (
        patch("ada_mcp.server.get_als_client", new_callable=AsyncMock) as acquire,
        patch("ada_mcp.server.handle_project_info", new_callable=AsyncMock) as handler,
        patch("ada_mcp.server._als_pool.discard_client", new_callable=AsyncMock) as discard,
        patch("ada_mcp.server._als_pool.select_client", new_callable=AsyncMock) as select,
    ):
        response = await call_tool(
            "ada_project_info",
            {
                "gpr_file": "/project/view.gpr",
                "refresh": invalid,
            },
        )
    assert json.loads(response[0].text)["error"] == "refresh must be a Boolean"
    acquire.assert_not_awaited()
    handler.assert_not_awaited()
    discard.assert_not_awaited()
    select.assert_not_awaited()


@pytest.mark.asyncio
async def test_project_info_reports_invalid_context():
    """Invalid project context is distinguished from an ALS connection failure."""
    from ada_mcp.server import call_tool

    with patch(
        "ada_mcp.server.get_als_client",
        new_callable=AsyncMock,
        side_effect=ValueError("GPR project search paths must be absolute"),
    ):
        result = await call_tool(
            "ada_project_info",
            {
                "gpr_file": "/test/project/spawn_manager.gpr",
                "project_paths": ["relative/anet"],
            },
        )

    data = json.loads(result[0].text)
    assert data["error"] == "GPR project search paths must be absolute"
    assert "absolute GPR project directories" in data["hint"]
    assert "Failed to connect" not in data["error"]


@pytest.mark.asyncio
async def test_project_info_error_discards_selected_client():
    """A rejected explicit project must not remain selected in the pool."""
    from ada_mcp.server import call_tool

    client = MagicMock()
    with (
        patch(
            "ada_mcp.server.get_als_client",
            new_callable=AsyncMock,
            return_value=client,
        ),
        patch(
            "ada_mcp.server.handle_project_info",
            new_callable=AsyncMock,
            side_effect=RuntimeError("different project"),
        ),
        patch(
            "ada_mcp.server._als_pool.discard_client",
            new_callable=AsyncMock,
        ) as discard,
    ):
        result = await call_tool(
            "ada_project_info",
            {"gpr_file": "/test/project/spawn_manager.gpr"},
        )

    discard.assert_awaited_once_with("/test/project/spawn_manager.gpr", client)
    assert json.loads(result[0].text)["error"] == "different project"

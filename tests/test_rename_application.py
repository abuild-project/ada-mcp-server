"""Reject unsupported application while preserving rename previews and dispatch."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from ada_mcp.server import call_tool, list_tools
from ada_mcp.tools.refactoring import handle_rename_symbol

UNSUPPORTED = {
    "success": False,
    "error": "Rename application is not supported; use preview=true to inspect proposed changes.",
    "changes": [],
    "total_changes": 0,
    "applied": False,
}


def proposal_client(source):
    client = AsyncMock()
    client.send_request.side_effect = [
        {"placeholder": "Counter"},
        {
            "changes": {
                source.as_uri(): [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 7},
                        },
                        "newText": "NEXT",
                    }
                ]
            }
        },
    ]
    return client


@pytest.mark.asyncio
async def test_application_is_rejected_before_source_synchronization_or_native_rename(tmp_path):
    source = tmp_path / "source.adb"
    source.write_text("Counter := Counter;\n")
    before = source.read_bytes()
    client = proposal_client(source)
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock) as opened:
        result = await handle_rename_symbol(client, str(source), 1, 1, "Next", preview=False)
    assert result == UNSUPPORTED
    assert source.read_bytes() == before
    opened.assert_not_awaited()
    client.send_request.assert_not_awaited()
    client.send_notification.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("explicit_preview", [False, True], ids=["default", "explicit-preview"])
async def test_preview_and_default_preserve_native_edit_text_without_applying(
    tmp_path, explicit_preview
):
    source = tmp_path / "source.adb"
    source.write_text("Counter := Counter;\n")
    before = source.read_bytes()
    client = proposal_client(source)
    arguments = {"preview": True} if explicit_preview else {}
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock) as opened:
        result = await handle_rename_symbol(client, str(source), 1, 1, "Next", **arguments)
    assert result == {
        "success": True,
        "old_name": "Counter",
        "new_name": "Next",
        "changes": [
            {"file": str(source), "line": 1, "column": 1, "old_text": "Counter", "new_text": "NEXT"}
        ],
        "total_changes": 1,
        "files_affected": 1,
        "applied": False,
    }
    assert source.read_bytes() == before
    opened.assert_awaited_once_with(client, str(source))
    assert [call.args[0] for call in client.send_request.await_args_list] == [
        "textDocument/prepareRename",
        "textDocument/rename",
    ]


@pytest.mark.asyncio
async def test_catalog_describes_preview_only_without_changing_boolean_schema():
    tool = next(tool for tool in await list_tools() if tool.name == "ada_rename_symbol")
    assert "Preview" in tool.description and "not supported" in tool.description
    preview = tool.inputSchema["properties"]["preview"]
    assert preview["type"] == "boolean" and preview["default"] is True
    assert "false" in preview["description"] and "unsupported" in preview["description"]
    assert "enum" not in preview


@pytest.mark.asyncio
async def test_dispatch_returns_the_application_failure_with_existing_client_selection(tmp_path):
    source = tmp_path / "source.adb"
    source.write_text("Counter := Counter;\n")
    before = source.read_bytes()
    client = proposal_client(source)
    with (
        patch(
            "ada_mcp.server.get_als_client", new_callable=AsyncMock, return_value=client
        ) as select,
        patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock) as opened,
    ):
        result = await call_tool(
            "ada_rename_symbol",
            {
                "file": str(source),
                "line": 1,
                "column": 1,
                "new_name": "Next",
                "preview": False,
            },
        )
    assert json.loads(result[0].text) == UNSUPPORTED
    assert source.read_bytes() == before
    select.assert_awaited_once()
    opened.assert_not_awaited()
    client.send_request.assert_not_awaited()

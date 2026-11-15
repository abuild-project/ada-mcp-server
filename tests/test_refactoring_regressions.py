"""Preserve native code-action and rename proposals without applying them."""

from unittest.mock import AsyncMock, patch

import pytest

from ada_mcp.tools.refactoring import handle_code_actions, handle_rename_symbol


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("als-name-parameters", "als-name-parameters"),
        ({"title": "Name parameters", "command": "als-name-parameters"}, "Name parameters"),
    ],
)
async def test_code_actions_preserve_bare_and_nested_command_summaries(tmp_path, command, expected):
    """A legal bare LSP Command has a string identifier rather than a nested object."""
    source = tmp_path / "main.adb"
    source.write_text("procedure Main is begin null; end Main;\n")
    before = source.read_bytes()
    client = AsyncMock()
    client.send_request.return_value = [
        {"title": "Name parameters", "command": command, "arguments": [source.as_uri()]}
    ]
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock):
        result = await handle_code_actions(client, str(source), 1, 11)
    assert source.read_bytes() == before
    assert result == {
        "actions": [
            {
                "title": "Name parameters",
                "kind": "",
                "is_preferred": False,
                "has_edit": False,
                "files_affected": 0,
                "command": expected,
            }
        ],
        "count": 1,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("shape", ["changes", "documentChanges"])
async def test_rename_preview_preserves_each_native_replacement(tmp_path, shape):
    """Native per-edit replacement spelling must survive the preview conversion."""
    source = tmp_path / "main.adb"
    source.write_text("Counter := Counter;\n")
    before = source.read_bytes()
    edits = [
        {
            "range": {
                "start": {"line": 0, "character": column},
                "end": {"line": 0, "character": column + 7},
            },
            "newText": replacement,
        }
        for column, replacement in ((0, "NEXT"), (11, "Next"))
    ]
    workspace_edit = (
        {"changes": {source.as_uri(): edits}}
        if shape == "changes"
        else {
            "documentChanges": [
                {"textDocument": {"uri": source.as_uri(), "version": 1}, "edits": edits}
            ]
        }
    )
    client = AsyncMock()
    client.send_request.side_effect = [{"placeholder": "Counter"}, workspace_edit]
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock):
        result = await handle_rename_symbol(client, str(source), 1, 1, "Next", preview=True)
    assert source.read_bytes() == before
    assert result == {
        "success": True,
        "old_name": "Counter",
        "new_name": "Next",
        "changes": [
            {
                "file": str(source),
                "line": 1,
                "column": 1,
                "old_text": "Counter",
                "new_text": "NEXT",
            },
            {
                "file": str(source),
                "line": 1,
                "column": 12,
                "old_text": "Counter",
                "new_text": "Next",
            },
        ],
        "total_changes": 2,
        "files_affected": 1,
        "applied": False,
    }

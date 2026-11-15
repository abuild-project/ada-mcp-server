"""Preserve native code-action and rename proposals without applying them."""

from unittest.mock import AsyncMock, patch

import pytest

from ada_mcp.tools.refactoring import (
    handle_code_actions,
    handle_rename_symbol,
    handle_signature_help,
)


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("native_fields", "signature_fields", "expected_signature", "expected_parameter"),
    [
        ({"activeParameter": 0}, [{"activeParameter": 1}], 0, 1),
        ({"activeParameter": 1}, [{"activeParameter": 0}], 0, 0),
        ({}, [{"activeParameter": 2}], 0, 2),
        ({"activeParameter": 1}, [{}], 0, 1),
        ({}, [{}], 0, 0),
        (
            {"activeSignature": 1, "activeParameter": 0},
            [{"activeParameter": 0}, {"activeParameter": 2}],
            1,
            2,
        ),
        ({"activeParameter": 0}, [{"activeParameter": 1}, {"activeParameter": 2}], 0, 1),
        ({"activeSignature": 9, "activeParameter": 0}, [{"activeParameter": 1}], 0, 1),
        ({"activeParameter": 9}, [{}], 0, 0),
    ],
    ids=[
        "per-one-over-top-zero",
        "per-zero-over-top-one",
        "per-without-top",
        "top-fallback",
        "default-zero",
        "selected-second-signature",
        "missing-selected-signature",
        "out-of-range-signature",
        "out-of-range-top-parameter",
    ],
)
async def test_signature_help_uses_selected_signature_parameter(
    tmp_path, native_fields, signature_fields, expected_signature, expected_parameter
):
    """LSP per-signature selection overrides top-level selection by presence."""
    source = tmp_path / "main.adb"
    source.write_text("procedure Main is begin null; end Main;\n")
    before = source.read_bytes()
    native_signatures = [
        {
            "label": f"Overload_{index}",
            "parameters": [{"label": "Left"}, {"label": "Right"}, {"label": "Extra"}],
            **fields,
        }
        for index, fields in enumerate(signature_fields)
    ]
    client = AsyncMock()
    client.send_request.return_value = {"signatures": native_signatures, **native_fields}
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock):
        result = await handle_signature_help(client, str(source), 1, 11)
    assert result == {
        "found": True,
        "signatures": [
            {
                "label": f"Overload_{index}",
                "documentation": "",
                "parameters": [
                    {"label": name, "documentation": ""} for name in ("Left", "Right", "Extra")
                ],
            }
            for index in range(len(signature_fields))
        ],
        "active_signature": expected_signature,
        "active_parameter": expected_parameter,
    }
    assert source.read_bytes() == before


@pytest.mark.asyncio
@pytest.mark.parametrize("response", [None, {"signatures": []}])
async def test_signature_help_without_signatures_remains_negative(tmp_path, response):
    """An empty native signature reply preserves the existing explicit negative."""
    source = tmp_path / "main.adb"
    source.write_text("procedure Main is begin null; end Main;\n")
    client = AsyncMock()
    client.send_request.return_value = response
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock):
        result = await handle_signature_help(client, str(source), 1, 11)
    assert result == {
        "found": False,
        "signatures": [],
        "active_signature": 0,
        "active_parameter": 0,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["selected", "top", "per"])
@pytest.mark.parametrize("value", [None, False, True, "1", 1.0, -1])
async def test_signature_help_preserves_malformed_native_values_for_diagnosis(
    tmp_path, field, value
):
    """Malformed native indices remain visible rather than becoming valid defaults."""
    source = tmp_path / "main.adb"
    source.write_text("procedure Main is begin null; end Main;\n")
    native = {
        "signatures": [
            {"label": "First", "parameters": [{"label": "Left"}], "activeParameter": 0},
            {"label": "Second", "parameters": [{"label": "Right"}], "activeParameter": 1},
        ],
        "activeSignature": 0,
        "activeParameter": 0,
    }
    if field == "selected":
        native["activeSignature"] = value
    elif field == "top":
        del native["signatures"][0]["activeParameter"]
        native["activeParameter"] = value
    else:
        native["signatures"][0]["activeParameter"] = value
    client = AsyncMock()
    client.send_request.return_value = native
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock):
        result = await handle_signature_help(client, str(source), 1, 11)
    observed = result["active_signature" if field == "selected" else "active_parameter"]
    assert type(observed) is type(value) and observed == value
    if field == "selected":
        assert result["active_parameter"] == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("kind", "raw", "expected"),
    [
        ("active", 0, 0),
        ("active", 2147483647, 0),
        ("active", 2147483648, 2147483648),
        ("active", False, False),
        ("top-fallback", 0, 0),
        ("top-fallback", 2147483647, 0),
        ("top-fallback", 2147483648, 2147483648),
        ("top-fallback", False, False),
        ("top-overridden", 0, 0),
        ("top-overridden", 2147483647, 0),
        ("top-overridden", 2147483648, 0),
        ("top-overridden", False, 0),
        ("per", 0, 0),
        ("per", 2147483647, 2147483647),
        ("per", 2147483648, 2147483648),
        ("per", False, False),
    ],
    ids=[
        "active-zero",
        "active-max",
        "active-overflow",
        "active-bool",
        "top-zero",
        "top-max",
        "top-overflow",
        "top-bool",
        "override-zero",
        "override-max",
        "override-overflow",
        "override-bool",
        "per-zero",
        "per-max",
        "per-overflow",
        "per-bool",
    ],
)
async def test_signature_help_normalizes_only_valid_lsp_uintegers(tmp_path, kind, raw, expected):
    """MAX uses documented defaults; MAX+1 stays raw and never defeats per precedence."""
    source = tmp_path / "main.adb"
    source.write_text("procedure Main is begin null; end Main;\n")
    native = {
        "signatures": [
            {
                "label": "Combine",
                "parameters": [{"label": "Left"}, {"label": "Right"}],
                "activeParameter": 0,
            }
        ],
        "activeSignature": 0,
        "activeParameter": 0,
    }
    if kind == "active":
        native["activeSignature"] = raw
    elif kind == "top-fallback":
        del native["signatures"][0]["activeParameter"]
        native["activeParameter"] = raw
    elif kind == "top-overridden":
        native["activeParameter"] = raw
    else:
        native["signatures"][0]["activeParameter"] = raw
    client = AsyncMock()
    client.send_request.return_value = native
    with patch("ada_mcp.tools.refactoring._ensure_file_open", new_callable=AsyncMock):
        result = await handle_signature_help(client, str(source), 1, 11)
    actual = result["active_signature" if kind == "active" else "active_parameter"]
    assert type(actual) is type(expected) and actual == expected

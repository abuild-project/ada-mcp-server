"""Keep dependency summaries tied to code rather than comments or literals."""

import pytest

from ada_mcp.tools.navigation import _ensure_file_open
from ada_mcp.tools.project import handle_call_hierarchy, handle_dependency_graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source_text",
    [
        "-- procedure False_Unit is\nwith Visible;\nprocedure Actual is\nbegin null; end Actual;\n",
        'pragma Annotate (Tool, "procedure False_Unit");\nwith Visible;\n'
        "procedure Actual is\nbegin null; end Actual;\n",
        'pragma Annotate (Tool, "said ""procedure False_Unit"" then --");\n'
        "with Visible;\nprocedure Actual is\nbegin null; end Actual;\n",
        "with Visible; -- procedure False_Unit is\nprocedure Actual is\nbegin null; end Actual;\n",
        'with Visible;\npragma Annotate (Tool, "--"); procedure Actual is\n'
        "begin null; end Actual;\n",
        'with Visible;\npragma Annotate (Tool, "escaped ""--"" text"); procedure Actual is\n'
        "begin null; end Actual;\n",
        """pragma Compile_Time_Warning ('"' = Character'First, "procedure False_Unit");
with Visible;
procedure Actual is begin null; end Actual;
""",
    ],
    ids=[
        "comment-fake-unit",
        "literal-fake-unit",
        "escaped-literal-fake-unit",
        "trailing-comment-fake-unit",
        "comment-marker-in-string",
        "escaped-comment-marker-in-string",
        "quote-character-before-string",
    ],
)
async def test_dependency_graph_ignores_comment_and_literal_declarations(tmp_path, source_text):
    """Only the actual unit owns ordinary with clauses across lexical masking."""
    source = tmp_path / "actual.adb"
    source.write_text(source_text)
    before = source.read_bytes()
    assert await handle_dependency_graph(str(source)) == {
        "dependencies": [{"package": "Actual", "file": str(source), "depends_on": ["Visible"]}],
        "package_count": 1,
    }
    assert source.read_bytes() == before


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body",
    [
        "task body Worker is begin null; end Worker;\n",
        "task -- function False_Owner is\nbody Worker is\n"
        "   procedure Inner is begin null; end Inner;\n"
        "begin Inner; end Worker;\n",
        "procedure Worker is\n   procedure Inner is begin null; end Inner;\n"
        "begin Inner; end Worker;\n",
        "package body Worker is\n   procedure Inner is begin null; end Inner;\nend Worker;\n",
    ],
    ids=["task-only", "task-before-inner", "separate-procedure", "separate-package"],
)
async def test_dependency_graph_separate_body_owns_its_context(tmp_path, body):
    """Subunit imports belong to its declared name, without parent qualification."""
    source = tmp_path / "parent-worker.adb"
    source.write_text("with Visible;\nseparate (Parent)\n" + body)
    before = source.read_bytes()
    assert await handle_dependency_graph(str(source)) == {
        "dependencies": [{"package": "Worker", "file": str(source), "depends_on": ["Visible"]}],
        "package_count": 1,
    }
    assert source.read_bytes() == before


@pytest.mark.asyncio
async def test_call_hierarchy_synchronizes_cold_queried_source(tmp_path, mock_als_client):
    """Opening the queried file must precede native hierarchy preparation."""
    source = tmp_path / "actual.adb"
    source.write_text("procedure Actual is begin null; end Actual;\n")
    events = []

    async def notify(method, _params):
        events.append(method)

    async def request(method, _params):
        events.append(method)
        return None

    mock_als_client.send_notification.side_effect = notify
    mock_als_client.send_request.side_effect = request
    await handle_call_hierarchy(mock_als_client, str(source), 1, 11)
    assert events == ["textDocument/didOpen", "textDocument/prepareCallHierarchy"]


@pytest.mark.asyncio
async def test_call_hierarchy_refreshes_only_its_changed_queried_file(tmp_path, mock_als_client):
    """A queried-file change must reach ALS before evaluating the new edges."""
    source = tmp_path / "actual.adb"
    initial = "procedure Actual is begin First; Second; end Actual;\n"
    changed = "procedure Actual is begin Second; end Actual;\n"
    source.write_text(initial)
    synchronized = ""
    events = []

    async def notify(method, params):
        nonlocal synchronized
        events.append(method)
        synchronized = (
            params["textDocument"]["text"]
            if method == "textDocument/didOpen"
            else params["contentChanges"][0]["text"]
        )

    async def request(method, _params):
        events.append(method)
        if method == "textDocument/prepareCallHierarchy":
            return [{"name": "Actual"}]
        assert method == "callHierarchy/outgoingCalls"
        names = ["First", "Second"] if "First;" in synchronized else ["Second"]
        return [
            {
                "to": {
                    "name": name,
                    "kind": 12,
                    "uri": source.as_uri(),
                    "range": {"start": {"line": 0, "character": 0}},
                }
            }
            for name in names
        ]

    mock_als_client.send_notification.side_effect = notify
    mock_als_client.send_request.side_effect = request
    await _ensure_file_open(mock_als_client, str(source))
    source.write_text(changed)
    events.clear()
    result = await handle_call_hierarchy(mock_als_client, str(source), 1, 11)
    assert [item["name"] for item in result["outgoing_calls"]] == ["Second"]
    assert events == [
        "textDocument/didChange",
        "textDocument/prepareCallHierarchy",
        "callHierarchy/outgoingCalls",
    ]
    assert source.read_text() == changed

"""Keep imported-source selection separate from lexical roots and pool lifetime."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from ada_mcp.als.client import ALSClient
from ada_mcp.server import ALSPool, call_tool


@pytest_asyncio.fixture
async def views(tmp_path):
    library = tmp_path / "library"
    cli = library / "cli"
    other = tmp_path / "other"
    for root in (library, cli, other):
        (root / "src").mkdir(parents=True)
        (root / "view.gpr").write_text("project View is end View;\n")
    source = library / "src/shared.ads"
    source.write_text("package Shared is end Shared;\n")
    unlisted = library / "src/unlisted.ads"
    unlisted.write_text("package Unlisted is end Unlisted;\n")
    clients = [MagicMock() for _ in range(3)]
    for client in clients:
        client.is_running = True
        client.project_view_sources = frozenset({source})
    pool = ALSPool()
    with (
        patch(
            "ada_mcp.server.start_als_with_monitoring",
            new_callable=AsyncMock,
            side_effect=[(client, MagicMock()) for client in clients],
        ) as start,
        patch("ada_mcp.server.shutdown_als", new_callable=AsyncMock),
    ):
        try:
            yield SimpleNamespace(
                pool=pool,
                clients=clients,
                start=start,
                library=library,
                cli=cli,
                other=other,
                source=source,
                unlisted=unlisted,
            )
        finally:
            await pool.shutdown_all()


async def select(views, root, **context):
    """Make an explicit successful selection with an evaluated source list."""
    project = root / "view.gpr"
    client = await views.pool.get_client(str(project), gpr_file=project, **context)
    await views.pool.select_client(client)
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("path_kind", ["canonical", "dotdot", "symlink"])
async def test_imported_member_reuses_selected_importer_but_unlisted_file_does_not(
    views, path_kind
):
    selected = await select(views, views.cli)
    source = (
        views.source
        if path_kind == "canonical"
        else views.source.parent / ".." / "src" / views.source.name
    )
    if path_kind == "symlink":
        source = views.library.parent / "shared-alias.ads"
        source.symlink_to(views.source)
    assert await views.pool.get_client(str(source)) is selected
    assert await views.pool.get_client(str(views.unlisted)) is views.clients[1]
    assert views.start.call_count == 2
    assert views.start.await_args.args == (views.library,)
    assert views.start.await_args.kwargs["gpr_file"] is None


@pytest.mark.asyncio
async def test_latest_explicit_matching_view_wins_and_reselection_refreshes_order(views):
    first = await select(views, views.cli)
    second = await select(views, views.other)
    assert await views.pool.get_client(str(views.source)) is second
    # Ordinary use of an older view is not an explicit reselection.
    assert await views.pool.get_client(str(views.cli / "src/main.adb")) is first
    assert await views.pool.get_client(str(views.source)) is second
    assert await select(views, views.cli) is first
    assert await views.pool.get_client(str(views.source)) is first
    assert views.start.call_count == 2


@pytest.mark.asyncio
async def test_explicit_lexical_ancestor_and_nested_view_keep_priority(views):
    library = await select(views, views.library)
    nested = await select(views, views.cli)
    await select(views, views.other)
    assert await views.pool.get_client(str(views.source)) is library
    assert await views.pool.get_client(str(views.cli / "src/main.adb")) is nested
    assert views.start.call_count == 3


@pytest.mark.asyncio
async def test_imported_selection_keeps_exact_context_after_eviction(views):
    views.pool.max_instances = 1
    paths = [str(views.other), str(views.library)]
    await select(views, views.cli, project_paths=paths, scenario_variables={"MODE": "validation"})
    views.clients[1].project_view_sources = frozenset()
    await select(views, views.other)
    assert await views.pool.get_client(str(views.source)) is views.clients[2]
    assert views.start.await_args.args == (views.cli,)
    assert views.start.await_args.kwargs["gpr_file"] == views.cli / "view.gpr"
    context = views.start.await_args.kwargs["project_context"]
    assert context.project_paths == (views.other, views.library)
    assert context.scenario_map()["MODE"] == "validation"


@pytest.mark.asyncio
async def test_rejected_selected_view_drops_imported_membership(views):
    selected = await select(views, views.cli)
    await views.pool.discard_client(str(views.cli / "view.gpr"), selected)
    assert await views.pool.get_client(str(views.source)) is views.clients[1]
    assert views.start.await_args.args == (views.library,)
    assert views.start.await_args.kwargs["gpr_file"] is None


@pytest.mark.asyncio
async def test_pending_index_publishes_selection_and_later_readiness_without_discard(tmp_path):
    project = tmp_path / "pending.gpr"
    project.write_text("project Pending is end Pending;\n")
    source = tmp_path / "shared.ads"
    source.write_text("package Shared is end Shared;\n")
    process = MagicMock()
    process.returncode = None
    client = ALSClient(process)
    client.send_request = AsyncMock(
        side_effect=[
            {
                "tree": {"root-project": {"id": "pending"}},
                "projects": [
                    {
                        "project": {"id": "pending", "file-name": str(project)},
                        "sources": [{"file-name": str(source)}],
                    }
                ],
            },
            [],
        ]
    )
    client.wait_for_indexing = AsyncMock(
        side_effect=AssertionError("selection must not await indexing")
    )
    await client._handle_progress(
        {"token": "slow", "value": {"kind": "begin", "title": "Indexing"}}
    )
    pool = ALSPool()
    with (
        patch("ada_mcp.server._als_pool", pool),
        patch(
            "ada_mcp.server.start_als_with_monitoring",
            new_callable=AsyncMock,
            return_value=(client, MagicMock()),
        ) as start,
        patch("ada_mcp.server.shutdown_als", new_callable=AsyncMock) as shutdown,
    ):
        try:
            response = await call_tool(
                "ada_project_info",
                {"gpr_file": str(project), "project_paths": [], "scenario_variables": {}},
            )
            result = json.loads(response[0].text)
            assert result["complete"] is True and result["indexing_complete"] is False
            assert await pool.get_client(str(source)) is client
            assert len(pool._instances) == 1 and client.is_running
            shutdown.assert_not_awaited()
            client.wait_for_indexing.assert_not_awaited()
            await client._handle_progress({"token": "slow", "value": {"kind": "end"}})
            assert client._indexing_quiet_since is not None
            client._indexing_quiet_since -= 1.0
            assert await client.is_indexing_complete() is True
            assert await pool.get_client(str(source)) is client
            assert start.await_count == 1
            shutdown.assert_not_awaited()
        finally:
            await pool.shutdown_all()

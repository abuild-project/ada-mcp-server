"""Age an unchanged host snapshot without reconnecting or performing network checks."""

import json
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import ada_mcp.server as server
import ada_mcp.update_notice as notices

DAY = 86400
CHECKED_AT = 1700000000
AGES = [
    (-1, None),
    (0, "fresh"),
    (DAY - 1, "fresh"),
    (DAY, "stale"),
    (DAY + 1, "stale"),
    (7 * DAY, "stale"),
    (7 * DAY + 1, None),
]


def snapshot(incoming):
    return json.dumps(
        {
            "schema": 1,
            "current_version": "0.2.0-rc.1",
            "available_version": "0.3.0",
            "channel": "prerelease",
            "checked_at": CHECKED_AT,
            "freshness": incoming,
            "release_url": notices.RELEASES + "0.3.0",
        }
    )


@pytest.mark.parametrize("incoming", ["fresh", "stale"])
@pytest.mark.parametrize("age,expected", AGES)
def test_validation_ages_snapshot_and_preserves_incoming_stale(
    monkeypatch, incoming, age, expected
):
    raw = snapshot(incoming)
    monkeypatch.setattr(notices, "time", SimpleNamespace(time=lambda: CHECKED_AT + age))
    monkeypatch.setenv("ADA_MCP_UPDATE_NOTICE", raw)
    result = notices.validate_notice(raw, "0.2.0-rc.1")
    assert notices.environment_notice("0.2.0-rc.1") == result
    assert os.environ["ADA_MCP_UPDATE_NOTICE"] == raw
    if expected is None:
        assert result is None
    else:
        assert result is not None
        freshness = "stale" if incoming == "stale" else expected
        assert result["freshness"] == freshness
        assert ("not been refreshed successfully" in result["message"]) == (freshness == "stale")
        assert result["checked_at"] == CHECKED_AT
        assert result["current_version"] == "0.2.0-rc.1"
        assert result["available_version"] == "0.3.0"


@pytest.mark.parametrize("incoming", ["fresh", "stale"])
async def test_later_project_reads_age_the_same_environment_snapshot(monkeypatch, incoming):
    raw = snapshot(incoming)
    clock = SimpleNamespace(now=CHECKED_AT)
    monkeypatch.setattr(notices, "time", SimpleNamespace(time=lambda: clock.now))
    monkeypatch.setenv("ADA_MCP_UPDATE_NOTICE", raw)
    project = {
        "complete": True,
        "project_file": "/source/project.gpr",
        "source_dirs": ["/source/src"],
    }
    monkeypatch.setattr(server, "get_als_client", AsyncMock(return_value=object()))
    handler = AsyncMock(side_effect=lambda *args, **kwargs: dict(project))
    selection = AsyncMock()
    monkeypatch.setattr(server, "handle_project_info", handler)
    monkeypatch.setattr(server._als_pool, "select_client", selection)
    for age, expected in AGES[1:]:
        clock.now = CHECKED_AT + age
        response = await server.call_tool("ada_project_info", {"gpr_file": project["project_file"]})
        result = json.loads(response[0].text)
        if expected is None:
            assert "update_notice" not in result
        else:
            advisory = result.pop("update_notice")
            assert advisory == notices.environment_notice("0.2.0-rc.1")
            freshness = "stale" if incoming == "stale" else expected
            assert advisory["freshness"] == freshness
            assert ("not been refreshed successfully" in advisory["message"]) == (
                freshness == "stale"
            )
        assert result == project
        assert os.environ["ADA_MCP_UPDATE_NOTICE"] == raw
    assert handler.await_count == selection.await_count == len(AGES) - 1

"""Pytest configuration and fixtures for Ada MCP Server tests."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture(autouse=True)
def disable_automatic_release_checks(monkeypatch):
    """Keep unrelated tests offline and away from the caller's application cache."""
    monkeypatch.setenv("ADA_MCP_UPDATE_CHANNEL", "off")
    monkeypatch.delenv("ADA_MCP_UPDATE_NOTICE", raising=False)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_als_client() -> AsyncMock:
    """Create a mock ALS client for unit tests."""
    client = AsyncMock()
    client.send_request = AsyncMock()
    client.send_notification = AsyncMock()
    client.is_new_project_source = MagicMock(return_value=False)
    client.is_known_project_source = MagicMock(return_value=False)
    client.remember_project_source = MagicMock()
    client.forget_project_source = MagicMock()
    return client


@pytest.fixture
def sample_ada_file(tmp_path: Path) -> Path:
    """Create a sample Ada file for testing."""
    ada_file = tmp_path / "test.adb"
    ada_file.write_text("""\
with Ada.Text_IO;

procedure Test is
   X : Integer := 42;
begin
   Ada.Text_IO.Put_Line ("Hello, Ada!");
end Test;
""")
    return ada_file

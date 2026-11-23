"""Check documentation links through a small owned Pages build."""

import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import build_pages
import pytest

TAGGED_GUIDE = (
    "https://github.com/abuild-project/ada-mcp-server/blob/"
    "v0.2.0-rc.5/doc/first-install.md#install-or-upgrade-to-rc5"
)


@pytest.fixture
def pages_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(build_pages, "ROOT", tmp_path)
    docs = tmp_path / "doc/user"
    docs.mkdir(parents=True)
    for name in build_pages.GUIDES:
        (docs / f"{name}.md").write_text(f"# {name}\n")
    (docs / "first-install.md").write_text("# Installation\n\n## Install the runtime\n")
    (tmp_path / "doc/pages.css").write_text("body { color: black; }\n")
    (tmp_path / "LICENSE").write_text("Fixture license notice\n")
    return tmp_path


@pytest.mark.parametrize(
    "current_guide",
    [
        "first-install.md#install-the-runtime",
        "https://github.com/abuild-project/ada-mcp-server/blob/main/"
        "doc/user/first-install.md#install-the-runtime",
    ],
    ids=["relative", "github-main"],
)
def test_pages_guide_links_resolve_at_project_path(pages_source: Path, current_guide: str) -> None:
    (pages_source / "doc/user/index.md").write_text(
        f"# Start\n\n[Current guide]({current_guide})\n\n[Published guide]({TAGGED_GUIDE})\n"
    )
    output = pages_source / "ada-mcp-server"
    build_pages.build(output)

    index = (output / "index.html").read_text()
    current = re.search(r'<a href="([^"]+)">Current guide</a>', index)
    assert current is not None
    assert current[1] == "first-install.html#install-the-runtime"
    base = "https://abuild-project.github.io/ada-mcp-server/"
    destination = urlsplit(urljoin(base, current[1]))
    assert destination.path == "/ada-mcp-server/first-install.html"
    assert f'id="{destination.fragment}"' in (output / Path(destination.path).name).read_text()
    assert f'<a href="{TAGGED_GUIDE}">Published guide</a>' in index


@pytest.mark.parametrize(
    ("target", "message"),
    [
        ("missing.md", "broken documentation link"),
        ("first-install.md#missing", "unknown documentation anchor"),
    ],
)
def test_pages_rejects_broken_link(pages_source: Path, target: str, message: str) -> None:
    (pages_source / "doc/user/index.md").write_text(f"# Start\n\n[Broken link]({target})\n")
    with pytest.raises(ValueError, match=message):
        build_pages.build(pages_source / "ada-mcp-server")


@pytest.mark.parametrize(
    "target",
    [
        "../advanced.md",
        "https://github.com/abuild-project/ada-mcp-server/blob/main/doc/advanced.md",
    ],
    ids=["relative", "github-main"],
)
def test_pages_checks_advanced_reference_headings(pages_source: Path, target: str) -> None:
    (pages_source / "doc/advanced.md").write_text("# Advanced guide\n\n## Set up, then verify\n")
    start = pages_source / "doc/user/index.md"
    start.write_text(f"# Start\n\n[Advanced guide]({target}#set-up-then-verify)\n")
    output = pages_source / "ada-mcp-server"
    build_pages.build(output)

    expected = (
        "https://github.com/abuild-project/ada-mcp-server/blob/main/"
        "doc/advanced.md#set-up-then-verify"
    )
    assert f'<a href="{expected}">Advanced guide</a>' in (output / "index.html").read_text()
    assert not (output / "advanced.html").exists()

    start.write_text(f"# Start\n\n[Advanced guide]({target}#missing)\n")
    with pytest.raises(ValueError, match=r"unknown documentation anchor.*#missing"):
        build_pages.build(pages_source / "broken")

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render the maintained user guides into a standalone GitHub Pages site."""

import argparse
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from markdown_it import MarkdownIt
from markdown_it.token import Token
from version import ROOT

REPOSITORY = "https://github.com/abuild-project/ada-mcp-server"
SOURCE = f"{REPOSITORY}/blob/main/"
GUIDES = {
    "index": "Start",
    "first-install": "Install",
    "setup": "Use",
    "updating": "Updates",
    "support": "Help",
}


def heading_ids(tokens: list[Token]) -> dict[str, str]:
    """Set GitHub-style heading IDs and collect their display text."""
    headings: dict[str, str] = {}
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        inline = tokens[index + 1]
        title = "".join(
            part.content for part in inline.children or [] if part.type in {"text", "code_inline"}
        )
        slug = re.sub(r"[^\w -]", "", title.lower()).replace(" ", "-")
        anchor = slug
        suffix = 1
        while anchor in headings:
            anchor = f"{slug}-{suffix}"
            suffix += 1
        token.attrSet("id", anchor)
        headings[anchor] = title
    return headings


def resolve_link(
    href: str,
    source: Path,
    rendered: set[Path],
    anchors: dict[Path, dict[str, str]],
    parser: MarkdownIt,
) -> str:
    """Resolve a guide URL and verify its local destination."""
    repo_link = href.startswith(SOURCE)
    origin = ROOT if repo_link else source.parent
    url = urlsplit(href.removeprefix(SOURCE))
    if url.scheme or url.netloc:
        return href

    path = (origin / unquote(url.path)).resolve() if url.path else source
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"{source.name}: broken documentation link {href!r}")
    if url.fragment and path.suffix.lower() == ".md":
        if path not in anchors:
            anchors[path] = heading_ids(parser.parse(path.read_text(encoding="utf-8")))
        if unquote(url.fragment) not in anchors[path]:
            raise ValueError(f"{source.name}: unknown documentation anchor {href!r}")
    if path in rendered:
        html_path = f"{path.stem}.html" if url.path else ""
        return urlunsplit(("", "", html_path, url.query, url.fragment))
    if repo_link:
        return href
    source_url = urlsplit(SOURCE + quote(path.relative_to(ROOT).as_posix()))
    return source_url._replace(query=url.query, fragment=url.fragment).geturl()


def render_page(name: str, body: str, headings: dict[str, str]) -> str:
    """Wrap a guide in navigation that works from any hosting subpath."""
    navigation = "\n".join(
        f'<a href="{guide}.html"'
        + (' aria-current="page"' if guide == name else "")
        + f">{label}</a>"
        for guide, label in GUIDES.items()
    )
    section_links = "\n".join(
        f'<li><a href="#{quote(anchor)}">{escape(title)}</a></li>'
        for anchor, title in list(headings.items())[1:]
    )
    contents = (
        f'<nav class="contents" aria-label="On this page"><details>'
        f"<summary>On this page</summary><ul>{section_links}</ul></details></nav>"
        if name != "index"
        else ""
    )
    title = escape(next(iter(headings.values())))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a class="skip" href="#main-content">Skip to content</a>
  <header>
    <nav aria-label="Documentation">
      {navigation}
    </nav>
  </header>
  <main id="main-content" tabindex="-1">
    {contents}
    {body}
  </main>
  <footer>
    <a href="{REPOSITORY}">Ada MCP Server on GitHub</a>
    <a href="LICENSE.txt">MIT license</a>
  </footer>
</body>
</html>
"""


def build(output: Path) -> None:
    """Build the allowlisted guides in a new output directory."""
    parser = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])
    sources = [ROOT / "doc/user" / f"{name}.md" for name in GUIDES]
    documents = {path: parser.parse(path.read_text(encoding="utf-8")) for path in sources}
    rendered = set(documents)
    anchors = {source: heading_ids(tokens) for source, tokens in documents.items()}
    pages: dict[str, str] = {}
    for source, tokens in documents.items():
        for block in tokens:
            for token in block.children or []:
                if token.type == "link_open" and isinstance(href := token.attrGet("href"), str):
                    token.attrSet("href", resolve_link(href, source, rendered, anchors, parser))
        body = parser.renderer.render(tokens, parser.options, {})
        pages[source.stem] = render_page(source.stem, body, anchors[source])

    style = (ROOT / "doc/pages.css").read_text(encoding="utf-8")
    output.mkdir(parents=True)
    for name, page in pages.items():
        (output / f"{name}.html").write_text(page, encoding="utf-8")
    (output / "style.css").write_text(style, encoding="utf-8")
    shutil.copyfile(ROOT / "LICENSE", output / "LICENSE.txt")


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--output", type=Path, required=True, help="new site output directory")
    build(arguments.parse_args().output)

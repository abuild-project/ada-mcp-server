#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check maintained local links, example syntax and coordinated version claims."""

import json
import re
import subprocess
import tomllib
from pathlib import Path

from version import ROOT, project_version


def check_documents(root: Path = ROOT) -> None:
    """Validate maintained docs without rewriting historical import records."""
    paths = [root / "README.md", root / "AGENTS.md", root / "CHANGELOG.md", root / "ROADMAP.md"]
    paths.extend(path for path in (root / "doc").rglob("*.md") if "history" not in path.parts)
    for path in paths:
        text = path.read_text()
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            local = target.split("#", 1)[0]
            if local and not (path.parent / local).exists():
                raise ValueError(f"broken local documentation link: {path.name}: {target}")
        for language, content in re.findall(r"```([a-z]*)\n(.*?)```", text, flags=re.DOTALL):
            if language == "json":
                json.loads(content)
            elif language in {"bash", "sh"}:
                subprocess.run(["bash", "-n"], input=content, text=True, check=True)
    project = tomllib.loads((root / "pyproject.toml").read_text())
    if not all(
        "abuild-project/ada-mcp-server" in url for url in project["project"]["urls"].values()
    ):
        raise ValueError("project URLs must identify the independent repository")
    if project_version(root) not in (root / "CHANGELOG.md").read_text():
        raise ValueError("canonical candidate version is absent from the changelog")
    obsolete = ["pip install ada-mcp-server", "uvx ada-mcp-server", "--branch abuild/maintained"]
    for path in paths:
        if any(claim in path.read_text() for claim in obsolete):
            raise ValueError(f"obsolete installation instruction: {path}")


if __name__ == "__main__":
    check_documents()
    print("Maintained links, examples and version references passed.")

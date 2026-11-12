#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read the canonical version without importing runtime dependencies."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def project_version(root: Path = ROOT) -> str:
    """Return the single canonical SemVer string from the source tree."""
    tree = ast.parse((root / "src/ada_mcp/_version.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if isinstance(value, str):
                return value
    raise ValueError("canonical project version is missing")


if __name__ == "__main__":
    print(project_version())

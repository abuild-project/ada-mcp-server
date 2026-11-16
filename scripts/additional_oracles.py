#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require independently source-derived additional-tool results."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
Location = tuple[str, int, int]
Edge = tuple[str, int, str, int, int]
FORMATTED_UNEVEN = "procedure Uneven is\nbegin\n   null;\nend Uneven;\n"
MANIFEST = {
    "is_alire_project": True,
    "name": "additional_probe",
    "version": "1.2.3-dev",
    "description": "Exact metadata for the additional tool probe",
    "authors": ["Fixture Author"],
    "maintainers": ["Fixture Maintainer <fixture@example.invalid>"],
    "licenses": "MIT",
    "website": "https://example.invalid/additional-probe",
    "tags": ["fixture", "regression"],
    "dependencies": [
        {"name": "fixture_dependency", "version": "^2.0"},
        {"name": "another_dependency", "version": "~3.1"},
    ],
    "build_profiles": {"*": "validation"},
    "gpr_externals": {"MODE": ["debug", "release"]},
    "gpr_set_externals": {"MODE": "debug"},
    "executables": ["main"],
    "project_files": ["additional.gpr"],
}


def require_equal(actual: Any, expected: Any, purpose: str) -> None:
    """Fail with the exact expected and observed bounded contract."""

    def same(left: Any, right: Any) -> bool:
        if type(left) is not type(right):
            return False
        if isinstance(right, dict):
            return left.keys() == right.keys() and all(
                same(left[key], value) for key, value in right.items()
            )
        if isinstance(right, (list, tuple)):
            return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
        return bool(left == right)

    if not same(actual, expected):
        raise AssertionError(f"{purpose}: expected {expected!r}, received {actual!r}")


def require_token(location: Location, token: str) -> None:
    """Tie an independently fixed coordinate to the expected source spelling."""
    file, line, column = location
    lines = Path(file).read_text().splitlines()
    if (
        not 1 <= line <= len(lines)
        or lines[line - 1][column - 1 : column - 1 + len(token)] != token
    ):
        raise AssertionError("the expected location must identify the exact source token")


def _require_mcp_location(item: JSON) -> None:
    """Keep exact one-based coordinate types before set membership can erase aliases."""
    if any(
        type(item.get(key)) is not int or not 1 <= item[key] <= 2_147_483_648
        for key in ("line", "column")
    ):
        raise AssertionError(
            "one-based source coordinates must be exact integers from 1 through 2147483648"
        )


def require_hierarchy(result: JSON, symbol: str, outgoing: set[Edge], incoming: set[Edge]) -> None:
    """Require complete unique source-bound caller and callee edge sets."""
    if result.get("found") is not True or result.get("symbol") != symbol or result.get("error"):
        raise AssertionError("hierarchy must identify the exact queried callable")
    for direction, expected in (("outgoing", outgoing), ("incoming", incoming)):
        items = result.get(direction + "_calls")
        if not isinstance(items, list):
            raise AssertionError("hierarchy edges must be lists")
        for item in items:
            _require_mcp_location(item)
        actual = [
            (row.get("name"), row.get("kind"), row.get("file"), row.get("line"), row.get("column"))
            for row in items
        ]
        if (
            set(actual) != expected
            or len(actual) != len(expected)
            or type(result.get(direction + "_count")) is not int
            or result.get(direction + "_count") != len(expected)
        ):
            raise AssertionError(f"{direction} hierarchy must match exact unique source edges")
        for name, _kind, file, line, column in expected:
            require_token((file, line, column), name)


def require_dependencies(result: JSON, root: Path, unit_count: int, imports: list[str]) -> None:
    """Check a bounded ordinary-with graph without claiming full Ada parsing."""
    expected = (
        [{"package": "Main", "file": str(root / "src/main.adb"), "depends_on": imports}]
        if imports
        else []
    )
    require_equal(
        result, {"dependencies": expected, "package_count": unit_count}, "dependency graph"
    )


def require_project(result: JSON, root: Path) -> None:
    """Require the complete explicit GPR view and its owned build directories."""
    actual = {
        **result,
        "source_dirs": sorted(result.get("source_dirs", [])),
        "object_dir": str(Path(result.get("object_dir", ""))),
        "exec_dir": str(Path(result.get("exec_dir", ""))),
    }
    require_equal(
        actual,
        {
            "complete": True,
            "project_file": str(root / "additional.gpr"),
            "project_name": "Additional",
            "source_dirs": sorted([str(root / "src"), str(root / "formatting")]),
            "object_dir": str(root / "obj"),
            "exec_dir": str(root / "bin"),
            "main_units": ["main.adb"],
        },
        "explicit project view",
    )


def require_completions(result: JSON, changed: bool, limit: int = 50) -> None:
    """Check exact controlled members independently of result order."""
    descriptions = (
        [
            (
                "Merge",
                "function Merge (Left : Natural; Right : Natural; Extra : Natural) return Natural",
                5,
            ),
            ("Advance", "procedure Advance (Item : in out Natural)", 4),
        ]
        if changed
        else [
            ("Combine", "function Combine (Left : Integer; Right : Integer) return Integer", 3),
            ("Increment", "procedure Increment (Item : in out Integer)", 2),
        ]
    )
    expected = {
        (name, "Function", f"Probe.{name}\n\n{declaration}", f"at probe.ads ({line}:4)", name)
        for name, declaration, line in descriptions[:limit]
    }
    items = result.get("completions")
    if not isinstance(items, list) or result.get("error"):
        raise AssertionError("completions must be an error-free list")
    actual = [
        (
            row.get("label"),
            row.get("kind"),
            row.get("detail"),
            row.get("documentation"),
            row.get("insert_text"),
        )
        for row in items
    ]
    if (
        set(actual) != expected
        or len(actual) != len(expected)
        or type(result.get("count")) is not int
        or result.get("count") != len(expected)
        or result.get("is_incomplete") is not False
    ):
        raise AssertionError(
            "completion members, signatures, insertions and native completeness must match"
        )


def signature_result(changed: bool, parameter: int) -> JSON:
    """Describe exact formal ordering and the independently intended selection."""
    name, kind, formals = (
        ("Merge", "Natural", ["Left", "Right", "Extra"])
        if changed
        else ("Combine", "Integer", ["Left", "Right"])
    )
    declaration = (
        f"function {name} ("
        + "; ".join(f"{formal} : {kind}" for formal in formals)
        + f") return {kind}"
    )
    return {
        "found": True,
        "signatures": [
            {
                "label": declaration,
                "documentation": "",
                "parameters": [{"label": formal, "documentation": ""} for formal in formals],
            }
        ],
        "active_signature": 0,
        "active_parameter": parameter,
    }


def require_signature(result: JSON, changed: bool, parameter: int) -> None:
    """Require actual-to-formal selection rather than snapshotting a native bug."""
    require_equal(result, signature_result(changed, parameter), "signature selection")


def require_actions(result: JSON, location: str) -> None:
    """Check meaningful action discovery summaries without executing commands."""
    titles = {
        "call": [
            ("Name parameters in the call", "refactor.rewrite"),
            ("Extract Procedure", "refactor.extract"),
            ("Extract Function", "refactor.extract"),
        ],
        "declaration": [("Extract Variable", "refactor.extract")],
        "comment": [],
    }[location]
    expected = [
        {
            "title": title,
            "kind": kind,
            "is_preferred": False,
            "has_edit": False,
            "files_affected": 0,
            "command": "",
        }
        for title, kind in titles
    ]
    require_equal(result, {"actions": expected, "count": len(expected)}, "code-action discovery")


def require_rename(result: JSON, old_name: str, new_name: str, locations: set[Location]) -> None:
    """Require the complete preview edit set, excluding comments and same-name units."""
    if (
        result.get("success") is not True
        or result.get("applied") is not False
        or result.get("error")
    ):
        raise AssertionError("rename must be a successful unapplied preview")
    require_equal(
        (result.get("old_name"), result.get("new_name")), (old_name, new_name), "rename names"
    )
    changes = result.get("changes")
    if not isinstance(changes, list):
        raise AssertionError("rename changes must be a list")
    for change in changes:
        _require_mcp_location(change)
    actual = [
        (
            row.get("file"),
            row.get("line"),
            row.get("column"),
            row.get("old_text"),
            row.get("new_text"),
        )
        for row in changes
    ]
    expected = {(*location, old_name, new_name) for location in locations}
    if set(actual) != expected or len(actual) != len(expected):
        raise AssertionError("rename preview must contain the exact unique native edit set")
    require_equal(
        (result.get("total_changes"), result.get("files_affected")),
        (len(expected), len({location[0] for location in locations})),
        "rename counts",
    )
    for location in locations:
        require_token(location, old_name)


def _offset(text: str, line: Any, column: Any) -> int:
    """Validate ASCII fixture edit coordinates before calculating a text offset."""
    if type(line) is not int or type(column) is not int or line < 1 or column < 1:
        raise AssertionError("format edit positions must be positive integers")
    lines = text.splitlines(keepends=True)
    if text.endswith("\n"):
        lines.append("")
    if line > len(lines) or column > len(lines[line - 1].rstrip("\r\n")) + 1:
        raise AssertionError("format edit position is outside the source")
    return sum(map(len, lines[: line - 1])) + column - 1


def require_formatting(result: JSON, file: Path, expected: str) -> str:
    """Validate nonoverlapping edits and reconstruct independently fixed bytes."""
    if (
        result.get("formatted") is not True
        or result.get("file") != str(file)
        or result.get("error")
    ):
        raise AssertionError("uneven formatting must return a positive edit proposal")
    edits = result.get("edits")
    if (
        not isinstance(edits, list)
        or not edits
        or type(result.get("changes")) is not int
        or result.get("changes") != len(edits)
    ):
        raise AssertionError("uneven formatting must contain a nonempty exact edit count")
    original = file.read_text()
    intervals = []
    for edit in edits:
        start = _offset(original, edit.get("start_line"), edit.get("start_column"))
        end = _offset(original, edit.get("end_line"), edit.get("end_column"))
        replacement = edit.get("new_text")
        if start > end or not isinstance(replacement, str):
            raise AssertionError("format edit range or replacement is invalid")
        if original[start:end] == replacement:
            raise AssertionError("format edits must change their selected text")
        intervals.append((start, end, replacement))
    intervals.sort()
    if any(
        right[0] < left[1] or right[0] == left[0] for left, right in zip(intervals, intervals[1:])
    ):
        raise AssertionError("format edits must not overlap")
    formatted = original
    for start, end, replacement in reversed(intervals):
        formatted = formatted[:start] + replacement + formatted[end:]
    if formatted == original or formatted != expected:
        raise AssertionError("format edits must produce the independently fixed formatted source")
    return formatted


def require_spec(result: JSON, spec: Path, line: int, column: int, preview: str) -> None:
    """Distinguish an exact declaration result from the explicit file fallback."""
    require_equal(
        result,
        {"found": True, "spec_file": str(spec), "line": line, "column": column, "preview": preview},
        "spec target",
    )
    require_equal(spec.read_text().splitlines()[line - 1].strip(), preview, "spec source preview")


def require_build(result: JSON, root: Path, success: bool) -> None:
    """Require a real executable or exact compiler type errors at the source literal."""
    if (
        result.get("gpr_file") != str(root / "additional.gpr")
        or result.get("success") is not success
        or result.get("error")
    ):
        raise AssertionError("build must report the exact owned project and expected outcome")
    require_equal((result.get("warnings"), result.get("warning_count")), ([], 0), "build warnings")
    require_equal(result.get("hints"), [], "build hints")
    if success:
        require_equal(
            (
                result.get("exit_code"),
                result.get("errors"),
                result.get("error_count"),
                result.get("output"),
            ),
            (0, [], 0, ""),
            "successful compilation",
        )
        executable = root / "bin/main"
        if (
            not executable.is_file()
            or not os.access(executable, os.X_OK)
            or executable.read_bytes()[:4] != b"\x7fELF"
        ):
            raise AssertionError("successful build must produce its owned executable")
        return
    require_token((str(root / "src/main.adb"), 3, 25), '"deliberate compiler type error"')
    expected = [
        {"file": "main.adb", "line": 3, "column": 25, "severity": "error", "message": message}
        for message in ('expected type "Standard.Integer"', "found a string type")
    ]
    require_equal(
        (result.get("errors"), result.get("error_count")),
        (expected, 2),
        "compiler error locations and messages",
    )
    if (
        type(result.get("exit_code")) is not int
        or result["exit_code"] == 0
        or not result.get("output")
    ):
        raise AssertionError(
            "deliberate compiler error must retain nonzero status and compiler output"
        )


def require_manifest(result: JSON, root: Path, changed: bool = False) -> None:
    """Check every exposed manifest field against independent literal metadata."""
    expected = {**MANIFEST, "alire_file": str(root / "manifest/alire.toml")}
    if changed:
        expected = {
            **expected,
            "version": "2.0.0",
            "dependencies": [{"name": "fixture_dependency", "version": "=4.2"}],
            "gpr_set_externals": {"MODE": "release"},
        }
    require_equal(result, expected, "manifest metadata")

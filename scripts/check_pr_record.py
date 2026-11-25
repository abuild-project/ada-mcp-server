#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare a pull request body with the canonical record at its checked-out head."""

import json
import os
import sys
from difflib import unified_diff
from itertools import islice
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_DIFF_LINES = 40
_DIFF_WIDTH = 240


def _log_text(text: str) -> str:
    """Keep untrusted text on one log line and escape workflow command markers."""
    text = "".join(char if char.isprintable() else ascii(char)[1:-1] for char in text)
    return text.replace("::", r"\x3a\x3a").replace("##[", r"\x23#[")


def _normalize(text: str) -> str:
    """Treat CRLF as LF and ignore whitespace at the end of the text."""
    return text.replace("\r\n", "\n").rstrip()


def check_record(root: Path, head_ref: str, body: str) -> int:
    """Check the branch-derived record and print a bounded diff on mismatch."""
    topic = head_ref.split("/", 1)[-1].replace("/", "-")
    if not topic or "\\" in topic or "\0" in topic:
        print("The pull request head ref does not identify a change record.", file=sys.stderr)
        return 1

    relative = Path("doc/change-records") / f"{topic}.md"
    path = root / relative
    label = _log_text(relative.as_posix())
    try:
        if any(part.is_symlink() for part in (root / "doc", path.parent, path)):
            print(f"Change record path contains a symlink: {label}", file=sys.stderr)
            return 1
        if not path.is_file():
            print(f"Missing change record: {label}", file=sys.stderr)
            return 1
        record = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError):
        print(f"Cannot read UTF-8 change record: {label}", file=sys.stderr)
        return 1

    record, body = _normalize(record), _normalize(body)
    if record == body:
        print(f"Pull request body matches {label}.")
        return 0

    print(f"Pull request body differs from {label}.", file=sys.stderr)
    lines = unified_diff(
        record.split("\n"),
        body.split("\n"),
        relative.as_posix(),
        "pull request body",
        n=2,
        lineterm="",
    )
    for line in islice(lines, _DIFF_LINES):
        suffix = "..." if len(line) > _DIFF_WIDTH else ""
        print(_log_text(line[:_DIFF_WIDTH]) + suffix, file=sys.stderr)
    if next(lines, None) is not None:
        print("... diff truncated", file=sys.stderr)
    return 1


def main() -> int:
    """Read pull request input from the GitHub Actions event file."""
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        head_ref = event["pull_request"]["head"]["ref"]
        body = event["pull_request"]["body"]
        if not isinstance(head_ref, str) or (body is not None and not isinstance(body, str)):
            raise ValueError("invalid pull request field type")
    except (KeyError, OSError, TypeError, ValueError):
        print("Cannot read pull request head and body from GITHUB_EVENT_PATH.", file=sys.stderr)
        return 1
    return check_record(ROOT, head_ref, body or "")


if __name__ == "__main__":
    raise SystemExit(main())

"""Exercise comparison, branch paths and the Actions event boundary."""

import json
from pathlib import Path

import check_pr_record as checker
import pytest

_RECORD = "# Café topic\n\nKeep Markdown formatting.  \nNext line."


def _write_record(root: Path, name: str, text: str = _RECORD) -> Path:
    path = root / "doc/change-records" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


@pytest.mark.parametrize(
    ("head_ref", "name"),
    [
        ("codex/topic", "topic.md"),
        ("topic", "topic.md"),
        ("author/area/topic", "area-topic.md"),
        (
            "dependabot/github_actions/main/actions/checkout-7.0.1",
            "github_actions-main-actions-checkout-7.0.1.md",
        ),
    ],
)
def test_matching_record_uses_the_canonical_branch_path(tmp_path, capsys, head_ref, name):
    _write_record(tmp_path, name)
    assert checker.check_record(tmp_path, head_ref, _RECORD) == 0
    assert f"matches doc/change-records/{name}" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("record", "body"),
    [
        (_RECORD, _RECORD + " \t\n\n"),
        (_RECORD + " \t\n\n", _RECORD),
        (_RECORD.replace("\n", "\r\n"), _RECORD),
        (_RECORD, _RECORD.replace("\n", "\r\n")),
    ],
)
def test_only_crlf_and_end_of_text_whitespace_are_normalized(tmp_path, record, body):
    _write_record(tmp_path, "topic.md", record)
    assert checker.check_record(tmp_path, "codex/topic", body) == 0


@pytest.mark.parametrize(
    "body",
    [
        _RECORD.replace("Next line.", "Changed line."),
        _RECORD.replace("formatting.  \n", "formatting.\n"),
        _RECORD.replace("formatting.  \n", "formatting.  \r"),
        " " + _RECORD,
    ],
)
def test_substantive_and_interior_whitespace_changes_show_a_diff(tmp_path, capsys, body):
    _write_record(tmp_path, "topic.md")
    assert checker.check_record(tmp_path, "codex/topic", body) == 1
    error = capsys.readouterr().err
    assert "differs from doc/change-records/topic.md" in error
    assert "--- doc/change-records/topic.md\n+++ pull request body\n@@" in error
    changes = error.splitlines()[4:]
    assert any(line.startswith("-") for line in changes)
    assert any(line.startswith("+") for line in changes)


def test_missing_record_reports_path(tmp_path, capsys):
    assert checker.check_record(tmp_path, "codex/area/topic", _RECORD) == 1
    assert "Missing change record: doc/change-records/area-topic.md" in capsys.readouterr().err


@pytest.mark.parametrize("name", ["doc", "doc/change-records", "doc/change-records/topic.md"])
def test_symlinks_cannot_supply_an_external_record(tmp_path, capsys, name):
    checkout = tmp_path / "checkout"
    external = tmp_path / "external"
    _write_record(external, "topic.md")
    symlink = checkout / name
    symlink.parent.mkdir(parents=True)
    symlink.symlink_to(external / name)
    assert checker.check_record(checkout, "codex/topic", _RECORD) == 1
    assert "contains a symlink: doc/change-records/topic.md" in capsys.readouterr().err


def test_diff_bounds_and_escapes_workflow_commands(tmp_path, capsys):
    context = [f"shared line {number}" for number in range(5)]
    record = "\n".join(["old line", *context, *["record line"] * 50])
    _write_record(tmp_path, "topic.md", record)
    body = "\n".join(["::warning::\r##[error]" + "x" * 300, *context, *["body line"] * 50])
    assert checker.check_record(tmp_path, "codex/topic", body) == 1
    error = capsys.readouterr().err
    assert "... diff truncated" in error
    assert len(error.splitlines()) <= 42
    assert r"\x3a\x3awarning\x3a\x3a\r\x23#[error]" in error
    assert "::" not in error
    assert "##[" not in error
    assert "\r" not in error
    assert "x" * 300 not in error


@pytest.mark.parametrize("body", [_RECORD, None])
def test_main_reads_head_and_body_from_event(tmp_path, monkeypatch, body):
    _write_record(tmp_path, "area-topic.md", body or "")
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps(
            {"pull_request": {"head": {"ref": "codex/area/topic"}, "body": body}},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_HEAD_REF", "an-unrelated-branch")
    assert checker.main() == 0


def test_main_rejects_an_invalid_event(tmp_path, monkeypatch, capsys):
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"pull_request": {"head": {"ref": "codex/topic"}, "body": 17}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    assert checker.main() == 1
    assert "from GITHUB_EVENT_PATH" in capsys.readouterr().err

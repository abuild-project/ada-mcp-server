"""Exercise comparison, branch paths and the Actions event boundary."""

import json
import os
import re
import subprocess
from pathlib import Path
from textwrap import dedent

import check_pr_record as checker
import pytest

_RECORD = "# Café topic\n\nKeep Markdown formatting.  \nNext line."
_BASE_RECORD = "Record from the base checkout."
_CHECKER_PATH = Path("scripts/check_pr_record.py")
_WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/pr-record.yml"


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
        ("author/claude", "claude.md"),
        ("author/area/CLAUDE.local", "area-CLAUDE.local.md"),
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


@pytest.mark.parametrize("topic", ["CLAUDE", "CLAUDE.local"])
def test_reserved_names_are_rejected_even_for_a_matching_record(tmp_path, capsys, topic):
    _write_record(tmp_path, f"{topic}.md")
    assert checker.check_record(tmp_path, f"author/{topic}", _RECORD) == 1
    assert f"{topic} is a reserved change record name" in capsys.readouterr().err


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
    monkeypatch.chdir(tmp_path)
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


def _step_value(step: str, key: str, default: str) -> str:
    match = re.search(rf"^ +{key}: (.+)$", step, re.MULTILINE)
    return match[1] if match else default


@pytest.fixture
def record_workflow(tmp_path):
    # Read the checkout paths, run directory and command from this workflow's steps.
    blocks = _WORKFLOW.read_text(encoding="utf-8").split("\n      - name: ")[1:]
    steps = dict(block.split("\n", 1) for block in blocks)
    workspace = tmp_path / "workspace"
    base_step = steps.get("Check out the immutable PR base", "")
    base = workspace / _step_value(base_step, "path", "base")
    head = workspace / _step_value(steps["Check out the immutable PR head"], "path", ".")
    _write_record(base, "topic.md", _BASE_RECORD)
    _write_record(head, "topic.md")

    compare_step = steps["Compare the PR body with its change record"]
    cwd = workspace / _step_value(compare_step, "working-directory", ".")
    command = compare_step.split("        run: ", 1)[1]
    if command.startswith("|\n"):
        command = dedent(command[2:])

    def run(body: str) -> subprocess.CompletedProcess[str]:
        event = tmp_path / "event.json"
        event.write_text(
            json.dumps({"pull_request": {"head": {"ref": "author/topic"}, "body": body}}),
            encoding="utf-8",
        )
        return subprocess.run(
            ["bash", "-e", "-o", "pipefail", "-c", command],
            cwd=cwd,
            env=os.environ | {"GITHUB_EVENT_PATH": str(event)},
            capture_output=True,
            text=True,
            check=False,
        )

    return base, head, run


def _install_checker(root: Path) -> None:
    path = root / _CHECKER_PATH
    path.parent.mkdir()
    path.write_bytes(Path(checker.__file__).read_bytes())


def test_workflow_uses_base_checker_when_head_lacks_one(record_workflow):
    base, _, run = record_workflow
    _install_checker(base)

    result = run(_RECORD)
    assert result.returncode == 0, result.stderr
    assert "matches doc/change-records/topic.md" in result.stdout
    assert "Using the PR head checker" not in result.stdout


def test_workflow_uses_head_record_and_keeps_base_mismatch(record_workflow):
    base, head, run = record_workflow
    _install_checker(base)
    weakened = head / _CHECKER_PATH
    weakened.parent.mkdir()
    weakened.write_text("raise SystemExit(0)\n", encoding="utf-8")

    result = run(_BASE_RECORD)
    assert result.returncode == 1, result.stderr
    assert "differs from doc/change-records/topic.md" in result.stderr
    assert "+Record from the base checkout." in result.stderr
    assert "Using the PR head checker" not in result.stdout


def test_workflow_logs_fallback_when_base_checker_is_absent(record_workflow):
    _, head, run = record_workflow
    _install_checker(head)

    result = run(_RECORD)
    assert result.returncode == 0, result.stderr
    assert "PR base has no record checker. Using the PR head checker." in result.stdout
    assert "matches doc/change-records/topic.md" in result.stdout


def test_workflow_rejects_a_symlinked_head_checker_directory(record_workflow, tmp_path):
    _, head, run = record_workflow
    external = tmp_path / "external"
    external.mkdir()
    (external / _CHECKER_PATH.name).write_text("print('external checker ran')\n", encoding="utf-8")
    (head / "scripts").symlink_to(external)

    result = run(_RECORD)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "Cannot read PR record checker: scripts/check_pr_record.py" in result.stderr
    assert "external checker ran" not in result.stdout


@pytest.mark.parametrize("unusable", ["directory", "dangling symlink"])
def test_workflow_fails_without_fallback_for_unusable_base_checker(record_workflow, unusable):
    base, head, run = record_workflow
    _install_checker(head)
    path = base / _CHECKER_PATH
    path.parent.mkdir()
    if unusable == "directory":
        path.mkdir()
    else:
        path.symlink_to("missing.py")

    result = run(_RECORD)
    assert result.returncode == 1, result.stderr
    assert "Cannot read PR record checker: ../base/scripts/check_pr_record.py" in result.stderr
    assert "Using the PR head checker" not in result.stdout


def test_workflow_rejects_a_symlinked_base_checker_directory(record_workflow):
    base, head, run = record_workflow
    _install_checker(head)
    (base / "scripts").symlink_to(head / "scripts")

    result = run(_RECORD)
    assert result.returncode == 1, result.stderr
    assert "PR base checker directory is a symlink" in result.stderr
    assert "Using the PR head checker" not in result.stdout

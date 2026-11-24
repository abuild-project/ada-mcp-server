"""Bind published notes to reviewed Git bytes without contacting release services."""

import hashlib
import subprocess
from pathlib import Path

import ada_mcp_setup as setup
import promote
import pytest

VERSION = "0.2.0-rc.2"
NOTES = f"# Ada MCP Server {VERSION}\n\nReviewed release behavior and limits.\n".encode()


def repository(tmp_path, notes=NOTES):
    root = tmp_path / "source"
    path = root / "doc/releases" / f"{VERSION}.md"
    path.parent.mkdir(parents=True)
    (root / "tracked").write_text("source\n")
    if notes is not None:
        path.write_bytes(notes)

    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()

    git("init", "--initial-branch=fixture")
    git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "add", ".")
    git(
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Source",
    )
    return root, path, git("rev-parse", "HEAD")


def publication_input(tmp_path, source, monkeypatch):
    """Sentinel the next real execution boundary after the required notes preflight."""
    (tmp_path / "image.tar").write_bytes(b"archive boundary sentinel")

    def premature_archive(*args):
        raise AssertionError("image processing preceded notes validation")

    monkeypatch.setattr(setup, "validate_docker_archive", premature_archive)
    return {
        "source_sha": source,
        "version": VERSION,
        "image_archive": {"filename": "image.tar"},
        "image_id": "sha256:" + "a" * 64,
    }


def test_notes_use_approved_blob_despite_uncommitted_replacement(tmp_path):
    root, path, source = repository(tmp_path)
    path.write_bytes(b"Unreviewed worktree notes\n")
    assert promote.read_release_notes(source, VERSION, root) == NOTES


def test_untracked_notes_and_wrong_source_do_not_supply_missing_blob(tmp_path):
    root, path, missing_source = repository(tmp_path, None)
    path.write_bytes(NOTES)
    with pytest.raises(ValueError, match="approved source"):
        promote.read_release_notes(missing_source, VERSION, root)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "Add notes",
        ],
        check=True,
        capture_output=True,
    )
    source = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    assert promote.read_release_notes(source, VERSION, root) == NOTES
    with pytest.raises(ValueError, match="approved source"):
        promote.read_release_notes(missing_source, VERSION, root)


@pytest.mark.parametrize(
    "notes",
    [
        b"",
        f"# Ada MCP Server {VERSION}\n\n".encode(),
        b"# Ada MCP Server 0.2.0-rc.1\n\nWrong version.\n",
        NOTES + b"\xff",
        NOTES + b"\0",
        NOTES + b"x" * promote.MAX_NOTES_BYTES,
    ],
)
def test_invalid_notes_fail_before_any_publication(tmp_path, monkeypatch, notes):
    root, _, source = repository(tmp_path, notes)
    monkeypatch.setattr(promote, "ROOT", root)
    monkeypatch.setenv("ADA_MCP_PUBLISH_APPROVED_SOURCE", source)
    manifest = publication_input(tmp_path, source, monkeypatch)
    actual_run = subprocess.run
    calls = []

    def local_git_only(command, *args, **kwargs):
        calls.append(command)
        assert command[0] == "git", "invalid notes must not reach a service command"
        return actual_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", local_git_only)
    with pytest.raises(ValueError):
        promote.execute(tmp_path, manifest)
    assert calls and all(command[0] == "git" for command in calls)


def test_missing_notes_fail_before_any_publication(tmp_path, monkeypatch):
    root, _, source = repository(tmp_path, None)
    monkeypatch.setattr(promote, "ROOT", root)
    monkeypatch.setenv("ADA_MCP_PUBLISH_APPROVED_SOURCE", source)
    manifest = publication_input(tmp_path, source, monkeypatch)
    with pytest.raises(ValueError, match="approved source"):
        promote.execute(tmp_path, manifest)


@pytest.mark.parametrize("source,version", [("main", VERSION), ("a" * 40, "../notes")])
def test_note_identifiers_are_validated_before_git(tmp_path, monkeypatch, source, version):
    def unexpected(*args, **kwargs):
        raise AssertionError("invalid identifier reached Git")

    monkeypatch.setattr(subprocess, "run", unexpected)
    with pytest.raises(ValueError, match="source/version"):
        promote.read_release_notes(source, version, tmp_path)


@pytest.mark.parametrize("version", [VERSION, "0.2.0"])
def test_published_notes_file_is_not_a_release_asset(tmp_path, monkeypatch, version):
    notes = NOTES.replace(VERSION.encode(), version.encode())
    stage = tmp_path / "stage"
    stage.mkdir()
    for number in range(13):
        path = stage / f"asset-{number:02}.bin"
        path.write_bytes(f"tested artifact {number}".encode())
        path.chmod(0o640)

    def snapshot():
        return {
            path.name: (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode)
            for path in stage.iterdir()
        }

    before = snapshot()
    captured = []

    def publish(command, *, check):
        assert check is True
        assert command[:4] == ["gh", "release", "create", "v" + version]
        assert "--verify-tag" in command
        assert ("--prerelease" in command) is (version == VERSION)
        assert ("--latest" in command) is (version == "0.2.0")
        assert "--notes" not in command
        note_path = Path(command[command.index("--notes-file") + 1])
        assert note_path.parent == stage.parent and not note_path.is_relative_to(stage)
        assert note_path.read_bytes() == notes
        assert command[command.index("--notes-file") + 2 :] == [
            str(path) for path in sorted(stage.iterdir())
        ]
        captured.append(note_path)

    monkeypatch.setattr(subprocess, "run", publish)
    promote.publish_release(stage, "v" + version, notes)
    assert len(captured) == 1 and not captured[0].exists()
    assert snapshot() == before and len(before) == 13

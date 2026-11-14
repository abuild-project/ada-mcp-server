"""The documented manual switch must preserve relative targets and refuse clobber."""

import os
import re
import subprocess
import sys

import pytest
from version import ROOT


def switch(current, staged, backup):
    document = (ROOT / "doc/updating.md").read_text()
    code = re.search(r"python3 -I - <<'PY'\n(.*?)\nPY", document, re.DOTALL)[1]
    for original, replacement in [
        ("/absolute/project/.agents/skills/ada-development", str(current)),
        ("/absolute/private-staging/ada-development", str(staged)),
        ("/absolute/private-rollback/old-ada-development", str(backup)),
    ]:
        code = code.replace(original, replacement)
    return subprocess.run([sys.executable, "-I", "-"], input=code, text=True, capture_output=True)


def test_manual_switch_and_rollback_keep_both_storage_trees(tmp_path):
    old = tmp_path / "old-storage"
    new = tmp_path / "new-storage"
    old.mkdir()
    new.mkdir()
    discovery = tmp_path / "project/.agents/skills"
    discovery.mkdir(parents=True)
    current = discovery / "ada-development"
    current.symlink_to(os.path.relpath(old, discovery), target_is_directory=True)
    staged = tmp_path / "staged"
    staged.symlink_to(new, target_is_directory=True)
    rollback = tmp_path / "private-rollback"
    rollback.mkdir(mode=0o700)
    backup = rollback / "old-skill"
    assert switch(current, staged, backup).returncode == 0
    assert current.resolve() == new and backup.resolve() == old
    assert backup.readlink().is_absolute()
    assert switch(current, backup, rollback / "new-skill").returncode == 0
    assert current.resolve() == old and (rollback / "new-skill").resolve() == new
    assert old.is_dir() and new.is_dir()


@pytest.mark.parametrize("occupied", ["backup", "current-directory"])
def test_manual_switch_refuses_unexpected_entries(tmp_path, occupied):
    old = tmp_path / "old-storage"
    new = tmp_path / "new-storage"
    old.mkdir()
    new.mkdir()
    current = tmp_path / "current"
    current.symlink_to(old, target_is_directory=True)
    staged = tmp_path / "staged"
    staged.symlink_to(new, target_is_directory=True)
    backup = tmp_path / "backup"
    if occupied == "backup":
        backup.write_text("preserve")
    else:
        current.unlink()
        current.mkdir()
    assert switch(current, staged, backup).returncode != 0
    if occupied == "backup":
        assert backup.read_text() == "preserve" and current.resolve() == old
    else:
        assert current.is_dir() and not current.is_symlink() and not backup.exists()
    assert old.is_dir() and new.is_dir()

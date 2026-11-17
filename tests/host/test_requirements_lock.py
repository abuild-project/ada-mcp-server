"""Reject declared input drift without requiring Git metadata or resolving packages."""

import os
import shutil
import subprocess
import sys

import check_requirements as checker
import pytest


@pytest.fixture
def requirements(tmp_path):
    directory = tmp_path / "requirements"
    directory.mkdir()
    (directory / "development.in").write_text("-r runtime.in\nruff==0.17.5\n")
    (directory / "runtime.in").write_text("mcp==1.30.0\n")
    (directory / "development.lock").write_text("ruff==0.17.5\nmcp==1.30.0\nextra==1.0\n")
    return tmp_path


def test_original_ruff_drift_is_rejected_and_corrected_lock_passes(requirements):
    lock = requirements / "requirements/development.lock"
    corrected = lock.read_text()
    lock.write_text(corrected.replace("ruff==0.17.5", "ruff==0.17.4"))
    with pytest.raises(ValueError, match=r"ruff: input ==0\.17\.5, lock ==0\.17\.4"):
        checker.check_requirements(requirements)
    lock.write_text(corrected)
    checker.check_requirements(requirements)


def test_runtime_include_pin_is_required(requirements):
    lock = requirements / "requirements/development.lock"
    lock.write_text("ruff==0.17.5\nextra==1.0\n")
    with pytest.raises(ValueError, match="mcp: input ==1.30.0, missing"):
        checker.check_requirements(requirements)


def test_repository_format_and_transitive_lock_extras(requirements):
    directory = requirements / "requirements"
    (directory / "development.in").write_text(
        "# input\n\n  -r runtime.in # relative include\nPyTest_Asyncio == 1.5.0 # pin\n"
    )
    (directory / "development.lock").write_text(
        "# generated lock\npytest-asyncio==1.5.0 \\\n"
        "    --hash=sha256:" + "a" * 64 + " \\\n"
        "    --hash=sha256:" + "b" * 64 + "\n    # via input\n"
        "mcp==1.30.0\ntransitive==2.0\n"
    )
    checker.check_requirements(requirements)


@pytest.mark.parametrize("name", ["development.in", "development.lock"])
def test_unrecognized_relevant_line_is_not_silently_ignored(requirements, name):
    path = requirements / "requirements" / name
    path.write_text(path.read_text() + "unhandled>=1.0\n")
    with pytest.raises(ValueError, match="unsupported requirements line"):
        checker.check_requirements(requirements)


def test_conflicting_included_pin_is_rejected(requirements):
    path = requirements / "requirements/development.in"
    path.write_text(path.read_text() + "MCP==1.29.0\n")
    with pytest.raises(ValueError, match="conflicting pins for mcp"):
        checker.check_requirements(requirements)


def test_include_cycle_fails_clearly(requirements):
    (requirements / "requirements/runtime.in").write_text("-r development.in\n")
    with pytest.raises(ValueError, match="requirements include cycle"):
        checker.check_requirements(requirements)


def test_ci_stops_before_lint_on_drift(requirements):
    scripts = requirements / "scripts"
    scripts.mkdir()
    shutil.copy2(checker.ROOT / "scripts/check_requirements.py", scripts)
    shutil.copy2(checker.ROOT / "scripts/ci", scripts)
    lock = requirements / "requirements/development.lock"
    lock.write_text(lock.read_text().replace("ruff==0.17.5", "ruff==0.17.4"))
    binary = requirements / "bin"
    binary.mkdir()
    python = binary / "python"
    python.write_text(
        f'#!/bin/sh\nif [ "$1" = -c ]; then exit 0; fi\nexec "{sys.executable}" "$@"\n'
    )
    python.chmod(0o755)
    for name in ["gnat", "gprbuild", "als"]:
        stub = binary / name
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
    lint = binary / "ruff"
    lint.write_text('#!/bin/sh\nprintf called > "$LINT_CALLED"\nexit 99\n')
    lint.chmod(0o755)
    marker = requirements / "lint-called"
    result = subprocess.run(
        ["bash", str(scripts / "ci"), str(requirements / "output")],
        cwd=requirements,
        env=dict(
            os.environ,
            PATH=str(binary) + os.pathsep + os.environ["PATH"],
            ALS_PATH=str(binary / "als"),
            LINT_CALLED=str(marker),
        ),
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "ruff: input ==0.17.5, lock ==0.17.4" in result.stderr
    assert not marker.exists()

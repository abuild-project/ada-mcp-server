"""Real host Python startup controls, no Docker or Ada-runtime acceptance claim."""

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import artifacts
from image_fixtures import metadata_archive
from version import ROOT


def entrypoint_flags():
    line = next(
        line
        for line in (ROOT / "docker/Dockerfile").read_text().splitlines()
        if line.startswith("ENTRYPOINT ")
    )
    command = json.loads(line.removeprefix("ENTRYPOINT "))
    assert command[0] == "/opt/ada-mcp/venv/bin/python"
    return command[1:]


def test_cwd_package_override_stops_but_installed_server_imports_still_work(tmp_path, monkeypatch):
    project = tmp_path / "shared project Ω"
    (project / "ada_mcp").mkdir(parents=True)
    (project / "ada_mcp/__init__.py").write_text("")
    (project / "ada_mcp/__main__.py").write_text("print('SYNTHETIC_CWD_OVERRIDE')\n")
    (project / "json.py").write_text("raise RuntimeError('SYNTHETIC_STDLIB_OVERRIDE')\n")
    monkeypatch.setenv("PYTHONPATH", str(project))
    monkeypatch.setenv("ADA_PROJECT_ROOT", "")
    monkeypatch.setenv("ADA_PROJECT_FILE", "")
    monkeypatch.setenv("ADA_PROJECT_SCENARIO_VARIABLES", "{}")
    original = subprocess.run(
        [sys.executable, "-m", "ada_mcp"],
        cwd=project,
        input="",
        text=True,
        capture_output=True,
        timeout=20,
    )
    assert original.returncode == 0 and "SYNTHETIC_CWD_OVERRIDE" in original.stdout
    flags = entrypoint_flags()
    assert flags[-2:] == ["-m", "ada_mcp"]
    # Host-only import control. Actual pinned-image STDIO/ALS is a separate gate.
    program = (
        "import importlib,json,os; p=importlib.import_module('ada_mcp'); "
        "e=importlib.import_module('ada_mcp.__main__'); "
        "s=importlib.import_module('ada_mcp.server').server; "
        "print(json.dumps(dict(package=p.__file__,entry=e.__file__,cwd=os.getcwd(),"
        "version=s.create_initialization_options().server_version)))"
    )
    fixed = subprocess.run(
        [sys.executable, *flags[:-2], "-c", program],
        cwd=project,
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    result = json.loads(fixed.stdout)
    assert not Path(result["package"]).is_relative_to(project)
    assert not Path(result["entry"]).is_relative_to(project)
    assert result["cwd"] == str(project) and result["version"] == "0.2.0rc1"


def test_isolated_startup_ignores_python_environment_and_preserves_cwd(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "json.py").write_text("raise RuntimeError('SYNTHETIC_JSON_OVERRIDE')\n")
    (project / "sitecustomize.py").write_text("raise RuntimeError('SYNTHETIC_SITE_OVERRIDE')\n")
    environment = dict(os.environ, PYTHONPATH=str(project), PYTHONHOME=str(project / "bad-home"))
    command = [
        sys.executable,
        "-I",
        "-c",
        "import json,os,sys; print(json.dumps(dict(cwd=os.getcwd(),"
        "isolated=sys.flags.isolated,ignore=sys.flags.ignore_environment,"
        "user=sys.flags.no_user_site)))",
    ]
    result = subprocess.run(
        command,
        cwd=project,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    observed = json.loads(result.stdout)
    assert observed == {"cwd": str(project), "isolated": 1, "ignore": 1, "user": 1}


def test_user_site_startup_is_excluded_by_isolation(tmp_path):
    base_python = getattr(sys, "_base_executable", sys.executable)
    userbase = tmp_path / "userbase"
    site = (
        userbase
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    site.mkdir(parents=True)
    (site / "usercustomize.py").write_text("print('SYNTHETIC_USER_SITE_STARTUP')\n")
    environment = dict(os.environ, PYTHONUSERBASE=str(userbase))
    for key in ["PYTHONPATH", "PYTHONHOME", "PYTHONNOUSERSITE", "PYTHONSAFEPATH"]:
        environment.pop(key, None)
    ordinary = subprocess.run(
        [base_python, "-c", "print('ordinary')"],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    assert "SYNTHETIC_USER_SITE_STARTUP" in ordinary.stdout
    isolated = subprocess.run(
        [base_python, "-I", "-c", "print('ordinary')"],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    assert isolated.stdout == "ordinary\n"


def test_generated_stdin_acquirer_ignores_shared_cwd_before_hash_checks(tmp_path):
    release = tmp_path / "release"
    release.mkdir()
    archive, _, target = metadata_archive(oci=True)
    image = release / "fixture-image.tar"
    image.write_bytes(archive.getvalue())
    manifest = artifacts.package(ROOT, release, "a" * 40, target, image)
    with tarfile.open(release / manifest["plugin"]["filename"]) as plugin:
        skill = plugin.extractfile("skills/ada-development/SKILL.md").read().decode()
    block = re.search(r"```sh\n(.*?)```", skill, re.S).group(1)
    header, program = block.split("<<'PY'\n", 1)
    program = program.rsplit("\nPY", 1)[0]
    argv = shlex.split(header.replace("\\\n", " "))
    assert argv[:3] == ["python3", "-I", "-"]
    argv[0] = sys.executable
    index = argv.index("--url")
    argv[index : index + 2] = ["--archive", str(release / manifest["tooling"]["filename"])]
    destination = tmp_path / "verified-runtime"
    argv[argv.index("--destination") + 1] = str(destination)
    project = tmp_path / "untrusted-cwd"
    project.mkdir()
    (project / "json.py").write_text("raise RuntimeError('SYNTHETIC_PREHASH_OVERRIDE')\n")
    original = subprocess.run(
        [arg for arg in argv if arg != "-I"],
        cwd=project,
        input=program,
        text=True,
        capture_output=True,
        timeout=20,
    )
    assert original.returncode != 0 and "SYNTHETIC_PREHASH_OVERRIDE" in original.stderr
    fixed = subprocess.run(
        argv, cwd=project, input=program, text=True, capture_output=True, check=True, timeout=20
    )
    assert json.loads(fixed.stdout)["runtime"] == str(destination)
    assert (destination / "scripts/runtime-manifest.json").is_file()


def test_build_version_parser_ignores_unrelated_cwd_module_with_docker_stub(tmp_path):
    repo = tmp_path / "source"
    (repo / "docker").mkdir(parents=True)
    (repo / "src/ada_mcp").mkdir(parents=True)
    shutil.copy2(ROOT / "docker/build", repo / "docker/build")
    shutil.copy2(ROOT / "src/ada_mcp/_version.py", repo / "src/ada_mcp/_version.py")
    git = ["git", "-C", str(repo)]
    subprocess.run(
        git + ["init", "--initial-branch", "codex/startup"], check=True, capture_output=True
    )
    subprocess.run(git + ["add", "."], check=True)
    subprocess.run(
        git
        + [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "Fixture",
        ],
        check=True,
        capture_output=True,
    )
    project = tmp_path / "unrelated-cwd"
    project.mkdir()
    (project / "ast.py").write_text("raise RuntimeError('SYNTHETIC_AST_OVERRIDE')\n")
    binary = tmp_path / "bin"
    binary.mkdir()
    capture = tmp_path / "arguments"
    fake = binary / "docker"
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$CAPTURE"\n')
    fake.chmod(0o755)
    environment = dict(
        os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"], CAPTURE=str(capture)
    )
    subprocess.run(
        [str(repo / "docker/build")],
        cwd=project,
        env=environment,
        check=True,
        capture_output=True,
        timeout=20,
    )
    assert "PROJECT_VERSION=0.2.0-rc.1" in capture.read_text().splitlines()


def test_ci_keeps_intentional_source_imports_and_probes_use_isolation():
    check = (ROOT / "docker/check").read_text()
    assert "--entrypoint /bin/bash" in check and "export PYTHONPATH=/ci-work/source/src" in check
    assert '"python", "-I", "-c"' in (ROOT / "tooling/ada_mcp_setup.py").read_text()
    assert '"python", "-I", "-c"' in (ROOT / "tooling/mac_smoke.py").read_text()

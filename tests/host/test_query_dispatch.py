"""Dispatch the real setup/query client from retained sources without changing its CLI."""

import hashlib
import json
import subprocess
import sys
import tarfile

import acquire
import pytest
from test_acquire import make_archive
from test_update_bytecode import snapshot
from test_verified_helpers import installed as installed


def program(installed, arguments, hook=""):
    source = installed["scripts"] / "ada_mcp_setup.py"
    return (
        "from pathlib import Path\nimport json,os,sys\n"
        f"source=Path({str(source)!r})\n"
        "ns={'__name__':'_query_fixture','__file__':str(source)}\n"
        "exec(compile(source.read_bytes(),str(source),'exec'),ns)\n"
        + hook
        + f"sys.argv={arguments!r}\nraise SystemExit(ns['main']())\n"
    )


def arguments(installed, tmp_path, request):
    return [
        str(installed["scripts"] / "ada_mcp_setup.py"),
        "query",
        "--binding",
        str(installed["binding"]),
        "--update-channel",
        "off",
        "--update-cache",
        str(tmp_path / "unused-cache"),
        "--timeout",
        "5",
        "--log-dir",
        str(tmp_path / "query Ω logs"),
        "--name",
        "query-dispatch-fixture",
        *request,
    ]


def run(installed, code, cwd, data=None):
    return subprocess.run(
        [sys.executable, "-I", "-B", "-c", code],
        cwd=cwd,
        env=dict(installed["env"], PYTHONDONTWRITEBYTECODE="1"),
        input=data,
        text=True,
        capture_output=True,
        timeout=12,
    )


@pytest.mark.parametrize("preloaded", [False, True])
def test_query_ignores_disk_replacement_after_real_verification(installed, tmp_path, preloaded):
    client = installed["scripts"] / "mcp_client.py"
    original = hashlib.sha256(client.read_bytes()).hexdigest()
    marker = tmp_path / "unverified-client-executed"
    replacement = (
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        "raise SystemExit(93)\n"
    )
    hook = (
        "verify=ns['verified_manifest']\n"
        "def verified_then_replace():\n"
        "    manifest=verify()\n"
        f"    client=Path({str(client)!r})\n"
        "    captured=ns['_verified_sources'][client]\n"
        f"    assert __import__('hashlib').sha256(captured).hexdigest()=={original!r}\n"
    )
    if preloaded:
        hook += "    ns['load_helper']('mcp_client')\n"
    hook += (
        f"    client.write_text({replacement!r})\n"
        "    return manifest\nns['verified_manifest']=verified_then_replace\n"
    )
    expected = snapshot(installed["runtime"])
    expected["scripts/mcp_client.py"] = (
        hashlib.sha256(replacement.encode()).hexdigest(),
        expected["scripts/mcp_client.py"][1],
    )
    code = program(installed, arguments(installed, tmp_path, ["tools", "--help"]), hook)
    result = run(installed, code, tmp_path)
    assert result.returncode == 0 and "usage: mcp_client.py tools" in result.stdout, result.stderr
    assert not marker.exists() and snapshot(installed["runtime"]) == expected
    assert not (tmp_path / "query Ω logs").exists() and not (tmp_path / "unused-cache").exists()


def test_query_rejects_post_acquisition_unlisted_client_before_launch(installed, tmp_path):
    # Healthy acquisition requires an exact declared archive set. This is an
    # explicitly malformed/post-acquisition runtime, not a valid release archive.
    with pytest.raises(ValueError, match="undeclared or missing tooling file"):
        acquire.verified_files(*make_archive(tarfile.TarInfo("scripts/mcp_client.py")))
    scripts = installed["scripts"]
    marker = tmp_path / "unlisted-client-executed"
    (scripts / "mcp_client.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
        "raise SystemExit(93)\n"
    )
    manifest_path = scripts / "runtime-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files_sha256"].pop("scripts/mcp_client.py")
    manifest_path.write_text(json.dumps(manifest))
    expected = snapshot(installed["runtime"])
    code = program(installed, arguments(installed, tmp_path, ["tools"]))
    result = run(installed, code, tmp_path)
    assert result.returncode == 1 and "has not been verified" in json.loads(result.stdout)["error"]
    assert not marker.exists() and snapshot(installed["runtime"]) == expected
    assert not installed["commands"].exists() and not (tmp_path / "query Ω logs").exists()


@pytest.mark.parametrize(
    "mode",
    [
        "tools",
        "call",
        "batch-stdin",
        "batch-file",
        "semantic-error",
        "timeout",
        "bad-exit",
        "denied",
        "help",
    ],
)
def test_query_preserves_cli_protocol_streams_status_and_eof(installed, tmp_path, mode):
    caller = tmp_path / "caller cwd"
    caller.mkdir()
    receipt = tmp_path / "runtime-eof.json"
    frontend = tmp_path / "frontend-pid"
    # Keep the real generic launcher and client Session/stdio/cleanup path.
    # Only the fixture Docker command's run branch becomes a tiny protocol peer;
    # this is no real Docker, Ada, or semantic-acceptance evidence.
    docker = tmp_path / "bin/docker"
    source = docker.read_text()
    source = source.replace(
        "elif sys.argv[1] == 'run' or sys.argv[1:3] == ['image','load']:",
        "elif sys.argv[1:3] == ['image','load']:",
    )
    branch = (
        "elif sys.argv[1] == 'run':\n"
        "    seen=[]\n"
        "    for line in sys.stdin:\n"
        "        request=json.loads(line); seen.append(request)\n"
        "        if 'id' not in request: continue\n"
        "        method=request['method']\n"
        "        if method=='initialize':\n"
        "            result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},"
        "'serverInfo':{'name':'fixture','version':'fixture'}}\n"
        "        elif method=='tools/list':\n"
        + ("            continue\n" if mode == "timeout" else "            result={'tools':[]}\n")
        + "        elif method=='tools/call':\n"
        + (
            "            payload={'error':'controlled semantic failure'}\n"
            if mode == "semantic-error"
            else "            payload={'complete':True,\n"
            "                     'arguments':request['params']['arguments']}\n"
        )
        + "            result={'structuredContent':payload}\n"
        "        else: raise RuntimeError('unexpected method')\n"
        "        reply={'jsonrpc':'2.0','id':request['id'],'result':result}\n"
        "        print(json.dumps(reply),flush=True)\n"
        f"    Path({str(receipt)!r}).write_text(json.dumps({{'eof':True,'requests':seen,"
        "'cwd':__import__('os').getcwd(),'client_pid':__import__('os').getppid(),'argv':sys.argv[1:]}))\n"
        + ("    raise SystemExit(7)\n" if mode == "bad-exit" else "    raise SystemExit(0)\n")
    )
    source = source.replace(
        "else: raise SystemExit('unexpected Docker command')",
        branch + "else: raise SystemExit('unexpected Docker command')",
    )
    docker.write_text(source)
    calls = [{"tool": "ada_project_info", "arguments": {"gpr_file": "/source/project.gpr"}}]
    data = None
    if mode in {"call", "semantic-error", "denied"}:
        tool = "ada_build" if mode == "denied" else calls[0]["tool"]
        request = ["call", tool, "--arguments", json.dumps(calls[0]["arguments"])]
    elif mode == "batch-stdin":
        request, data = ["batch", "-"], json.dumps(calls)
    elif mode == "batch-file":
        (caller / "requests.json").write_text(json.dumps(calls))
        request = ["batch", "requests.json"]
    else:
        request = ["tools", "--help"] if mode == "help" else ["tools"]
    cli = arguments(installed, tmp_path, request)
    if mode == "timeout":
        cli[cli.index("--timeout") + 1] = "0.2"
    hook = f"Path({str(frontend)!r}).write_text(str(os.getpid()))\n"
    expected = snapshot(installed["runtime"])
    result = run(installed, program(installed, cli, hook), caller, data)
    assert snapshot(installed["runtime"]) == expected
    assert not (tmp_path / "unused-cache").exists()
    if mode == "help":
        assert result.returncode == 0 and "usage: mcp_client.py tools" in result.stdout
        assert result.stderr == "" and not receipt.exists()
        assert not (tmp_path / "query Ω logs").exists()
        return
    if mode in {"semantic-error", "timeout", "bad-exit", "denied"}:
        assert result.returncode == 1 and result.stdout == ""
        assert "error" in json.loads(result.stderr)
    else:
        assert result.returncode == 0 and result.stderr == ""
        payload = json.loads(result.stdout)  # Extra setup JSON would fail parsing.
        assert "initialize" in payload
        if mode == "tools":
            assert payload["tools"] == [] and "ada_project_info" in payload["client_read_tools"]
        else:
            assert payload["results"][0]["result"]["arguments"] == calls[0]["arguments"]
    if mode == "denied":
        assert not receipt.exists() and not (tmp_path / "query Ω logs").exists()
        return
    ended = json.loads(receipt.read_text())
    assert ended["eof"] is True and ended["cwd"] == str(caller)
    assert ended["client_pid"] == int(frontend.read_text())
    assert ended["argv"][0] == "run" and "--network" in ended["argv"]
    assert "none" in ended["argv"] and installed["target"] in ended["argv"]
    command = json.loads((tmp_path / "query Ω logs/command.json").read_text())
    assert command[command.index("--name") + 1] == "query-dispatch-fixture"
    assert command[command.index("--update-channel") + 1] == "off"
    assert command[command.index("--update-cache") + 1] == str(tmp_path / "unused-cache")

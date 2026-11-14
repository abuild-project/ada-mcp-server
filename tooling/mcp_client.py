#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Query the real STDIO server through the generic container launcher."""

import argparse
import datetime
import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, TextIO

JSON = dict[str, Any]


READ_TOOLS = frozenset(
    {
        "ada_goto_definition",
        "ada_hover",
        "ada_diagnostics",
        "ada_find_references",
        "ada_document_symbols",
        "ada_workspace_symbols",
        "ada_type_definition",
        "ada_implementation",
        "ada_project_info",
        "ada_call_hierarchy",
        "ada_dependency_graph",
        "ada_completions",
        "ada_signature_help",
        "ada_code_actions",
        "ada_get_spec",
        "ada_alire_info",
    }
)


def validate_calls(calls: Any) -> list[JSON]:
    """Validate the whole read-only batch before starting any subprocess."""
    if not isinstance(calls, list) or not calls:
        raise ValueError("a batch must be a nonempty JSON array")
    for call in calls:
        if not isinstance(call, dict) or set(call) != {"tool", "arguments"}:
            raise ValueError("each call requires exactly tool and arguments")
        if not isinstance(call["arguments"], dict):
            raise ValueError("tool arguments must be a JSON object")
        tool = call["tool"]
        if tool == "ada_rename_symbol":
            if call["arguments"].get("preview") is not True:
                raise ValueError("rename is permitted only with explicit preview=true")
        elif tool not in READ_TOOLS:
            raise ValueError("tool is outside this read-only client policy: " + str(tool))
    return calls


def create_private_directory(path: Path) -> None:
    """Create only new directories, each owner-only, without chmod of existing paths."""
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    missing = []
    parent = path
    while not parent.exists():
        if parent.is_symlink():
            raise FileExistsError(parent)
        missing.append(parent)
        parent = parent.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)


class Session:
    """Own one MCP subprocess and preserve request/result boundaries."""

    def __init__(
        self, command: list[str], timeout: float = 60, log_dir: Path | str | None = None
    ) -> None:
        self.command = command
        self.timeout = timeout
        self.serial = 0
        self.messages: queue.Queue[JSON | BaseException] = queue.Queue()
        self.events: TextIO | None = None
        self.error_log: TextIO | None = None
        self.lock = threading.Lock()
        self.closed = False
        self.server_exit: int | None = None
        if log_dir is not None:
            root = Path(log_dir)
            create_private_directory(root)
            self.events = (root / "protocol.jsonl").open("w")
            self.error_log = (root / "server-stderr.log").open("w")
            (root / "command.json").write_text(json.dumps(command, indent=2) + "\n")
        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self.error_log,
                text=True,
                bufsize=1,
            )
        except BaseException:
            self._close_logs()
            raise
        self.reader = threading.Thread(target=self._consume, daemon=True)
        self.reader.start()

    def _record(self, direction: str, message: Any) -> None:
        """Append one protocol observation when an explicit log was requested."""
        if self.events is not None:
            with self.lock:
                self.events.write(
                    json.dumps(
                        {
                            "at": datetime.datetime.now(datetime.UTC).isoformat(),
                            "direction": direction,
                            "message": message,
                        }
                    )
                    + "\n"
                )
                self.events.flush()

    def _consume(self) -> None:
        """Parse newline-delimited server messages without hiding bad stdout."""
        try:
            assert self.process.stdout is not None
            for line in self.process.stdout:
                if not line.strip():
                    continue
                self._record("server-line", line)
                try:
                    value = json.loads(line)
                except ValueError as error:
                    self.messages.put(RuntimeError("non-JSON MCP stdout: " + str(error)))
                    return
                self.messages.put(value)
        finally:
            self.messages.put(EOFError("MCP server stdout closed"))

    def _send(self, value: JSON) -> None:
        """Send one JSON-RPC value on the server's standard input."""
        self._record("client", value)
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(value) + "\n")
        self.process.stdin.flush()

    def request(self, method: str, params: JSON) -> JSON:
        """Wait for one response, retaining and answering intervening requests."""
        self.serial += 1
        ident = self.serial
        self._send({"jsonrpc": "2.0", "id": ident, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("MCP request timed out: " + method)
            try:
                message = self.messages.get(timeout=remaining)
            except queue.Empty:
                raise TimeoutError("MCP request timed out: " + method) from None
            if isinstance(message, BaseException):
                raise message
            if message.get("id") == ident and "method" not in message:
                if "error" in message:
                    raise RuntimeError("MCP protocol error: " + json.dumps(message["error"]))
                response: JSON = message["result"]
                return response
            if "method" in message and "id" in message:
                response = {"jsonrpc": "2.0", "id": message["id"]}
                if message["method"] == "ping":
                    response["result"] = {}
                else:
                    response["error"] = {
                        "code": -32601,
                        "message": "Client callback is not supported",
                    }
                self._send(response)

    def initialize(self) -> JSON:
        """Complete a real MCP initialization before issuing tools requests."""
        result = self.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "generic-ada-mcp-client", "version": "0.1.0"},
            },
        )
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return result

    def tools(self) -> list[JSON]:
        """Collect the advertised server catalog, following protocol cursors."""
        result = []
        params: JSON = {}
        cursors = set()
        while True:
            page = self.request("tools/list", params)
            result.extend(page.get("tools", []))
            cursor = page.get("nextCursor")
            if not cursor:
                return result
            if cursor in cursors:
                raise RuntimeError("MCP tools/list repeated a pagination cursor")
            cursors.add(cursor)
            params = {"cursor": cursor}

    def call(self, tool: str, arguments: JSON) -> Any:
        """Perform one allowed tool call and decode its structured JSON result."""
        validate_calls([{"tool": tool, "arguments": arguments}])
        result = self.request("tools/call", {"name": tool, "arguments": arguments})
        if result.get("isError"):
            raise RuntimeError("MCP tool failed: " + json.dumps(result))
        if isinstance(result.get("structuredContent"), dict):
            payload = result["structuredContent"]
        else:
            payload = None
            for item in result.get("content", []):
                if item.get("type") == "text":
                    try:
                        payload = json.loads(item["text"])
                    except ValueError:
                        continue
                    break
            if payload is None:
                raise RuntimeError("MCP tool did not return structured JSON")
        if isinstance(payload, dict) and payload.get("error"):
            raise RuntimeError("MCP semantic request failed: " + json.dumps(payload))
        return payload

    def _close_logs(self) -> None:
        """Close only logs owned by this client instance."""
        for stream in [self.events, self.error_log]:
            if stream is not None:
                stream.close()

    def close(self) -> int | None:
        """Send STDIN EOF and wait for normal server cleanup within a bound."""
        if self.closed:
            return self.server_exit
        self.closed = True
        forced = False
        try:
            assert self.process.stdin is not None
            self.process.stdin.close()
            self.server_exit = self.process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            forced = True
            self.process.terminate()
            try:
                self.server_exit = self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.server_exit = self.process.wait(timeout=5)
        finally:
            self.reader.join(timeout=2)
            self._close_logs()
        if forced:
            raise RuntimeError("MCP subprocess required forced termination")
        if self.server_exit != 0:
            raise RuntimeError("MCP subprocess exited " + str(self.server_exit))
        return self.server_exit


def add_launch_arguments(parser: argparse.ArgumentParser) -> None:
    """Declare the same host binding parameters used by the native launcher."""
    parser.add_argument("--launcher", default=str(Path(__file__).with_name("ada-mcp-launch")))
    parser.add_argument("--image", required=True)
    parser.add_argument("--root", action="append", required=True)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--docker-host")
    selector.add_argument("--docker-context")
    parser.add_argument("--uid", type=int)
    parser.add_argument("--gid", type=int)
    parser.add_argument("--name")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--log-dir")
    parser.add_argument("--update-channel", choices=["auto", "stable", "prerelease", "off"])
    parser.add_argument("--update-cache")


def launcher_command(options: argparse.Namespace) -> list[str]:
    """Construct an argv list without evaluating shell text or host variables."""
    command = [str(Path(options.launcher).resolve()), "--image", options.image]
    for root in options.root:
        command.extend(["--root", root])
    for attribute in [
        "docker_host",
        "docker_context",
        "uid",
        "gid",
        "name",
        "update_channel",
        "update_cache",
    ]:
        value = getattr(options, attribute, None)
        if value is not None:
            if attribute == "update_cache" and not Path(value).is_absolute():
                raise ValueError("update cache directory must be absolute")
            command.extend(["--" + attribute.replace("_", "-"), str(value)])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_launch_arguments(parser)
    commands = parser.add_subparsers(dest="mode", required=True)
    commands.add_parser("tools")
    call = commands.add_parser("call")
    call.add_argument("tool")
    call.add_argument("--arguments", required=True)
    batch = commands.add_parser("batch")
    batch.add_argument("requests", help="JSON batch filename, or - for stdin")
    options = parser.parse_args()
    session = None
    result = None
    problem = None
    try:
        if options.timeout <= 0:
            raise ValueError("--timeout must be positive")
        calls = None
        if options.mode == "call":
            calls = validate_calls(
                [{"tool": options.tool, "arguments": json.loads(options.arguments)}]
            )
        elif options.mode == "batch":
            data = (
                sys.stdin.read() if options.requests == "-" else Path(options.requests).read_text()
            )
            calls = validate_calls(json.loads(data))
        session = Session(launcher_command(options), options.timeout, options.log_dir)
        initialize = session.initialize()
        if options.mode == "tools":
            result = {
                "initialize": initialize,
                "tools": session.tools(),
                "client_read_tools": sorted(READ_TOOLS),
                "rename_requires_explicit_preview": True,
            }
        else:
            assert calls is not None
            result = {
                "initialize": initialize,
                "results": [
                    {
                        "tool": call["tool"],
                        "arguments": call["arguments"],
                        "result": session.call(call["tool"], call["arguments"]),
                    }
                    for call in calls
                ],
            }
    except Exception as error:
        problem = type(error).__name__ + ": " + str(error)
    finally:
        if session is not None:
            try:
                session.close()
            except Exception as error:
                if problem is None:
                    problem = type(error).__name__ + ": " + str(error)
    if problem is not None:
        print(json.dumps({"error": problem}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

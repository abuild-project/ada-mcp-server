#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prove selected ancestor-GPR semantics against the actual ALS/MCP server."""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from test_integration import MCPTestClient, call_tool


async def run() -> None:
    """Resolve a nested source through an explicitly selected parent-only unit."""
    with tempfile.TemporaryDirectory(prefix="ada-parent-view-") as temporary:
        root = Path(temporary)
        (root / "src_expected").mkdir()
        (root / "src_wrong").mkdir()
        (root / "nested/src").mkdir(parents=True)
        project = root / "parent.gpr"
        project.write_text(
            'project Parent is\n Mode := external ("MODE", "wrong");\n'
            ' for Source_Dirs use ("src_" & Mode, "nested/src");\n'
            ' for Object_Dir use "obj";\nend Parent;\n'
        )
        (root / "nested/nested.gpr").write_text(
            'project Nested is for Source_Dirs use ("src"); end Nested;\n'
        )
        spec = root / "src_expected/shared.ads"
        spec.write_text("package Shared is\n procedure Root_Only;\nend Shared;\n")
        (root / "src_wrong/shared.ads").write_text(
            "package Shared is Wrong_Only : Integer; end Shared;\n"
        )
        (root / "src_expected/shared.adb").write_text(
            "package body Shared is\n"
            " procedure Root_Only is begin null; end Root_Only;\nend Shared;\n"
        )
        nested = root / "nested/src/child.adb"
        nested.write_text(
            "with Shared;\nprocedure Child is\nbegin\n Shared.Root_Only;\nend Child;\n"
        )
        environment = dict(os.environ)
        environment.update(
            ADA_PROJECT_FILE="", ADA_PROJECT_ROOT="", ADA_PROJECT_SCENARIO_VARIABLES="{}"
        )
        with (root / "server-stderr.log").open("w") as errors:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "ada_mcp",
                cwd=root,
                env=environment,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=errors,
            )
            client = MCPTestClient(process)
            try:
                initialized = await client.send_request(
                    "initialize",
                    {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {"name": "selected-parent-acceptance", "version": "1"},
                    },
                )
                await client.send_notification("notifications/initialized")
                info = await call_tool(
                    client,
                    "ada_project_info",
                    {
                        "gpr_file": str(project),
                        "project_paths": [],
                        "scenario_variables": {"MODE": "expected"},
                    },
                )
                assert info.get("complete") is True and info["project_file"] == str(project), info
                symbols = await call_tool(
                    client,
                    "ada_workspace_symbols",
                    {
                        "file": str(nested),
                        "query": "Root_Only",
                        "kind": "all",
                        "limit": 50,
                    },
                )
                assert symbols.get("complete") is True and not symbols.get("truncated"), symbols
                assert any(
                    symbol["file"] == str(spec) and symbol["name"] == "Root_Only"
                    for symbol in symbols["symbols"]
                ), symbols
                definition = await call_tool(
                    client,
                    "ada_goto_definition",
                    {
                        "file": str(nested),
                        "line": 4,
                        "column": 9,
                    },
                )
                assert definition.get("found") is True and definition["file"] == str(spec), (
                    definition
                )
                assert "Root_Only" in spec.read_text().splitlines()[definition["line"] - 1]
                print(
                    json.dumps(
                        {
                            "initialize": initialized,
                            "project": info,
                            "symbols": symbols,
                            "definition": definition,
                        },
                        indent=2,
                    )
                )
            finally:
                assert process.stdin is not None
                process.stdin.close()
                try:
                    status = await asyncio.wait_for(process.wait(), timeout=15)
                except TimeoutError:
                    process.kill()
                    await process.wait()
                    raise RuntimeError("parent-view MCP server did not exit on STDIN EOF") from None
                if status != 0:
                    raise RuntimeError(f"parent-view MCP server exited {status}")


if __name__ == "__main__":
    asyncio.run(run())

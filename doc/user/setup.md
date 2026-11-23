# Use Ada MCP

## Run your first query

Open the checkout you want to inspect. Give Codex the actual project file
(`.gpr`) and the name of an Ada source file in that project:

```text
Select app.gpr and list the symbols in src/app.ads.
Show the file names, line numbers and any warnings.
```

Replace the example paths with files in your checkout. If your project needs
dependency search paths or scenario values such as a release build mode,
include them. On Mac, Codex uses the connected Ada tools. In Managed Cloud,
ask the Ada skill to use the Docker query helper.

## Direct Docker query

Save a batch as `first-query.json`. Replace the example paths with absolute
paths inside folders you shared at setup.

```json
[
  {
    "tool": "ada_project_info",
    "arguments": {"gpr_file": "/path/to/project/app.gpr"}
  },
  {
    "tool": "ada_document_symbols",
    "arguments": {"file": "/path/to/project/src/app.ads"}
  }
]
```

Run the Docker query helper with the runtime and binding you set up:

```sh
python3 /path/to/runtime/scripts/ada_mcp_setup.py query \
  --binding /path/to/ada-binding.json batch /path/to/first-query.json
```

For projects with extra dependency paths or scenario values, see the
[full batch example](../first-install.md#shared-docker-binding-and-first-queries).

## Everyday questions

- “Where is the definition of the symbol at line 42 of this file?”
- “What type does this variable have?”
- “Which diagnostics were reported for this file?”

Give the file and position for navigation or hover. When you change projects
or worktrees, select the new checkout's project file and sources. Compare
paths and locations in the answer with your checkout.
[Get help with incomplete results](support.md#the-answer-is-empty-or-incomplete).

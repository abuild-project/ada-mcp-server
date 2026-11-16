# Separate task-body dependency owners

Dependency graphs did not recognize separate task bodies as source owners.
A task subunit's ordinary context imports were attributed to its first
inner procedure, function or package; without one, the subunit was omitted.

The existing forward declaration scan now recognizes complete task body
declarations and attributes imports to the task's declared name. The owner
remains unqualified, matching separate procedure and package bodies. This
is a bounded lexical correction using the existing masking and scan.

Contributor guidance now calls for proportionate records, verbatim PR
descriptions and later head validation in comments.

Regressions cover task bodies with and without an inner procedure,
comments and line breaks, plus the existing procedure/package naming
convention. A small Ada/GPR fixture checks the exact Worker/Ada.Text_IO
dependency reply through real STDIO MCP and compiles the parent with
GNAT 14. The [development guide](../development.md#task-subunit-fixture-check)
describes the fixture's compiler and input-integrity checks.

At revision `122db00f2d297444da7822e75652a9949508b532`, a fresh
detached worktree passed the complete exact-source AMD64 Trixie/GNAT 14/
pinned-ALS build/check chain: 1,293 tests passed, one was deselected and
none skipped. Quality, packaging, documentation and actual ALS/MCP checks
passed. Independent file/directory queries confirmed both original
counterexamples now return the task owner.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

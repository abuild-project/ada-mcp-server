# Separate task-body dependency owners

Dependency graphs did not recognize separate task bodies as source owners.
A task subunit's ordinary context imports were attributed to the first inner
procedure, function or package declaration; with no such declaration, the
subunit was omitted entirely.

The existing forward declaration scan now recognizes complete task body
declarations. Context imports belong to the task's declared name, using the
existing unqualified convention for separate procedure and package bodies.
The separate parent does not become part of the public owner name. Whole
keywords, generic with/access exclusions, comment/string masking, ordinary
import scope, path handling, package-count semantics and response shape
remain unchanged. This is a bounded lexical correction; it adds no general
task-type or protected-unit parsing and does not expand the support matrix.

Two regressions cover a task body alone and a task body before an inner
procedure, including comments and line breaks. Separate procedure/package
controls retain the existing owner convention. The
[topic plan](../plans/separate-task-bodies.md) preserves the scope and the
original-base counterexamples.

A three-input Ada/GPR fixture declares a task and its separate body under a
parent procedure. The existing STDIO integration script queries that task
source and requires its exact dependency response. In a fresh owned copy,
GNAT 14 compiles the parent with a bounded timeout; the script retains the
command/output, requires a new parent ALI artifact and verifies hashes of
the three known Ada/GPR inputs. These checks do not observe arbitrary
filesystem writes. Existing generic, reading and additional controls remain
intact, including the three unaccepted native signature blockers.

At base `839325351058d37d2e9f59c90ef999b3b4989b1e`, the valid task
fixture compiles with the project's GNAT 14 image while the original handler
returns the inner procedure as owner. The body-only counterexample is
omitted entirely. Both original failures are retained as regression evidence.

At implementation revision `60daa8f80fddbf12b1d50d4b9097c1bb16a4223a`,
a fresh detached worktree passed the complete exact-source AMD64 Trixie/
GNAT 14/pinned-ALS build/check chain: 1,293 unit tests passed, with one
integration case deselected and no skips. Quality, strict typing,
distributions/Twine, documentation, completed-check provenance and actual
ALS/MCP/E2E checks passed. All 22 STDIO integration assertions passed,
including the exact Worker/Ada.Text_IO reply and GNAT compilation using
the same owned fixture paths. The parent ALI was absent before compilation
and its resulting hash was retained; the three input hashes matched the
committed bytes and remained unchanged.

Independent checks of both original counterexamples passed through the
handler and real STDIO for file and directory queries, with successful
GNAT 14 parent compilation and unchanged inputs. Separate procedure/package
owners remained unqualified. The public dependency query is lexical;
the separate compiler check establishes Ada validity. Neither establishes
general parser coverage or arbitrary write confinement. The real native
chain retained 27 reading and 53 additional-tool calls, with exactly the
three unchanged positional signature blockers unaccepted and
semantic_acceptance=false. No SDK/ALS pin, version, client policy or
support-scope change is included.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

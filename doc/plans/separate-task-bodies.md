# Separate task-body dependency owners

Base revision: `839325351058d37d2e9f59c90ef999b3b4989b1e`.

## 2026-11-16: Authorized bounded task-body correction

Decision: recognize complete task body declarations in the existing forward
unit scan. A task subunit's own ordinary context imports belong to that
task's declared name, using the same unqualified naming convention as
separate procedure and package bodies. Do not qualify the owner using the
separate parent. Without a recognized task body, the current scan either
attributes imports to an inner declaration or omits the subunit entirely.

Decision: add only the task body keyword form, retaining whole-keyword
boundaries, existing with/access introducer exclusions, comment/string
masking, ordinary import scope, response shape and file/directory behavior.
Do not add general task declarations, task types, protected-unit grammar,
parent qualification or a full Ada parser. Preserve the earlier
[generic-unit decisions](generic-unit-names.md) and their controls.

Decision: retain red results against the unchanged base for task bodies
with and without an inner procedure. Add those two regressions and small
separate-procedure/package controls; reuse one task case for comment and
line-break masking rather than adding a new matrix.

Decision: add a three-input Ada/GPR fixture with a parent procedure, task
body stub and task subunit. Extend only the existing STDIO integration
script with its exact dependency response, GNAT 14 compilation of the
parent in a fresh owned copy, a new parent ALI artifact and hashes of the
three known inputs. Bound the compile timeout and retain argv/output.
Configured build outputs and unchanged input hashes do not prove arbitrary
filesystem-write confinement. Keep the generic, reading and additional
controls, native fixtures, pins, version and support scope unchanged.

Decision: update the user changelog and concise topic record/index. This
separate topic retains all previous refs, counters and primary evidence.
Only the assigned developer edits candidates, without delegation or
external writes. Modest reused-image checks are development evidence;
complete exact-source container validation, fresh detached testing and
independent review remain required before the coordinator's PR handoff.
Stop before merge or release.

## 2026-11-16: Completed implementation evidence

Decision: record completed validation of implementation revision
`60daa8f80fddbf12b1d50d4b9097c1bb16a4223a` from a fresh detached
worktree. The exact-source image target is
`sha256:d539d82e5e88f589c7a8b67a917ddffdb662f3b451888fc9db6afe2d64aab07d`;
the committed source archive has SHA256
`11c538481fec881df41090daf99b1fe5201e9f46222d2db53c2cfe3ecabbffb5`.
The complete build/check chain passed with 1,293 selected unit tests, one
integration deselection and no skips. Ruff/format, strict Mypy,
distributions/Twine, documentation, completed-check provenance, real
ALS/MCP probes and E2E checks passed.

Decision: retain the 22/22 STDIO integration results. The exact Worker
owner and Ada.Text_IO dependency used the same owned fixture path as the
successful GNAT 14 parent compile. The parent ALI was absent beforehand
and its resulting hash was retained; exactly three known input hashes
matched the committed bytes and stayed unchanged. Independent checks of
both original counterexamples passed through the handler and real STDIO
file/directory queries, with valid parent compilation, fresh ALI and
unchanged inputs. Existing separate procedure/package owners remained
unqualified. The public query is lexical and GNAT establishes fixture
validity separately; no general parsing or write-confinement claim follows.

Decision: keep native source guards, stable process births and cleanup
with the passing diagnostic/reading controls and all 27 reading and 53
additional-tool calls. The three known positional cases retain their exact
unaccepted defect descriptors and semantic_acceptance=false. Preserve the
original failing base evidence and all earlier topic refs and records.

Decision: complete the record around this identified implementation proof.
The documentation-only completion still requires exact-head validation
and independent review before the coordinator's PR handoff. Do not claim
future validation as completed; stop before merge or release.

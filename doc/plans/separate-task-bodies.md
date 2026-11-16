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

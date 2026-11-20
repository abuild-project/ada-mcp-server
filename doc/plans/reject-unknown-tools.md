# Reject unknown tools before ALS startup

Base revision: `4e80d63e46bbb04d37bb1d9b1689ef39ca453566`.

## 2026-11-20: Authorized scope

Decision: reject names absent from the server's own advertised tool catalog
before ALS client acquisition or project selection. Return the existing JSON
server-error convention with `Unknown tool: <name>`, the tool context and an
available-tools hint. Use the existing `list_tools` function as the authority;
do not add a separate name registry or depend on SDK private caches.

Decision: preserve known-tool schema validation, the strict refresh Boolean
guard, routing and defensive dispatch fallback. Do not change dependencies,
schemas, versions, workflows or the accepted input-validation topic. Add one
short Unreleased entry and the required concise change record and sorted index
entry. Development documentation needs no additional description of this
bounded behavior.

Decision: strengthen the existing unknown-tool unit test to forbid client
acquisition and check its meaningful error. Add an absent-startup-marker
assertion to the existing real-stdio unknown-tool control. Keep the other three
positive controls and eight SDK rejection cases unchanged. Demonstrate the
new assertion rejects the original behavior with an owned baseline source
copy, without reverting the candidate or committing a runtime mutation.

Decision: the assigned developer alone edits the candidate; the assigned
tester and independent reviewer retain their separate roles without further
delegation. This new topic starts at local 0/3 and later PR 0/3. Run focused
host checks with locked SDK 1.30 as development evidence, then freeze a coherent
commit for fresh detached testing and independent review. The tester runs the
complete exact-source AMD64 Trixie/GNAT 14/pinned-ALS chain. Docker use awaits
the coordinator's resource window. No external push, PR, merge, release, tag,
archive action or history integration is authorized; the predecessor remains
unchanged and its eventual main integration requires a separate decision.

## 2026-11-20: Distinguish an advertised tool without a handler

Decision: after early catalog rejection, the defensive dispatch fallback
represents an advertised name without a handler. Report
`Advertised tool has no handler: <name>` with `context.tool` and no
available-tools hint. Preserve early unknown-name rejection, known handlers,
SDK schema validation, the refresh guard, dependencies and schemas.

Decision: add one behavioral unit test with a mocked catalog advertising a
synthetic tool and harmless mocked client acquisition. Require the accurate
fallback JSON error and tool context without using live ALS, source parsing,
a duplicate catalog or a routing matrix. Demonstrate failure against an owned
copy of the published runtime, then retain the existing startup and stdio
controls. Update the final-state record and preserve published history with a
separate bounded correction commit.

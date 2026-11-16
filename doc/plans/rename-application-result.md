# Rename application result

Base revision: `4d688e159339b8ae72726b99cca7be3f8d6d2dc8`.

## 2026-11-16: Authorized scope

Decision: reject `ada_rename_symbol preview=false` explicitly as unsupported
application before source synchronization or native prepare/rename requests.
Use the existing failure result shape with success=false, a clear error,
changes=[], total_changes=0 and applied=false. Add no writer or error framework.
Keep preview/default behavior, native replacement text, Boolean schema/default,
SDK/ALS pins, version, client policy and support boundaries unchanged.

Decision: the server's existing shared ALS client selection/initialization is
outside this fix. Rejection prevents rename-handler synchronization and native
prepare/rename; it does not promise that no ALS connection can be initialized.
Update the tool description and current support/assessment wording honestly,
plus an Unreleased entry. Preserve the previous topic's historical record,
plan, evidence, exhausted counters and all published refs.

Decision: keep this new topic bounded. Preserve base-red proof of false
applied=true with unchanged owned source bytes. Add a focused early-rejection
regression, preview/default preservation controls, and small catalog/dispatch
checks. Add one STDIO MCP rejection smoke to the existing integration script
using its initialized sample project and unchanged fixture hashes. Do not
expand the 53-call additional-tool harness, malformed-input matrices or CI
workflows. The sample project is the dedicated fixture in the owned CI source
snapshot; the call must not change it.

Decision: the coordinator assigns the existing separate tester/reviewer roles;
only the developer edits candidates and no recursive delegation is allowed.
This independent package starts at local 0/3 and later PR 0/3; prior counters
do not reset. Run focused host tests, quality/typing and maintained-doc checks,
then freeze one coherent initial commit with a concise final-state record.
The coordinator publishes an immutable validation ref for the required full
exact-source AMD64 Trixie/GNAT 14/pinned-ALS chain before local acceptance.
Host checks are development evidence, not native acceptance. No Docker,
external write, push, PR, merge, release, force update, reviewer-configuration
or unrelated runtime/client/harness change is authorized to the developer.

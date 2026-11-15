# Bounded reading-tool regressions

Base revision: `0ed9028faff834e2973945d17aefca12c2232736`.

## 2026-11-14: Scope and acceptance

Decision: strengthen repeatable reading/navigation evidence for
`ada_project_info`, `ada_workspace_symbols`, `ada_goto_definition`,
`ada_hover`, `ada_diagnostics`, `ada_document_symbols`,
`ada_find_references`, `ada_implementation` and `ada_type_definition`.
Keep other inherited tools, editing operations and SDK 2 migration for
separate topics. Do not change release pins, versions or support claims.

Decision: add a required MCP-to-pinned-ALS probe with an owned Ada fixture.
Require exact source locations, symbol names/kinds/hierarchy and reference
sets with and without declarations, excluding a same-name unrelated object.
Exercise type definition on an object identifier, declaration-to-body
implementation and a comment with no semantic target. Reuse existing explicit
parent GPR/scenario and generated-artifact Arca/Spawn/Anet view gates.

Decision: query before and after renaming an object in one MCP/ALS session.
Require new document symbols, definition, hover and reference results while
observing unchanged process IDs and start ticks. Hash Ada/GPR inputs around
each read-only call. Mutate only a new fixture copy, retain both source states,
raw requests/results and failure summaries, bound waits and require EOF cleanup
of the observed child. Existing diagnostic error/repair/error evidence remains
mandatory.

Decision: distinguish real protocol evidence from mocked oracle guards.
Deliberately empty, displaced, duplicated, unrelated or stale result payloads
must fail the same oracles used by the live probe. Host development checks
cannot establish real ALS or AMD64 Trixie acceptance. Preserve the complete
existing CI chain, including both Linux UID gates, and test the frozen
candidate through the hosted build/check workflow before claiming live proof.

## 2026-11-14: Independent hover-oracle refinement

Decision: require the full controlled object declaration and source position
actually emitted by the pinned ALS. Substring checks can accept a different
object or type, including Counter appearing only in a comment. Add exact
prefix/suffix, declaration and location corruption guards, and replay captured
Item/Other presentation payloads as mocked evidence. The replacement immutable
candidate still needs its own complete real build/check acceptance.

Decision: continue this topic on `codex/reading-regression-baseline`, with its
canonical change record at `doc/change-records/reading-regression-baseline.md`.
Preserve the earlier published topic branch and commits. Branch continuity
does not reset workflow counters, which remain outside tracked source.

## 2026-11-14: Changed semantic targets in the warm session

Decision: replace the rename-only mutation with a complete owned source
state outside the GPR's explicit Source_Dirs until copied into Main. Move
the object declaration from 3:4 to 5:4, change its record type from Counter
at reading.ads 2:9 to Alternate_Counter at 6:9, and replace the single use
at 6:40 with uses at 9:7 and 9:22. Reference counts including/excluding the
declaration must change from 2/1 to 3/2. Keep the original procedure's exact
specification, implementation and workspace targets unchanged.

Decision: keep both complete source states and their explicit expected
metadata in evidence, including hashes for the committed state template.
Require exact changed document and hover positions, definition, type target
and reference sets in the same observed process births. Replay old locations
with previews regenerated from the current source, including a still-valid
old Counter declaration and incorrect reference sets at the correct new
count. These mocked controls must reject stale locations independently of
stale preview text; the final source still needs real pinned-ALS acceptance.

## 2026-11-15: Runner and documentation guard sensitivity

Decision: test the complete runner with otherwise-valid mocked semantics.
Inject owned Ada, GPR and state-template changes, additions and deletions
during a call, vary each observed process PID/birth field after mutation,
and change only an owned temporary original-fixture copy. Require the exact
intended failure, before/after hashes, available arguments/results and normal
EOF attempts in the retained summary. Preserve changed process observations
before comparison, including the final no-target comparison. These controls
prove guard sensitivity, not real ALS or process-cleanup acceptance.

Decision: add healthy and separate missing/wrong/extra project-field and
namespace-envelope controls, and verify that disabling each previously
uncovered guard makes its corresponding committed tests fail. Substitute
the reading module's clock privately rather than patching the shared stdlib
clock. Enforce alphabetical change-record titles through the integrated
documentation checker and test a swapped index in an owned minimal tree.
The initial comment line remains serialized fixture metadata; semantic
no-target calls exercise the changed state. Final exact-head CI and independent
acceptance evidence belong in the PR, separately from host details in the record.

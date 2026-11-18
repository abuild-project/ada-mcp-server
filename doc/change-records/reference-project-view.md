# Imported-source project views

Queries anchored to an imported library could lose the explicitly selected
CLI project and omit callers outside the library. Selection now retains the
exact evaluated membership of the root and imported projects. File queries
preserve the deepest explicitly selected lexical ancestor, including nested
views. Outside those roots, canonical file identity selects the most recent
matching explicit view, including equivalent absolute paths and file symlinks.
Ordered search paths, scenario values and membership survive pool eviction.

A new ALS client configured for the exact explicit GPR/context supplies its
initial view without a redundant reload. Optional strict Boolean `refresh`
defaults to false: same-view repeats observe the live view without reloading
or invalidating readiness. True requests reevaluation on a reused client through
the native reload fence. Validation precedes client acquisition or selection
mutation. Changed paths/scenarios select their exact view; membership changes
needing reevaluation use explicit refresh. Freshness is independent of whether
a valid view contains sources. Successful selection retains recent-view order.

`complete=true` describes valid evaluated project metadata and membership.
The separate Boolean `indexing_complete` conservatively confirms observed,
quiescent indexing, with a new indexing begin required for a warm refresh.
False includes pending and unconfirmed states. Slow indexing preserves the
valid selection and live client; it no longer imposes a separate index timeout
on project selection. Real load, reload and wrong-view errors still fail.
Semantic queries retain their own completeness guards.

Focused controls cover fresh/warm and empty views, pending-to-ready progress,
client retention, invalid refresh, load errors, aliases, selection context and
native command ordering. The compiling STDIO control checks default repeat,
explicit unchanged refresh and three-reference initial anchors, then adds an
imported caller and requires four after explicit refresh, with
stable process births and preserved input hashes. It honors semantic readiness
separately. Additional-tool traces distinguish exact cold and warm setup while
retaining forbidden-action and existing signature controls.

Negative API controls compare against `7ec5a1713f9fa2a5e01d15ff40183e5d85d0edb9`.
Source-mounted development checks supplement the required complete exact-head
Trixie build/check, artifacts and numeric-identity validation; each immutable
head's evidence is recorded in a new PR comment. Larger-project Mac timing
remains pending before release under `doc/assessments/project-selection-timing.md`.
See `doc/setup.md` and `doc/plans/reference-project-view.md` for the contract.
The tool schema and generated full/lightweight skills describe that contract;
older compatible entries read their selected runtime's verified guide/catalog.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

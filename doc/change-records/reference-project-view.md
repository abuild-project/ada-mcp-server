# Imported-source project views

Queries anchored to an imported library could lose the explicitly selected
CLI project and omit callers outside the library. Selection now retains the
exact evaluated membership of the root and imported projects. File queries
preserve the deepest explicitly selected lexical ancestor, including nested
views. Outside those roots, canonical file identity selects the most recent
matching explicit view, including equivalent absolute paths and file symlinks.
Ordered search paths, scenario values and membership survive pool eviction.

A new ALS client configured for the exact explicit GPR/context supplies its
initial view without a redundant reload. Reused clients refresh through the
native reload fence before metadata is evaluated. Freshness is one-shot state,
independent of whether a valid view contains sources. Successful reselection
refreshes membership and selection order; ordinary file use does not.

`complete=true` describes valid evaluated project metadata and membership.
The separate Boolean `indexing_complete` conservatively confirms observed,
quiescent indexing, with a new indexing begin required for a warm refresh.
False includes pending and unconfirmed states. Slow indexing preserves the
valid selection and live client; it no longer imposes a separate index timeout
on project selection. Real load, reload and wrong-view errors still fail.
Semantic queries retain their own completeness guards.

Focused controls cover fresh/warm and empty views, pending-to-ready progress,
client retention, load errors, aliases, selection context and native command
ordering. The compiling STDIO control requires three references from initial
anchors, adds an imported caller and requires four after reselection, with
stable process births and preserved input hashes. It honors semantic readiness
separately. Additional-tool traces distinguish exact cold and warm setup while
retaining forbidden-action and existing signature controls.

Negative API controls compare against `ced1076fb1e87df0bc73f4702d31160aa0c8cfde`.
Source-mounted development checks supplement the required complete exact-head
Trixie build/check, artifacts and numeric-identity validation; each immutable
head's evidence is recorded in a new PR comment. Larger-project Mac timing
remains pending before release under `doc/assessments/project-selection-timing.md`.
See `doc/setup.md` and `doc/plans/reference-project-view.md` for the contract.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

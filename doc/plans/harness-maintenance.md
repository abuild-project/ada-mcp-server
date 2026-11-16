# Additional-tool harness maintenance

Base revision: `b3c3b9199dffe1461cf20f091b190e8c03e9aff9`.

## 2026-11-16: Approved internal decomposition

Decision: split the additional-tool control into explicit orchestration and
bounded phases, and extract shared fixture inspection, hashing, mutation,
MCP decoding and native tracing from the exploratory runner. Keep a small
control context for request evidence, the shared deadline, process identity
and source snapshots. Preserve the existing call order, arguments, native
requests, result oracles, failure evidence, cleanup and JSON/status shapes.

Decision: retain the real_additional.py CLI and the currently invoked
observe_additional.py --serve-trace path. Retain the optional exploratory
runner and its meaningful unit tests: those tests run in CI even though the
optional native exploration does not. Extraction removes the strict runner's
implementation dependence on exploration without widening this task to
delete or redesign the optional entry point.

Decision: preserve the three exact pinned-ALS positional signature blockers
as unaccepted with semantic_acceptance=false. Do not change product src/,
SDK/ALS pins, version, support scope or public contracts. Update existing
test imports and monkeypatch targets where implementation moves, retaining
their assertions and sensitivity. Add no feature, hardening, matrix or
structural line-count tests, and no user-facing changelog entry.

Decision: only the assigned developer edits this candidate. Use modest
focused host tests, Ruff/format, strict Mypy and documentation checks before
freezing one coherent unpublished commit above the accepted base. The
coordinator arranges immutable fresh-worktree testing, independent review,
the complete managed AMD64 Trixie/GNAT 14/pinned-ALS chain and checked PR.
Host checks are development evidence. Keep operational attempts outside
tracked source, retain previous topics' counters, and perform no recursive
delegation, native build, external write, push, merge or release action.

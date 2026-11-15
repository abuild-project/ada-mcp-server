# Bounded additional-tool regressions

Additional tools had individual mocked coverage without a complete bounded
MCP-to-pinned-ALS basis. Add a required source-derived fixture control for
call hierarchy, dependency graphs, completions, signatures, code actions,
rename previews, formatting edits, spec selection, builds and Alire manifest
metadata. Preserve the reading probe, complete existing CI chain, dependency
pins, prerelease version and documented support limits.

Fix four concrete correctness defects exposed by the regression work. A
legal bare LSP Command now preserves its string identifier instead of calling
dictionary methods on it. Rename previews preserve each native replacement
for both workspace-edit shapes. Dependency summaries mask character literals,
quoted strings and comments before ordinary with-clause/unit matching,
including doubled quotes and comment markers inside strings. Hierarchy
requests synchronize their queried file before native preparation; this is
not a global refresh of other changed open files. The changes have factual
Unreleased entries and leave published RC3 notes intact.

The control selects an exact owned GPR with explicit source and formatting
directories, dependency search paths and scenarios. It requires exact caller/
callee sets and native call-site ranges, controlled completion members,
signature declarations and ordered formals, a meaningful named-parameter
action proposal, single- and three-file rename edits, semantic spec targets
and separate filename fallback. An isolated Main-only mutation removes one
callee and moves another call before hierarchy runs. Repeating the original
action range on its replacement comment must remove the proposals. A later
complete package change explicitly synchronizes those other sources, moves
declarations, renames members, changes formal types/arity and adds a call site.
Exact changed results replace the warm values. Cross-unit rename requires
four native edits in three files and excludes the unrelated Increment.

Formatting edits must be bounded, nonoverlapping and meaningful, and must
reconstruct independently fixed bytes in memory. Only the fresh owned
fixture receives the explicit formatted state for a second query. Real
GPRbuild success must create the owned executable; a deliberate compiler
type error must report the exact source literal and two compiler messages.
All exposed TOML fields, changed metadata and missing/malformed manifest
negatives are checked. Input hashes include Ada/GPR/TOML and state templates,
separately from permitted generated obj/bin files. Raw MCP envelopes,
correlated native requests/results/errors, complete source states, process
births and normal EOF/child cleanup survive failures.

The initial immutable managed observation established meaningful native
responses for all ten tools and exposed stale hierarchy data and a native
positional-signature defect. The [capability assessment](../assessments/additional-tool-capabilities.md)
records its exact source and native evidence. Expected-correct positional
selection remains authoritative: three pinned-ALS replies select the wrong
formal. Strict mode fails them. The explicit CI assessment recognizes only
the three evidenced label/state/path/cursor combinations, requires matching
unchanged native requests and native/MCP integer indices excluding booleans,
and retains correct expectations versus wrong observations. Each remains
blocked with `accepted=false` and `semantic_acceptance=false`; the overall
status is `assessed-with-native-blocker`. A correct native index with a wrong
MCP index, other coordinates or any unrelated mismatch fails. Named
association checks supplement these cases; they do not accept or repair the
positional defect. All additional tools remain in development under the
unchanged support matrix.

Native rename application remains an inherited gap: `preview=false` reports
`applied=true` without writing sources. This work adds no writer. Preview,
actions and formatting do not silently edit consumer roots. The shipped
read-only client still requires explicit rename preview and denies formatting
and builds. Code actions expose discovery summaries, with native command
arguments retained for assessment but never executed. Dependency parsing
remains bounded to ordinary with clauses. Alire checks concern manifest
metadata, without an Alire toolchain or dependency workflow.

Focused host development checks passed 97 semantic/native-trace oracle
controls, 36 full-runner controls and 72 existing/new correctness tests.
They reject empty, duplicate, unrelated, stale and wrongly counted results,
invalid edits, incomplete native traces, unexpected input/build-output
changes, changed process births, original-fixture changes, timeouts and
cleanup failures. Separate native edit/command corruptions keep otherwise
healthy MCP summaries and must leave the call unaccepted. Native/MCP index
mismatches, Boolean indices and unevidenced positional cases cannot use the
known-native exception. An ENOSPC host attempt is retained separately;
subsequent batches were run individually and compacted after byte-hash
verification. Host tests are development evidence, not real ALS acceptance.
The retained exploratory harness's 40 host controls also passed against the
expanded fixture. Repository Ruff/format checks passed for 98 files, strict
Mypy passed the 40-file CI selection with its cache disabled, and maintained
documentation, index order, examples, CI shell syntax and whitespace passed.

Twenty-five in-memory sensitivity controls disabled one named boundary or
oracle at a time. Every corresponding committed counterexample failed and
no mutant survived. They cover source/build boundaries, process births,
original fixtures, request budget, EOF/child cleanup, native ranges/actions/
signature origin, known-case scope, action execution, trace completeness and
the semantic oracles. Candidate files stayed unchanged. Final exact-source
managed CI and independent tester/reviewer evidence belong in the PR packet;
this record does not preclaim them or promote public support.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

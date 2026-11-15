# Bounded additional-tool regressions

Additional tools had individual mocked coverage without a complete bounded
MCP-to-pinned-ALS basis. Add a required source-derived fixture control for
call hierarchy, dependency graphs, completions, signatures, code actions,
rename previews, formatting edits, spec selection, builds and Alire manifest
metadata. Preserve the reading probe, complete existing CI chain, dependency
pins, prerelease version and documented support limits.

Fix five concrete correctness defects exposed by the regression work. A
legal bare LSP Command now preserves its string identifier instead of calling
dictionary methods on it. Rename previews preserve each native replacement
for both workspace-edit shapes. Dependency summaries mask character literals,
quoted strings and comments before ordinary with-clause/unit matching,
including doubled quotes and comment markers inside strings. Hierarchy
requests synchronize their queried file before native preparation; this is
not a global refresh of other changed open files. The changes have factual
Unreleased entries and leave published RC3 notes intact.

Qualified quote-character literals, including whitespace around qualification,
also preserve the following string's masking boundary. A token such as
`Character'('"')` must not expose a fake unit declaration inside that string.
Ordinary character literals, attributes and ordinary with-clause scope remain
unchanged.

Signature help now gives the selected SignatureInformation's explicit active
parameter precedence over the top-level fallback, including zero. Missing
and valid out-of-range active-signature indices use signature zero. Only
the documented top-level fallback is clamped when its selected signature has
parameter information; per-signature values are not silently clamped.
Malformed raw indices remain visible for diagnosis and are rejected by the
integration oracle before classification. Only integers in the LSP unsigned
domain 0..2147483647 can use documented defaults; oversized used values remain
raw instead of becoming zero. Invalid unused top-level values do not override
valid per-signature precedence, and every raw field is still validated,
including unselected signatures and missing/empty parameter lists.
Response fields, version, pins,
capability negotiation and read-only policy stay unchanged.

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

Fixture inspection rejects symbolic links at the root, in ancestors and in
every file/directory entry, including dangling links and obj/bin. Original
fixtures are inspected before copying; copying preserves links for rejection.
Both exploratory and strict source mutations validate the complete existing
owned-file batch before the first write. A same-byte symlink substitution
cannot evade hashing or redirect a later source mutation. This controlled
harness does not claim a concurrent-filesystem sandbox.

Fixture traversal opens every directory explicitly with deterministic
scandir enumeration. Scan, stat and read errors propagate instead of being
silently omitted by recursive globbing. An unreadable root or subtree
therefore cannot masquerade as a complete unchanged snapshot, hide a
dangling link or permit an owned mutation before full inspection. The same
shared traversal protects both strict and exploratory runners.

Every one of the 40 ALS-backed calls requires its native request/result
evidence before semantic classification, including negative paths and known
blocked signatures. The 57 in-call exchanges include cold initialization,
project commands, document-symbol synchronization and hierarchy/rename
preparation. The independent native oracle checks correlation, request
coordinates/options and all exposed result fields without importing production
converters. Existing source-derived expectations remain the semantic authority.
Thirteen explicitly native-free calls require empty event slices; compiler,
manifest, dependency and filename-spec paths do not invent ALS provenance.

Native Position fields now require exact integers in 0..2147483647 before
conversion, indexing, slicing, copying or comparison. Boolean and float
aliases cannot become healthy integer coordinates through Python arithmetic
or set equality. Explicit standard containers cover nested and unexposed
range endpoints, locations/LocationLinks, child symbols, completion edits,
workspace edits and prepared hierarchy items. Opaque data and arbitrary
command arguments retain their protocol freedom; only the known ALS
where.position and extraction-location argument shapes are inspected.
Valid raw MAX becomes one-based MAX+1 (2147483648). Direct hierarchy/rename
set oracles check their corresponding one-based domain independently;
physical source expectations still reject incorrect fixture locations.

The initial immutable managed observation established meaningful native
responses for all ten tools and exposed stale hierarchy data and a native
positional-signature defect. The [capability assessment](../assessments/additional-tool-capabilities.md)
records its exact source and native evidence. Expected-correct positional
selection remains authoritative: three pinned-ALS replies select the wrong
formal. Strict mode fails them. The explicit CI assessment recognizes only
the three evidenced label/state/path/cursor combinations, requires matching
unchanged native requests and native/MCP integer indices excluding booleans,
using LSP effective selection rather than requiring the native fields to
agree generally. The known exception also requires the exact original raw
defect envelope and presence: both native parameter fields carry the same
wrong value, with the original selected signature/declaration/formals.
Valid differing fields pass normal effective selection; missing or changed
raw defect fields cannot borrow the exception. The control retains correct
expectations versus wrong observations. Each remains
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

Initial host development checks passed 97 semantic/native-trace oracle
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

The initial 25 in-memory sensitivity controls disabled one named boundary or
oracle at a time. Every corresponding committed counterexample failed and
no mutant survived. They cover source/build boundaries, process births,
original fixtures, request budget, EOF/child cleanup, native ranges/actions/
signature origin, known-case scope, action execution, trace completeness and
the semantic oracles. Candidate files stayed unchanged. Final exact-source
managed CI and independent tester/reviewer evidence belong in the PR packet;
this record does not preclaim them or promote public support.

The signature precedence correction has retained base-red evidence against
the previously accepted source: 23 failing cases exposed the actual handler
and native-oracle defects before either was changed. Independent literal
expectations cover per-signature zero, a selected second signature, absent
fields and documented fallbacks. Native-effective-correct/MCP-wrong and the
reverse direction both fail; malformed fields and new raw variants cannot
use the old exception. A host replay preserved all eleven previous native
signature replies and the three blocked cases; it is not a new ALS run.

The precedence-corrected source passed 317 focused host tests, including the new
precedence matrix, malformed-field preservation/rejection, effective-index
fidelity and exact raw-envelope controls. All 34 current in-memory sensitivity
mutations were detected with no survivors and no candidate-file changes
during the checks. These include removing only the effective-fidelity check,
which must expose a semantically correct MCP value hiding the wrong native
selection, and removing only the historical raw-envelope check. Repository
Ruff/format checks passed for 99 files, strict Mypy passed the 40-file CI
selection without a cache, and documentation/index/examples, CI shell and
whitespace checks passed. This host evidence does not replace the final
exact-source managed chain or independent tester/reviewer acceptance.

The complete uinteger-domain correction retained a further base-red run
against unchanged prior production/oracle bytes: nine failures and twenty
healthy controls. The resulting host basis passes 346 tests, including MAX,
MAX+1, Boolean distinctions, overridden top-level fields, unselected
signatures and empty/missing parameter lists. All 38 current in-memory
mutations are detected with no survivors or candidate-file changes during
the checks. Ruff/format for 99 files, strict Mypy for 40 files, documentation,
shell and whitespace checks pass. The eleven retained native replies remain
unchanged and the three original cases remain blocked; the replay supplies
no new real ALS acceptance. Exact final-source managed CI and independent
acceptance remain required.

The later evidence-boundary correction retained twelve base-red cases against
the unchanged published source. Focused development now passes 447 tests.
Ruff/format checks cover 101 files, strict Mypy covers 41 source files, and
documentation/index/examples, CI shell syntax and whitespace checks pass.
The retained current-PR CI replay preserves 53 calls, 50 accepted results and
the same three blocked cases; all 57 single native-pair deletions and all seven
reported wrong native payloads fail inside the offending call with
accepted=false. Seven additional shape-valid wrong-field controls establish
native/MCP fidelity rather than relying only on malformed reply rejection.
The replay uses explicit process/build stand-ins and supplies no new live
ALS or compiler proof. Seven focused in-memory mutations of the new native,
inspection, batch-write and lexical boundaries are detected. Their source
files stay unchanged during those checks. Failed development attempts remain
retained; one sensitivity attempt exposed a nonisolating multiline lexer
test, which now keeps the qualified literal and following string on the
same source line. Final exact-source managed PR CI and independent acceptance
remain required; no future CI result is claimed here.

The coordinate refinement retains seven base failures: five complete-runner
Boolean aliases and two direct semantic-set aliases. A passing control
confirms that existing recursive request equality already distinguishes
Boolean and integer coordinates. An independent retained-data assay rejects
all 514 malformed standard coordinate fields while accepting a recorded
completion with opaque data.line metadata and unchanged public results.
Domain tests preserve zero/MAX and the one-based offset; malformed types,
negative/overflow values and unused endpoints fail before interpretation.
The same 53-call native replay, three blocked cases, 57 pair-deletion and
seven wrong-payload counterexamples remain mandatory. All evidence is host
development or retained protocol replay; the final immutable source still
requires managed PR CI and independent acceptance.

The refined host basis passes 575 focused tests. Five targeted in-memory
mutations of coordinate validation, integer identity, lower/upper bounds and
the independent one-based set guard are detected with no survivors. Ruff
and formatting cover 102 files, strict Mypy covers 41 source files, and
documentation/index/examples, shell syntax and whitespace checks pass.

The final traversal regression retains six failing base cases and one
pre-existing passing file-read control under actual UID/GID 1000. The
mode000-directory regression proves a real scandir PermissionError before
checking snapshot rejection, and tests restore only owned temporary permissions in
finally. The new tests require nonroot execution without skipping, covering
source/generated subtrees, the root, both runners and writer preflight.
All 582 focused tests pass with zero skips. Ruff/format cover 103 files,
strict Mypy covers 41 source files, and documentation/index/examples, shell
syntax and whitespace pass. Retained current-PR CI data preserves 53 calls,
50 accepted results and three blocked signatures; all 57 native-pair deletions
and seven wrong native replies remain rejected. This is retained replay,
not a new live ALS or compiler run.
The required managed Trixie check enforces positive runtime UID/GID and must
run these regressions on the final source. Host or retained-data results do
not preclaim that managed CI or independent acceptance.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

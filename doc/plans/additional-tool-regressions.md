# Bounded additional-tool regressions

Base revision: `fe6aabec2f33a8766f6a63c9b35f670b89ed3cfa`.

## 2026-11-15: Scope and boundaries

Decision: cover the ten advertised tools outside the accepted reading probe:
`ada_call_hierarchy`, `ada_dependency_graph`, `ada_completions`,
`ada_signature_help`, `ada_code_actions`, `ada_rename_symbol` with explicit
`preview=true`, `ada_format_file`, `ada_get_spec`, `ada_build` and
`ada_alire_info`. Retain the nine-tool reading probe and every existing CI,
coverage, packaging, documentation, Arca/Spawn/Anet and Linux identity gate.
Keep MCP 1.30.0, version 0.2.0-rc.3 and all release, plugin and support
boundaries unchanged. Pure test changes need no changelog entry; actual
user-facing correctness fixes need a factual entry.

Decision: only the assigned developer edits candidates. The coordinator
assigns the separate tester and independent reviewer. The new bounded
package starts at local 0/3 and later PR 0/3; the previous reading topic's
closed counters remain intact. Evidence and counters live outside source.
Normal maintainer handoff precedes PR submission. This scope does not
authorize merge, release, publication, force pushes or GitHub writes by
the developer.

Decision: native rename application is outside this work. The inherited
handler returns `applied=true` for `preview=false` without writing files.
Reproduce and document that gap using owned data, preserve read-only client
denials, and obtain a maintainer decision before implementing any writer.
Formatting returns edits; its tests must not silently apply them to consumer
roots. Alire acceptance concerns manifest metadata, not an Alire toolchain.
Advertising 19 tools does not establish support for all 19 tools.

## 2026-11-15: Implementation and acceptance plan

Decision: use a small committed Ada/GPR fixture with explicit Source_Dirs,
Object_Dir and Exec_Dir, two source-bound calls, a separate same-name symbol,
a package specification/body, deliberately uneven formatting and exact
`alire.toml` metadata. Copy it into a new evidence-owned directory before
starting a session. Hash all Ada, GPR and TOML inputs separately from allowed
generated obj/bin files. Retain source states and raw evidence on failure.

Decision: propose one frozen managed-CI observational phase before selecting
implementation-specific pinned ALS expectations. Run the exact committed
source through the existing AMD64 Trixie/GNAT 14/pinned ALS build/check
environment. Add test-only child instrumentation around ALS requests to
retain native initialize capabilities, request parameters, results and LSP
errors while preserving production dispatch and responses. Retain MCP
protocol and stderr separately. This phase is exploration, not positive
semantic acceptance; empty results cannot establish a working capability.
Unsupported methods are explicit blockers with their native error/capability
evidence. Do not weaken a fixture or add a skip to hide them.

Decision: observe call hierarchy as the first file-semantic call after explicit
GPR selection, then warm it and request incoming/outgoing/both directions.
Acceptance requires exact expected source-bound caller/callee names, kinds,
files and coordinates, excludes the unrelated same-name symbol, and includes
a genuine no-symbol comment. Retain the native call-site ranges even though
the current MCP summary omits them. Assess absent synchronization separately
before any routine correction backed by a failing regression.

Decision: dependency acceptance requires an exact bounded set of ordinary
with-clause edges for a file and directory, the exact unique unit count and
an explicit missing-path negative. The current regex is not a complete Ada
parser: comments, string literals, limited/private clauses and multiline
forms require explicit assessment and targeted failing examples before any
production change. Do not call this a complete semantic dependency graph.

Decision: completion acceptance selects known package members at an exact
source position and checks their labels, kinds and insertion values, limit
behavior and completeness metadata. Signature acceptance selects the known
overload and active parameter at separate arguments, checking the complete
parameter labels. Include a comment/no-call negative. Freeze exact native
presentation expectations after observation, independently of handler code.

Decision: code-action acceptance requires a known meaningful action at the
controlled source range, its exact title/kind/preference/edit-file count and
unchanged source hashes. Preserve native edit ranges/replacements or command
IDs/arguments for independent assessment. The MCP handler exposes summaries,
so this scope does not add a public edit/apply API or claim to execute actions.
A bare legal LSP Command and an empty native action result need explicit
unit/negative coverage; unsupported positive behavior is a blocker.

Decision: rename preview acceptance requires the exact complete edit set,
old/new names and file/change counts, confirms every old token against source
and excludes the unrelated symbol. Reject invalid identifiers and a genuine
non-symbol location. Preview calls must return `applied=false` and preserve
all source inputs. Keep the existing client prohibition on native application.

Decision: formatting acceptance requires nonempty valid bounded edits whose
application in memory produces an independently fixed formatted source.
Request formatting of that text only after writing a separate fresh owned
copy; require the expected already-formatted result. Check edit positions,
replacement text, count and file, and reject out-of-bounds/overlapping/no-op
payloads in oracle guards. Never apply returned edits outside owned copies.

Decision: spec acceptance checks a source-bound body-to-spec declaration
target, explicit sibling-file fallback and a missing-spec unit with no
sibling. Preserve the distinction between a native semantic target and the
fallback's file-level 1:1 result; an empty declaration response followed by
fallback is not semantic navigation evidence.

Decision: build acceptance invokes the actual GPRbuild only on the fresh
owned project, with generation confined to its explicitly declared obj/bin
directories. Require success, zero errors and an executable, then change
only an owned source to a deliberate compiler type error and require failure
with the exact source-bound error location/message. Retain both input states
and before/after input hashes separately from generated files. The compiler
control supplements rather than replaces the repository compiler/CI chain.

Decision: Alire acceptance compares every exposed field to exact committed
TOML metadata, including dependency constraints, profiles, externals and
project/executable lists. Separate fresh copies provide malformed and missing
manifest negatives. No `alr` execution or dependency download is evidence of
this manifest-reading tool's contract.

Decision: positive live oracles receive deliberately empty, wrong, duplicate,
unrelated and stale payloads, plus invalid edit ranges/text and wrong compiler
or manifest data. Full-runner controls inject input additions/deletions/
changes, generated files outside obj/bin, original-fixture changes, process
birth changes and cleanup failures with otherwise healthy semantics. Each
counterexample must hit its intended guard and preserve available evidence.
Disable each guard in memory and require its committed counterexample to
fail, addressing the preceding topic's surviving-guard lesson.

Decision: host development uses the existing external venv with bytecode off
and modest focused tests. Preserve failed logs and archive/verify before
removing only this task's repetitive temporary pytest data. No local Docker
build/load/prune, image deletion, large artifact downloads or host compiler
substitution is permitted under the current disk limit. Freeze clean coherent
unpublished commits before independent testing and review of the same revision.

## 2026-11-15: Approved capability observation

Decision: the coordinator approved one exploratory execution ref,
`codex/validation/additional-tool-observation`. The canonical topic remains
unpublished at its accepted base while the coordinator snapshots and pushes
that immutable observation. This execution ref does not reset scope or
correction counters. The complete existing managed CI remains mandatory.
Native tracing preserves decoded request parameters, results and exceptions,
including the unchanged initialize request and its capability response. It
does not claim a complete LSP wire or callback transcript.

Decision: include `formatting` explicitly in the selected GPR Source_Dirs.
The known action trigger is naming positional arguments in the Combine call;
the action request spans that invocation, alongside declaration/comment
observations. Keep compiler outputs under owned obj/bin using explicit `-p`.
Before the deliberate compiler error, restore the original valid sources.
Observe a complete warm source mutation that moves and renames the callee,
changes the signature's formal types/arity and adds a caller edge. Call
hierarchy runs first after that mutation, before a synchronizing handler.

Decision: preserve targeted synthetic reproductions of the inherited bare
LSP Command crash and the rename handler ignoring native replacement text.
They are handler robustness evidence, not actual ALS capability evidence.
Propose bounded corrections to the coordinator before any production edit.

## 2026-11-15: Observed behavior and bounded corrections

Decision: the frozen observation completed the unchanged managed chain at
revision `0950488ebbdc9710d59c5a5ed28b288d4ba00deb`. All ten tools produced
meaningful positive observations, while native source staleness and signature
selection issues remain separate from capability discovery. Final semantic
acceptance still requires independent oracles and the final immutable source.

Decision: the coordinator approved three bounded corrections after base-red
reproductions. Summarize a legal bare LSP Command's string identifier without
calling dictionary methods on it. Preserve each native rename replacement
in preview output for both workspace-edit shapes. Mask Ada comments and
double-quoted strings before the existing dependency regexes, respecting
doubled quotes, comment markers inside strings and line boundaries. Keep
ordinary with-clause scope, the response shapes and read-only client policy.
These actual user-facing fixes require the changelog entries above; the
original test-only changelog exception does not cover them.

Decision: assess the native positional signature-selection discrepancy rather
than accepting the observed indices as correct. MCP converts coordinates
to LSP correctly; the pinned native response already contains the unexpected
index. The independent source-derived actual-to-formal expectation remains
authoritative. No upstream implementation is imported or silently patched.

Decision: isolate call-hierarchy source synchronization with a main-only
mutation that removes an existing callee edge while package sources stay
unchanged. Hierarchy must run first after that mutation. The earlier complete
three-file change cannot prove that synchronizing one queried file refreshes
every other open source. Any routine synchronization fix needs a targeted
failing regression and final live proof; no global refresh is authorized.

## 2026-11-15: Current test scope and native blocker

Decision: the coordinator bounded this work under the existing maintainer
instruction to keep unassured functions in development. A pre-existing
external ALS defect does not require a new public-support decision to finish
unaffected tests and the four routine correctness fixes. This is not a
maintainer answer approving a native-defect option. The preference for
separate ALS work remains unresolved; no answer is assumed.

Decision: keep strict signature checks as the default. The CI assessment
option permits only the three primary-evidenced positional cases, correlates
their exact unchanged native request/cursor and integer native/MCP indices,
and records expected-correct versus observed-wrong results as blocked with
`accepted=false` and `semantic_acceptance=false`. Correct-native/wrong-MCP,
boolean indices, other labels/states/paths/cursors and unrelated mismatches
fail. The overall status is `assessed-with-native-blocker`, not passed.
Named-association positives supplement rather than replace those cases.

Decision: add a three-file native WorkspaceEdit preview for Increment's
specification, body declaration/end and Main call. Require four exact edits
across three files and exclude the unrelated Increment. After the main-only
hierarchy mutation, repeat the original code-action range at 5:15–5:36 and
require the original three proposals to disappear from the new comment.
Do not claim isolated action synchronization after hierarchy already refreshed
Main. Keep every native postcondition inside the call's acceptance boundary.

Decision: preserve the host ENOSPC attempt and partial evidence. Subsequent
focused batches run separately; completed owned pytest trees are archived,
byte-hash verified and only then removed. Regenerable task caches may be
removed explicitly; immutable source, raw CI and older evidence remain intact.

Decision: freeze the first strict managed run on execution ref
`codex/validation/additional-tool-round-1`, preserving canonical unpublished
topic history. Prepare coherent correctness and regression commits with
their own maintained tests. The coordinator retains the exact source and
managed evidence; independent roles assess that immutable head. A local
canonical fast-forward to identical accepted commits changes no tested bytes.
Do not rewrite published validation history or reset correction counters.

Decision: all 25 named in-memory guard/oracle mutations were detected by
their committed counterexamples, with candidate files unchanged. Preserve
those expected failures separately from healthy host checks and final real
MCP/ALS evidence. No host mock or cached runtime substitutes for the required
exact-source managed chain.

## 2026-11-15: Selected signature precedence and oracle correction

Decision: the maintainer accepted a bounded fifth correctness fix. Use the
selected SignatureInformation's activeParameter when present, including zero;
otherwise use the top-level/default value. Missing and valid out-of-range
activeSignature selects zero. Normalize only the documented top-level
parameter fallback when selected parameter information exists. Do not invent
per-signature out-of-range clamping. Safe lookup avoids accidental Python
indexing of malformed native values, which remain visible for diagnosis.

Decision: the independent native oracle follows effective LSP precedence,
without importing production conversion logic. Correct effective selection
with differing native fields passes; wrong MCP conversion and a semantically
correct MCP value hiding wrong native selection both fail. Malformed raw
indices are rejected before healthy or known-defect classification. The
historical exception still requires its three exact contexts and exact
original raw envelope/presence, including both explicit native parameter
fields carrying the same wrong index. No new native variation is accepted
under that exception, and the three original cases remain blocked.

Decision: continue the same topic and counters on a new execution worktree
and ref, codex/validation/additional-tool-round-2, created from the accepted
base and populated from the prior accepted tree before this correction.
Preserve all earlier published refs, commits, authorship and sealed evidence;
the old canonical local ref stays at its prior accepted head until coordinated
promotion. Assemble two coherent new fix/test commits before first PR rather
than amending, rebasing or force-updating published validation history.

Decision: preserve base-red evidence against unchanged production and oracle
bytes at 452a32f546704b72bbb2477ec504cc5433c13587. The first targeted run
failed 23 cases before the correction, while 28 cases passed. A replay of
retained prior native observations preserves all eleven public replies and
the three historical blocked cases, but supplies no new real ALS acceptance.
The corrected immutable source still needs the full managed chain and
independent testing/review. Release, merge and publication remain outside
this work; the accepted plan authorizes the later normal PR/Copilot phase.

Decision: the current host basis passes 317 focused tests and all 34 named
in-memory mutations are detected, including independent effective-fidelity
and exact-envelope checks. Preserve the earlier and current evidence without
resetting the topic counters. The maintainer explicitly requested normal
PR/Copilot rounds for this package without waiting for an upstream ALS fix;
the three original native cases remain blocked and support is unchanged.

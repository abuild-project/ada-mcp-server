# Generic unit names

Base revision: `4e8a5ebb70b879c7b5b2c7dd297ca6bd3dc72fc5`.

## 2026-11-16: Authorized scope

Decision: identify the actual Ada unit owning ordinary context imports when
generic formal subprograms/packages or access-to-subprogram profiles precede
it. Skip those non-unit candidates using their masked declaration context.
Keep the existing comment/string masking, ordinary with-clause scope, response
shape and file/directory behavior. This is a bounded lexical correction, not
a complete Ada parser or support expansion.

Decision: preserve exact base-red owner/dependency results before fixing the
handler. Use a few distinct formal declarations and ordinary/generic unit
controls. Add a small valid Ada/GPR fixture and extend the existing STDIO
integration script with its exact dependency result and GNAT compilation in
a fresh owned copy. Bound compilation time, confine generated outputs and
verify unchanged source/GPR hashes. Do not change the additional-tool harness,
CI workflows, SDK/ALS pins, version, client policy or unrelated source.

Decision: this independent topic starts at local 0/3 and later PR 0/3; earlier
topics, counters and sealed evidence remain unchanged. Only the developer
edits candidates. The coordinator assigns separate tester/reviewer roles and
handles external delivery. Run focused host tests, quality/typing and docs
checks, then freeze one coherent commit. Host checks do not replace the
required exact-source AMD64 Trixie/GNAT 14/pinned-ALS CI chain. No external
writes, Docker build, merge, release, force update or delegation is authorized
to the developer.

## 2026-11-16: Bounded keyword and evidence correction

Decision: local correction 1/3 addresses the valid named formal access type
`Callback_Function`, which was misread as the keyword `function` inside an
identifier. Require whole-keyword unit matches. Sharpen the existing access
profile regression and compiled fixture without adding a case matrix or
changing ordinary imports, masking or support scope.

Decision: narrow the integration claim to hashes of its three known Ada/GPR
inputs, configured owned build directories and the required new ALI artifact.
This replaces the earlier output-confinement wording; it does not establish
observation of arbitrary filesystem writes. Add no traversal or filesystem
hardening machinery.

Decision: preserve the immutable initial revision
`076cfee91dcb055519db01990beacc2f447215da`, its validation ref and all
evidence. Assemble the unpublished topic and correction as one coherent
commit on the original base in a fresh validation worktree. The coordinator
retains the canonical ref until acceptance and runs the full exact-source
managed chain. The package remains at local 1/3 and PR 0/3; prior topics and
counters do not reset. Developer external writes remain unauthorized.

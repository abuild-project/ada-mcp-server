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

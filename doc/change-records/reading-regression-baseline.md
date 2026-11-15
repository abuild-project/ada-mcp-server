# Bounded reading-tool regressions

Reading tools previously combined broad real-ALS count checks, individual
source proofs and mocked tests. Add a required MCP-to-pinned-ALS fixture
probe for exact navigation targets, document hierarchy and reference sets,
so empty, unrelated or stale results cannot satisfy those checks.

The probe selects an explicit GPR with empty dependency search paths and
scenario overrides. It covers project information, workspace and document
symbols, definitions, object type definitions, implementations, hover,
references and clean file diagnostics. Reference sets include and exclude
the declaration and reject an unrelated object with the same name. Workspace
queries use a distinctive fixture symbol and require exact complete,
untruncated sets after both declaration and body are open. Document symbols
require exact semantic names, kinds, positions and hierarchy, while validating
the pinned ALS synthetic context-clause namespace separately.

An owned source mutation moves the declaration from Main 3:4 to 5:4, changes
its record type from Counter at reading.ads 2:9 to Alternate_Counter at 6:9,
and replaces the use at Main 6:40 with uses at 9:7 and 9:22. Exact reference
counts including/excluding the declaration change from 2/1 to 3/2. The new
document positions, definition, type, hover and reference results must replace
warm results within the same observed MCP/ALS processes. A comment
provides a genuine no-target case. Each read-only query preserves Ada/GPR
hashes, including the committed replacement state outside explicit GPR
Source_Dirs; only the fresh fixture copy is deliberately mutated. Raw protocol,
results, complete source states, exact state metadata, hashes and summaries
survive failures. Requests have individual and total bounds; normal MCP EOF
and exit of the observed ALS birth are required.

Hover requires the exact controlled declaration and its source position in
the presentation emitted by the pinned ALS. Guards reject object and type
prefixes/suffixes, a type mentioned only in a comment, changed initializers
and incorrect source positions. Mocked warm-state controls pair old definition,
reference and type locations with previews freshly regenerated from the current
source. They reject the still-valid old Counter target and incorrect reference
sets even at the correct new count. These controls do not replace real
acceptance of the final immutable candidate.

Healthy full-runner controls accompany injected Ada/GPR/template changes,
source additions/deletions, changed MCP/ALS PIDs and birth ticks, and changes
to an owned temporary original-fixture copy. Each counterexample must reach
its intended guard with otherwise-valid semantic replies, fail with the
exact error and retain available call/hash/process and EOF evidence. Separate
project source/main-field and namespace-envelope controls reject missing,
wrong and extra data. The cleanup clock substitute is local to the reading
module. The initial comment line remains serialized metadata; no-target
navigation and hover run against the changed state.

Mocked guard tests deliberately corrupt expected-result payloads with empty,
wrong, duplicate, unrelated and stale results. These test the live oracles and
failure evidence handling; they do not provide real ALS acceptance. Existing
parent-GPR/scenario, diagnostic error/repair/error, Arca/Spawn/Anet and both
Linux identity gates remain mandatory. Host development details appear below.
The PR links final exact-head AMD64 Trixie CI and independent acceptance
evidence after those checks complete; this record does not preclaim them.
No runtime behavior, SDK pin, version, release asset or support claim changes.

The documentation checker enforces alphabetical titles in the change-record
index. Its integrated minimal-tree controls accept the healthy order and
reject a swapped index without weakening link, example or version checks.

Targeted host development validation passed 103 tests covering semantic
oracles, full-runner failures, process observation, diagnostics, navigation,
symbols and integrated documentation checks. Repository Ruff checks and
format checks passed for 90 files; strict Mypy passed for the
37-file CI selection including the new probe. Maintained documentation,
example syntax, CI shell syntax and whitespace checks passed. These checks
exercise mocked guards and source contracts. Real MCP/ALS outcomes require
the complete hosted build/check run of the immutable candidate; no local
Docker or host-compiler substitute was used.

The untouched 72-test guard/documentation suite also passed an in-memory
sensitivity control. Disabling each source-hash, post-mutation identity,
original-fixture, project source-directory, project main-unit and namespace
guard made its intended committed counterexamples fail. Disabling the sorted
index invocation and final no-target identity comparison likewise failed
their corresponding tests. Each mutation changed exactly one check in memory;
candidate bytes stayed unchanged. These expected failures establish guard
sensitivity rather than live ALS behavior.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

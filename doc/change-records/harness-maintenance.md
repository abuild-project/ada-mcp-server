# Additional-tool harness maintenance

The required additional-tool control combined session orchestration, evidence
guards and its entire scenario in one function. It also imported fixture and
native tracing helpers from the optional exploratory runner. That coupling
made the required checks harder to follow and maintain independently.

scripts/real_additional.py now runs six explicit phases: initial queries,
edit previews and spec targets, the isolated main-only change, the full
semantic change, manifests and owned builds. A private control context holds
the existing session, source snapshots, process identity, total deadline and
per-call evidence checks. Setup and finalization retain their original failure
boundary. In particular, the main-only hierarchy call still precedes every
other handler after that source change, and changed packages synchronize
before the later semantic queries.

scripts/additional_support.py owns the shared fixture inventory/hash guards,
whole-batch mutation validation, MCP decoding and test-only native tracing.
Both runners use those helpers directly. The existing real_additional.py CLI
and observe_additional.py --serve-trace child path remain available. The
optional exploratory --output runner remains because its boundary tests run
in CI and deleting it would broaden this maintenance change. Those tests now
patch and exercise the actual shared helper lookups.

The refactor preserves call order and arguments, MCP/native results, source
states, input hashes, process births, cleanup and complete available failure
evidence. The three exact native positional signature discrepancies remain
blocked, unaccepted and semantic_acceptance=false. Product sources, SDK/ALS
pins, version, support scope and public contracts are unchanged.

Development checks for this candidate based on
`b3c3b9199dffe1461cf20f091b190e8c03e9aff9` pass the existing affected host
tests, including native corruption, source mutation, deadline, nonroot
inspection and lifecycle failures, plus Ruff/format, strict Mypy and
documentation checks. These host mocks do not establish native acceptance;
the unchanged managed AMD64 Trixie/GNAT 14/pinned-ALS check chain and
independent immutable review remain required.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

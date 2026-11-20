# Validation reference retention

Temporary validation branches can outlive merged work, while superseded heads
may carry snapshots required by earlier retention decisions. Cleanup requires
maintainer authorization for that occasion's named refs and actions; later
cleanups need new authorization. The same authorized operations need no repeat
request. AGENTS.md links safeguards for active work, exact-source reachability,
annotated source tags, verified remote protection and guarded deletion. Archive
tags never move or overwrite snapshots.

The [retention assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/validation-ref-retention.md)
records thirteen audited source heads, six required annotated source-snapshot
tags and the separate published CI-evidence archive. The binary CI Git archive
is a one-off exception. Prefer release assets outside Git object history for
future CI evidence; an explicit maintainer decision on storage and destination
is required before the next archive. No destination is selected here, and the
existing protected archive remains unchanged. Immutable identities, hash
receipts, dated protection/access observations and evidence-format boundaries
are detailed in the assessment. Append-only plan additions preserve earlier
text and counters. Workflow artifact retention remains fourteen days.

This changes internal process documentation only, with no runtime, helper,
dependency, version, workflow or support change. Documentation/link/index and
whitespace checks cover the prose. Exact-head hosted CI, tester and independent
reviewer evidence are recorded separately for the frozen candidate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

# Validation reference retention

Temporary validation branches can remain after merge, while superseded heads
may still carry source snapshots required by earlier retention decisions.
Cleanup requires maintainer authorization for that occasion's named refs and
permitted actions; later cleanups require new authorization. The same
already-authorized operations need no repeat request. AGENTS.md states this
boundary and links the development guide's safeguards: preserve active work
and open pull requests, confirm exact-source reachability for merged heads,
and retain superseded heads with annotated archive tags before guarded branch
deletion. Verify remote targets and effective protection against archive
updates/deletion first. Archive tags must never move or overwrite snapshots.

The [retention assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/validation-ref-retention.md)
records thirteen audited source heads, six verified annotated source tags and
the published public CI-evidence archive outside main. It identifies immutable
objects and hash receipts, dates protection/access observations and distinguishes
connector-serialized logs from original validation ZIPs. Dated plan additions
replace branch retention with source preservation without altering earlier
text or counters. Source tags do not extend the workflow's fourteen-day
artifact lifetime.

This changes internal process documentation only, with no runtime, helper,
dependency, version, workflow or support change. Documentation/link/index and
whitespace checks cover the prose. Exact-head hosted CI, tester and independent
reviewer evidence are recorded separately for the frozen candidate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

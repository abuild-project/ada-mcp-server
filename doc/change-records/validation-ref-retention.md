# Validation reference retention

Temporary validation branches can remain after merge, while superseded heads
may still carry source snapshots required by earlier retention decisions.
AGENTS.md now permits conditional cleanup within the maintainer's authorized
scope: preserve active work and open pull requests, confirm exact-source
reachability for merged heads, and preserve superseded heads with annotated
archive tags before guarded branch deletion. Remote targets and effective
protection against archive updates/deletion must be verified first. Archive
tags must never move or overwrite earlier snapshots.

The [retention assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/validation-ref-retention.md)
records thirteen audited source heads, six verified public annotated tags
and a separately retained CI-evidence handoff with hash receipts. Dated
additions to the affected historical plans replace branch retention with
source preservation without altering earlier text or counters. These facts
do not certify branch deletion or continuing server-side protection. Tags
do not extend the workflow's fourteen-day artifact lifetime.

This changes internal process documentation only, with no runtime, helper,
dependency, version, workflow or support change. Validation uses the existing
documentation/link/index checker and whitespace checks, with separate tester
and independent-reviewer verification of the frozen candidate and unchanged
source/test bytes. The assessment binds preservation evidence to its exact
original sources; head-specific candidate validation remains separate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

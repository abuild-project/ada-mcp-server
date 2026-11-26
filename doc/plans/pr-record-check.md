# Pull request record check

Base revision `d5bf50a5932fc79bcef96900ab513cf68aa2ba9f` contains the
[Code Review Rules](../../AGENTS.md#code-review-rules) this check enforces.

## 2026-11-25 — Scope and decisions

Add a separate, read-only workflow for pull request opens, edits, new head
commits, reopens and transitions to ready for review. Check out the pull
request's exact head with the existing immutable checkout pin. Read the head
ref and body from the event file and derive the canonical change record using
the branch rule in AGENTS.md. Require a regular file in `doc/change-records/`
and reject symlinks. Convert CRLF to LF and ignore whitespace only at the end
of the body and record. Report a missing record or show a bounded unified diff
for a mismatch.

Apply the same rule to Dependabot. The seven merged dependency PR bodies were
compared with the change records at their final head revisions. All seven
matched byte for byte. The one closed, unmerged dependency PR kept its generated
body and had no change record. A generated body can fail until the maintainer
commits and posts the record.

Add targeted tests for the normalization, path derivation, failure cases and
event input. Demonstrate sensitivity with an exact comparison and a broken
branch derivation. Use the complete local chain and independent review on the
immutable candidate, then post PR-head validation in its own comment. Requiring
the workflow check in repository settings is a separate maintainer action.

## 2026-11-26 — Use the base checker with the head record

The first workflow runs the proposed checker, so a head can remove or weaken
the check itself. Keep the dedicated read-only `pull_request` workflow and
check out the event's exact base and head with the existing pin and credential
persistence disabled. Run the base checker with the head checkout as its
working directory.
Log the head-checker fallback when the base has no checker, as on first
adoption. Fail the job for an unusable base checker or a failed comparison.
Review changes to the workflow definition through the usual PR process.

Reserve the exact derived topics `CLAUDE` and `CLAUDE.local` to align with the
sibling Arca Claude review workflow, which removes those Markdown filenames
from its review checkout.

Exercise the workflow command with different base and head records, an absent
or weakened head checker, and absent or unusable base checkers. Include a
matching record for each reserved name. Replay the new regressions against
published revision `eb8f80e46e20fa47d915360ea6271de41116502d` to confirm they
detect the previous behavior. Post actual validation of the corrected PR head
in a new comment for that revision.

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

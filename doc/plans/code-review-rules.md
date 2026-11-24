# Code review rules

Base revision `cb3102163690d99d30683ae988d4e6256bddd994`.

## 2026-11-24 — Maintainer decision

Add a short [Code Review Rules](../../AGENTS.md#code-review-rules) section to
AGENTS.md that directs reviewers to report the six specified findings as P1.
Apply it to PR-head validation evidence, sensitivity to previous behavior,
main-integration merge contents, contradictions in governing documentation,
verification of external dependencies and upstream behavior, and agreement
between the PR body and committed record.

The scope covers AGENTS.md, this plan, the change record and its index entry.
Check maintained documentation and diff whitespace during development. The
tester and independent reviewer verify the same immutable candidate before
submission. Record validation against that head in its own PR comment.

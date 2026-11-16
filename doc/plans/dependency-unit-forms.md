# Dependency unit and context forms

Base revision: `ebed7fd59c848b6a0fb2354a4feeff233ec99efc`.

## 2026-11-16: Approved lexical additions

Recognize complete protected body declarations alongside task bodies in the
existing forward scan. Keep declared subunit names unqualified. Recognize
ordinary with clauses and the valid optional prefix order limited, then
private, including limited private with. Collect all names in the existing
deduplicated, sorted depends_on list without visibility metadata.

Retain keyword boundaries, masking, generic exclusions and response shape.
Use focused owner/context regressions and one four-input Ada/GPR fixture:
package specification, parent body, protected subunit and project file.
First compile it with GNAT 14 and preserve the unchanged-base failures.
Require exact specification/subunit replies over real STDIO, parent
compilation, a fresh ALI and unchanged known inputs in an owned copy.

Keep native controls, pins, performance checks and unrelated topics intact.
Only the assigned developer edits; reused-image checks are development
evidence. The tester validates an immutable candidate in a fresh worktree
through the complete canonical chain; independent review precedes PR
delivery. Record later head validation in PR comments. No developer external
writes, merge or release.

## 2026-11-16: Context-only import scan

Collect imports before the selected unit. Cover Stop's multiline aspects
with focused regressions and the existing compiled STDIO fixture.

## 2026-11-16: Generic formal boundary

End context imports before generic or the selected unit. Retain both
aspect regressions and compile their shared fixture.

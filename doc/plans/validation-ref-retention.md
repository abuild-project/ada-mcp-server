# Validation reference retention

Base revision: `67b93c7cc337ef307913e2760562b152a32a74d7`.

## 2026-11-19: Conditional cleanup and archival substitution

Decision: permit post-merge cleanup of inactive temporary validation branches
within the maintainer's existing scoped authorization. Preserve active work
and open pull requests. Remove an unchanged redundant branch only when its
exact source is reachable from main. Preserve a superseded source through an
annotated `archive/<original-branch>` tag pinned to its exact SHA before
deleting its unchanged branch. Record branch, SHA and reason in the tag.

Decision: verify each remote tag object and peeled target and effective
archive-namespace protection against updates/deletion before guarded deletion.
Never move or overwrite archive tags. Stop for changed heads, active work,
conflicting tags or failed preservation/protection. This authorization covers
the thirteen branches and six archive mappings in the
[retention ledger](../assessments/validation-ref-retention.md), plus this modest
process-policy change; it grants no unrelated ref, release or settings action.
Do not repeat approval requests for actions already covered by that scope.

Decision: append dated archival substitutions to the affected historical
plans, preserving their earlier text, published commits and counters. Keep
the branch/SHA/tag inventory and verified remote evidence in the ledger.
Required CI logs and artifacts need separate retention because archive tags
do not extend the workflow's fourteen-day artifact retention. Public prose
contains bounded receipts, not raw CI archives, logs or private host paths.

Decision: change only internal process guidance, plans, assessment and the
concise change record/index. Keep runtime, helpers, SDK, versions, workflows
and support claims unchanged; no changelog entry is required. Use existing
documentation/link/index and whitespace checks for the prose, followed by
the established immutable-candidate tester and independent-reviewer workflow.
The coordinator owns remote refs/settings and normal delivery handoff.

## 2026-11-20: Authorization for each cleanup occasion

Decision: cleanup authorization covers only the named refs and permitted
actions for that specific cleanup occasion. Later cleanups require new
maintainer authorization. The same already-authorized operations need no
repeat request. This clarifies the earlier scope statements without extending
their authorization to future cleanups.

Decision: keep the core authorization, active-work and immutable-tag rules in
AGENTS.md and move all detailed cleanup safeguards to the development guide.
Record the published public CI-evidence archive and its immutable identity in
the assessment, dating the protection/access observation and distinguishing
connector-serialized logs from original validation ZIP bytes. Keep raw evidence
outside main and leave workflow retention, runtime, tests and versions unchanged.

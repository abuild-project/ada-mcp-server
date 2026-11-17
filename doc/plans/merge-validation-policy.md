# Merge and validation history

Base revision: `180ecbcf8f279bf00e75a3f926ef2fb430670320`.

## 2026-11-17: Repository-visible workflow rules

Keep main-integration merges limited to conflict resolution and place
corrections in separate commits. Preserve each head's validation as a new
short PR comment, rather than replacing an earlier validation record.
Put both rules in the versioned AGENTS.md so they apply to all contributors.
Preserve existing published commits and comments.

This is a documentation-only policy change. The coordinator is the developer;
the assigned tester and independent reviewer check the immutable candidate,
documentation links/index order and source parity. No runtime, dependency,
CI configuration or changelog change belongs to this topic. Create its own
PR after the local workflow; merging it requires separate authorization.

## 2026-11-17: Clarify integration corrections

Explicitly include fixes needed for the combined state in the separate
following commit, even when the integration merge temporarily fails tests.
Require validation of the corrected combined head. Remove the older duplicate
validation-comment clause so the precise append-only rule is authoritative.
Validate this wording-only correction with the same tester/reviewer roles,
post a new short head-specific validation comment and perform the authorized
PR merge after successful checks. Preserve published history and comments.

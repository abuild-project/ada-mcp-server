# Routine update documentation

Base revision: `ffb7daff7003bc7280d4d934909f24b51997a85f`.

## 2026-11-17: Approved narrow plan exception

Allow only routine dependency patch updates and lock-only alignment to
approved input pins to omit a separate plan. Other changes retain dated
plans. Require a concise record with durable rationale; use it verbatim
as the PR description and post later head validation in a short comment.
Keep counters and attempt logs outside source. Preserve both word-count
guidelines and all tester, reviewer, CI and installed-version evidence
requirements. This policy change follows the existing plan requirement.
Use existing documentation checks with an explicit DEV snapshot; add no
tests, dependency, CI code, pin, runtime or changelog change.

## 2026-11-17: Superseding eligibility decision

The initial eligibility wording above is historical and superseded by the
[AGENTS rule](../../AGENTS.md#dependency-update-plans). The maintainer selected
update-level and dependency-role boundaries, with roles defined by direct
input-file pins. Required lock alignment inherits that eligibility. Keep
the normative categories only in AGENTS and link from development; retain
all record, CI, review and version-evidence duties.

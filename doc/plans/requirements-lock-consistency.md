# Requirements input and lock consistency

Base revision: `adf159ee9b2e206dad311d9aa1990f69d0324db4`.

## 2026-11-17: Approved narrow CI guard

Check development.in and its relative -r runtime.in include against the
exact versions in development.lock before lint/tests. Permit transitive
lock packages. Support the repository's exact-pin/include and generated
hash-line format; reject unknown relevant lines, missing/contradictory
pins and include cycles with clear diagnostics. Add no pip parser framework
or dependency, and keep pins, pyproject and runtime code unchanged.

Use a few owned-fixture tests for the original Ruff mismatch, agreement,
runtime inclusion, missing pins, format handling and early CI failure.
Tests do not require Git metadata. Preserve a separate historical-bot
counterexample as tester evidence rather than embedding history in CI.

Add only the authorized upstream signature-report links to the assessment
and support notes; preserve every existing acceptance restriction. Keep
AGENTS shortening work separate. This internal CI change has no changelog
entry. Only the assigned developer edits; focused checks precede immutable
canonical testing and independent review. Keep later head validation in PR
comments, and stop before merge or release.

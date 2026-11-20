# RC5 prerelease preparation

Prepare canonical `0.2.0-rc.5` and Python/MCP `0.2.0rc5` from accepted main
`e9760a8522065b26aca636677111c12d81777424` so the maintainer can test the
published Mac update path. The release notes cover changes since RC4:
unknown-tool rejection before ALS startup and accurate missing-handler errors,
the expanded locked-SDK validation test basis, and shared user-wide Codex
discovery/configuration and worktree guidance.

Move the corresponding Unreleased entries into RC5 and coordinate maintained
README, installation, update, support and release references. Preserve RC4's
historical Mac assessment, release notes and immutable published bytes. Only
the canonical version and documentation change; runtime behavior, dependencies,
workflows, SDK/ALS/GNAT pins, workflow contract 1 and the 19-tool catalog remain
unchanged.

The dated plan records authorized standalone-PR delivery and promotion from
the exact successful merged-main push CI, using reviewed source-bound notes
and tested artifacts without rebuilding. Actual public metadata and new pins
are required before acquisition; compatible selection-aware entries can retain
their version and previous runtime/binding rollback state.

Focused development checks of this release delta passed maintained links,
example syntax, sorted index, requirements and whitespace checks, plus existing
documentation, version, synthetic artifact and release-note contract tests and
Ruff checks. These host checks establish metadata/documentation consistency;
complete exact-head hosted Trixie CI and independent review remain required.
No RC5 Mac installation or update acceptance is claimed; the supplied Mac
evidence remains specific to RC4.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

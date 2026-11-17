# Automatic local image tags

Base revision: `a3f16279c08dffbe87c6f09ea77e88ed9d6df04b`.

## 2026-11-17: Versioned aliases after bootstrap

The maintainer requested an automatic local Docker tag for each installed
version. Bootstrap will retain its verified immutable image target and add
`ada-mcp-server:<project-version>` after Doctor succeeds, including warm-cache
and existing-binding runs. Map SemVer build metadata's `+` to `_` for Docker's
tag syntax. Reuse an existing alias only when it identifies that same target;
reject a different or unknown target without overwriting it. Verify the alias
after creation and retain command receipts and a concise result in the setup
report. Doctor, query, binding schemas and launcher pins remain unchanged.

Develop only in this independent repository. Published RC3 artifacts and the
installed acceptance runtime remain immutable. No GHCR publication or change
to source-selection defaults belongs to this change.

The coordinator also holds the developer role and is the sole candidate editor.
A separate tester and independent reviewer will assess the same immutable
patch against the base. The maintainer prohibits commits, pushes, publication
and compiler CI in this session. Therefore identify the candidate by base plus
patch SHA256 and file inventory in fresh detached test/review worktrees, and
run targeted host-tool tests, static checks and documentation checks. These
checks are local development evidence; the complete committed-source Trixie
chain remains a later acceptance requirement. Operational evidence and local
correction counters start at zero under ignored `build/`.

## 2026-11-17: Separate pull-request delivery

The maintainer authorized commits, the topic push and a pull request for this
completed tagging change after the local workflow, with the normal hosted
repository checks. Keep the GHCR-default/archive-fallback request in its own
topic rather than extending this patch. The native macOS RC3 acceptance remains
a separate private record; neither its published runtime nor its binding is
edited by this source change. Preserve the local test and independent-review
evidence and its zero correction counters when committing the checked source.

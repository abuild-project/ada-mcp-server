# RC2 prerelease preparation

RC1 has no release-notice hook, while the accepted public installation/update
workflow needs a coordinated published package. Prepare `0.2.0-rc.2` across
server, Python/MCP, image, tooling and skill metadata. Actual-runtime fixtures
derive their expectations from the canonical version; historical SemVer and
provenance examples remain explicit.

The first-install guide gives a concrete RC2 install/initial-upgrade prompt:
authenticate the actual published GitHub asset digest, final release manifest,
exact tag commit and new target pins before using the trusted acquirer. It
retains the verified immutable RC1 fallback and the existing consent, activation
and rollback workflow. The README stays focused on users. Full/light skill
catalog descriptions expose fresh release checks and approved updates.
Linux/AMD64 Docker remains the pilot target; Mac/native-client and separate
Cloud-account acceptance are not expanded.

Promotion reads bounded version-specific release notes from the approved Git
commit, validates them before publication and passes the reviewed bytes through
a temporary notes file outside the unchanged release asset set. Missing,
malformed, wrong-source or uncommitted notes cannot substitute for that blob.
The exact merged-main push CI artifacts still supply the tested bytes without
rebuilding. Versioned release notes and the changelog describe the RC2 changes;
publication is claimed only after actual access verification.

The update guide clarifies that a bounded worker timeout reports an offline or
unknown check without guaranteed recovery of partial output; persisted active
provider waits remain honored. This release does not change checker behavior.

Development validation passed 103 focused cases covering note provenance and
pre-publication failure, asset preservation, coordinated versions, generated
tooling/skill pins, image metadata, real MCP notice transport and build guards.
Missing/wrong-version note controls reject the original promotion entrypoint.
Ruff/format, strict Mypy, maintained links/examples and whitespace checks passed.
The installed-package isolated-import control remains part of the complete
container chain. These source-host controls do not replace exact-source AMD64
Trixie acceptance or post-publication consumer checks.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

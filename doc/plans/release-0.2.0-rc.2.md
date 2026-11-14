# RC2 release preparation

Base revision: `5cd4d016fc1e0401753d9a5a1e0bd393fdbc5bd5`.

## 2026-11-14: Coordinated pilot update

Prepare `0.2.0-rc.2` in a separate release package after the accepted public
installation/update feature. Keep the canonical SemVer coordinated across the
server, Python/MCP version, image, tooling and skill metadata. Derive fixtures
that inspect the actual server/build from that version; retain explicit
historical SemVer and provenance examples.

Keep the documented Linux/AMD64 Docker pilot contract. macOS, native clients
and another account's Cloud import need their own acceptance. Preserve the
published RC1 tag and bytes as a verified fallback; they have no notifier.
The initial upgrade uses actual published GitHub asset digests to authenticate
the final release manifest, exact tag commit and new tooling/plugin/image pins.
Reuse the trusted acquisition helper and the shared consent/activation workflow.
No future source hash or download is assumed to exist.

Use reviewed version-specific release notes from the approved immutable Git
source. Validate their bounded UTF-8 content, version heading and body before
publication; never substitute an uncommitted worktree file. Pass them through
a temporary notes file outside the unchanged tested asset set. Preserve the
existing source-bound approval, tag, public-access and no-rebuild gates.

Clarify the bounded checker contract: only completed worker metadata is used;
a timeout fails open without guaranteed partial-output recovery. Already
persisted provider deadlines continue to apply. No worker/cache architecture
change is part of this release preparation.

Validate meaningful note-source/malformed-content/asset-preservation controls,
version-sensitive packaging and protocol tests, style, typing and documentation.
Source-host checks are development evidence. Release acceptance requires the
full exact-source AMD64 Trixie chain and independent review, then promotion
from the exact resulting main push CI run after the reviewed release PR merges.
Public availability and consumer activation are checked after publication.

# Pydantic hash lock update

## 2026-11-13: Scope and decisions

Continue the existing dependency topic `dependabot/pip/main/pydantic-2.14.3`
from published revision `54edd4ebdbc5a0ba2dfcab62af5cec861a1e26a1`.
Integrate accepted main `7bff9e7f911af3a14d32de5f1f72fd6235ff2492` with an
ordinary merge, preserving published author information and history.
Temporary Codex preparation refs do not replace the existing topic or reset
its correction counters.

The only version changes are pydantic 2.13.4 to 2.14.3 and pydantic-core
2.46.4 to 2.50.4. Do not absorb an MCP 2 migration or unrelated transitive
upgrades.

Add the topic change record and sorted index entry. Keep this dependency
work separate from the frozen pilot release revision; it does not retag,
rebuild or replace that release's artifacts. No additional supported
platform, client or tool contract is introduced. No unrelated CI guard is
part of this update.

The preparation used uv 0.13.5 with CPython 3.13.5 for resolution targeting
Linux/AMD64. Existing output pins were preferred except for the requested
package; this is lock generation, not container/runtime acceptance.

```sh
uv pip compile requirements/development.in --generate-hashes \
  --python python3.13 --python-platform x86_64-unknown-linux-gnu \
  --no-python-downloads --only-binary=:all: \
  --upgrade-package pydantic --output-file requirements/development.lock
```

Regeneration downloads package metadata and hashes without installing
packages. The exact tool version, attempted commands, failed proxy attempt
if any and package/hash comparison evidence are retained outside tracked
source.

## Validation boundary

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388399084),
but its build log installed Pydantic 2.13.4. That result does not validate
the requested upgrade. Local preparation verifies input/lock agreement and
hash structure; the corrected merged revision requires complete Trixie CI
with the requested installed version, packaging, semantic and identity
checks and independent review.

Apply the existing bounded role workflow to the final immutable candidate.
Local preparation grants no remote push, review request, merge or
publication.

## 2026-11-13: Integrate the accepted Actions baseline

The maintainer selected the five accepted dependency updates for the first
pilot release. Integrate accepted main
`8d4e4e5ed88bf88bd55a0d9aa5d3096434b0d237`, containing the reviewed artifact
upload and checkout updates, into this existing Pydantic topic with an
ordinary merge. Preserve both published parent histories and authorship.

Retain Pydantic 2.14.3 and pydantic-core 2.50.4 from this topic. Preserve
every other package version and hash set, both accepted Actions pins and
the sorted union of indexed change records. The Python dependency ranges,
MCP 1.28.1 pin and documented support boundaries remain unchanged. Complete
Trixie CI and independent review must cover the new immutable revision;
earlier receipts identify only their original source revisions.

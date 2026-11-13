# Hatchling hash lock update

## 2026-11-13: Scope and decisions

Continue the existing dependency topic
`dependabot/pip/main/hatchling-1.33.0` from published revision
`462b5d3a09e7a8345f808f5d8d24a239351e1cab`. Integrate accepted main
`7bff9e7f911af3a14d32de5f1f72fd6235ff2492` with an ordinary merge,
preserving published author information and history. Temporary Codex
preparation refs do not replace the existing topic or reset its correction
counters.

The only dependency changes are hatchling 1.29.0 to 1.33.0 and new tomlkit
0.15.2. Check the backend's metadata 2.5 behavior through the actual build
and package-validation chain.

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
  --upgrade-package hatchling --output-file requirements/development.lock
```

Regeneration downloads package metadata and hashes without installing
packages. The exact tool version, attempted commands, failed proxy attempt
if any and package/hash comparison evidence are retained outside tracked
source.

## Validation boundary

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388432266),
but its build log installed Hatchling 1.29.0. Local preparation verifies
input/lock agreement and hash structure. The corrected merged revision
requires real wheel/sdist builds, Twine checks, coordinated
version/payload/provenance validation, complete Trixie checks and
independent review.

Apply the existing bounded role workflow to the final immutable candidate.
Local preparation grants no remote push, review request, merge or
publication.

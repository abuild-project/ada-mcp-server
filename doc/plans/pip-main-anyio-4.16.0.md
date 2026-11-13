# AnyIO hash lock update

## 2026-11-13: Scope and decisions

Continue the existing dependency topic `dependabot/pip/main/anyio-4.16.0`
from published revision `76533f44c416da19fdeacc0d0957fbbaf3f7c72f`.
Integrate accepted main `7bff9e7f911af3a14d32de5f1f72fd6235ff2492` with an
ordinary merge, preserving published author information and history.
Temporary Codex preparation refs do not replace the existing topic or reset
its correction counters.

The only version change is anyio 4.14.2 to 4.16.0. Cancellation, stream
close/checkpoint and cleanup behavior need the existing real lifecycle
acceptance rather than inference from the minor version.

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
  --upgrade-package anyio --output-file requirements/development.lock
```

Regeneration downloads package metadata and hashes without installing
packages. The exact tool version, attempted commands, failed proxy attempt
if any and package/hash comparison evidence are retained outside tracked
source.

## Validation boundary

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388448058),
but its build log installed AnyIO 4.14.2. Local preparation verifies
input/lock agreement and hash structure. The corrected merged revision
requires complete Trixie CI with the requested installed version, real
initialization/diagnostic controls, both numeric identities and
EOF/container cleanup, plus independent review.

Apply the existing bounded role workflow to the final immutable candidate.
Local preparation grants no remote push, review request, merge or
publication.

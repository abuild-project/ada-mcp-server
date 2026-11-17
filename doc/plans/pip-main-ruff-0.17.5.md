# Ruff hash lock update

## 2026-11-17: Scope and validation

Continue dependabot/pip/main/ruff-0.17.5 from published revision
`4cd14960f0dd58ef0ac9eed2c3300ba5ccd04e4f`, preserving bot authorship.
Merge accepted main `c29d8a3cf6d8a0fdd1b0ab05594e41195b157370` normally.
The input-only update still installs locked Ruff 0.17.4; align only that
lock entry with the requested 0.17.5. Preserve every other pin/hash set.

Use uv 0.13.6 with CPython 3.13.5 targeting Linux/AMD64:

```sh
uv pip compile requirements/development.in --generate-hashes \
  --python python3.13 --python-platform x86_64-unknown-linux-gnu \
  --no-python-downloads --only-binary=:all: --upgrade-package ruff \
  --output-file requirements/development.lock
```

Verify distribution hashes against the versioned release index and run
focused checks with the actual new Ruff. These are development evidence;
the final immutable candidate needs the complete canonical container chain
and independent review. Add the concise record/index, without a changelog
entry for this development-tool update. Keep the separate pytest-asyncio
topic, runtime pins, code and CI unchanged. No developer external writes,
merge or release; later head validation belongs in PR comments.

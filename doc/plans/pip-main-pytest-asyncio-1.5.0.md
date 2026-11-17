# pytest-asyncio hash lock update

## 2026-11-17: Scope and validation

Continue dependabot/pip/main/pytest-asyncio-1.5.0 from published revision
`64747b17d9433a0bbf4e44b12b0758537d55fde9`, preserving bot authorship.
Merge accepted main `c29d8a3cf6d8a0fdd1b0ab05594e41195b157370` normally.
The input-only update still installs locked pytest-asyncio 1.4.1.post1;
align only that lock entry with the requested 1.5.0. Preserve every other
pin/hash set.

Use uv 0.13.6 with CPython 3.13.5 targeting Linux/AMD64:

```sh
uv pip compile requirements/development.in --generate-hashes \
  --python python3.13 --python-platform x86_64-unknown-linux-gnu \
  --no-python-downloads --only-binary=:all: --upgrade-package pytest-asyncio \
  --output-file requirements/development.lock
```

Verify distribution hashes against the versioned release index and run
focused async tests with the actual new plugin. These are development
evidence; the final immutable candidate needs the complete canonical
container chain and independent review. Add the concise record/index,
without a changelog entry for this development-tool update. Keep the
separate Ruff topic, runtime pins, code and CI unchanged. No developer
external writes, merge or release; later head validation belongs in PR
comments.

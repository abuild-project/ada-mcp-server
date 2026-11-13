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

## 2026-11-13: Canonical Python metadata with the newer backend

The actual Hatchling 1.33.0 build used normalized Python distribution
filenames but preserved the provider's raw SemVer spelling in wheel and
sdist core metadata. The unchanged completed-check receipt rejected that
metadata, as required by the existing Python-version contract. Passing
unit tests and Twine alone do not establish receipt acceptance.

Decision: use Hatchling's documented builtin code version source on the
dependency-free src/ada_mcp/_version.py. Evaluate
`VERSION.replace("-rc.", "rc")` before the backend preserves the supplied
spelling. Retain the single canonical SemVer literal, existing Python/MCP
version and strict package-name/version/provenance checks. Do not introduce
another version constant, an external plugin or broader accepted metadata.

The backend's [code version source](https://github.com/pypa/hatch/blob/hatchling-v1.33.0/docs/plugins/version-source/code.md)
supports this path/expression configuration directly. Its
[history](https://github.com/pypa/hatch/blob/hatchling-v1.33.0/docs/history/hatchling.md)
records preservation of the original core-metadata version spelling starting
with 1.32.3; normalized filenames alone therefore cannot prove the contract.

The original actual wheel/sdist pair is a negative control for the unchanged
receipt helper. A private build-tool environment can inspect newly built
metadata during development; that is not a substitute for the complete new
exact-source AMD64 Trixie chain, successful receipt and generated-artifact
host acceptance. Preserve the original failed evidence and published commits.

## 2026-11-13: Integrate the accepted Pydantic baseline

The maintainer selected the accepted dependency updates for the first pilot
release. Integrate accepted main
`80ab1285b4d8695567d00a05e120b76d66177e1a` into this existing Hatchling topic
with an ordinary merge, preserving both published parent histories. Retain
the accepted Actions pins, Pydantic 2.14.3 and pydantic-core 2.50.4 from main,
alongside this topic's Hatchling 1.33.0 and tomlkit 0.15.2.

Preserve all other package versions and hash sets, the sorted union of change
records and the builtin Python-version provider. The canonical SemVer source,
normalized Python metadata contract, MCP 1.28.1 pin and strict receipt checks
remain unchanged. The combined source must receive its own complete Trixie
CI, successful provenance receipt, generated-artifact host acceptance and
independent review before acceptance. Earlier evidence remains tied to its
original immutable source revision.

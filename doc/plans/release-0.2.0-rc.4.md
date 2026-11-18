# RC4 release and subsequent local acceptance

Base revision: `f69fbba0eb68e004896d75097befd931b8d19950`.

## 2026-11-18: Release preparation and acceptance order

The maintainer chose to publish RC4 before testing a clean local Mac Codex
installation against Arca. Prepare a separate reviewed release package with
canonical SemVer `0.2.0-rc.4` and Python/MCP `0.2.0rc4`. MCP SDK 2 work starts
only after that local acceptance test. This decision supersedes the mandatory
before-release larger-project Mac timing gate in the imported-view topic;
the [assessment](../assessments/project-selection-timing.md) retains an optional
later performance procedure. Prior dated decisions remain historical records.

Move current Unreleased user changes into RC4, retain RC1–RC3 history and
immutable fixture/published fallback pins, and add version-specific reviewed
release notes. Update active release/setup/install/update/support guidance
without claiming future downloads, digests or client acceptance. Preserve
MCP 1.30.0, pinned ALS/GNAT, workflow contract 1 and the actual 19-tool catalog.
This package adds no runtime feature, installer behavior, global timeout change
or SDK update. Keep the fixed public RC2-to-RC3 consumer workflow unchanged.

Describe the existing project contract accurately: strict optional Boolean
`refresh` defaults to false; a repeated exact GPR/context reads the live view
without reload/readiness reset; true refreshes a reused client, while a new
exact client is already fresh. Project metadata completeness is independent
of the `indexing_complete` snapshot. The former 25-second project-selection
index wait is removed; the 30-second ALS RPC timeout and 25-second guarded
semantic wait remain. The same three pinned-ALS positional signature cases
remain unaccepted. Native Mac/Codex/Claude/OpenCode fresh installation and
lifecycle remain in development until direct consumer evidence exists.

The coordinator retains developer, tester and independent-reviewer roles for
this separate package. Use the new package's local correction counter, then
its separate PR counter, each starting at zero and bounded at three. Preserve
the preceding topic's closed counters and evidence. Keep operational receipts
outside tracked source. The developer makes modest metadata/docs checks and
freezes a coherent commit; the tester and independent reviewer assess that
immutable candidate. Full AMD64 Trixie CI, coverage, packages, native probes
and UID 1000/501 acceptance run on the exact committed hosted head. Do not
build/download the large image in the disk-constrained Cloud workspace.

After the reviewed release PR is merged with a merge commit, select the exact
successful `main` push run of `.github/workflows/ci.yml`. Use the existing
`promote.yml` and `scripts/promote.py` plan/publication gates, source-bound
notes and tested artifacts without rebuilding. Record actual tag/source,
asset hashes and anonymous registry identity/access before claiming public
availability. Only the coordinator performs external delivery actions.

## Planned post-publication local Mac test

Do not perform local cleanup or install configuration as part of release prep.
For the later test, inventory and back up the maintainer's own Ada plugin,
skill, MCP registrations, runtimes, bindings and selection locators. Remove
those installed entries and active state so they cannot supply the old build
project's MCP; preserve unrelated configuration and rollback copies outside
discovery. Check the effective user, project and ancestor discovery/configuration
scopes rather than assuming a new chat is clean.

Use a fresh Arca checkout as a sibling of the abuild checkout, never
inside it. Start a new **local Mac Codex** chat opened only on Arca. Acquire
the actually published RC4 through its ordinary verified installation route.
Require native agent tool discovery, actual server version/pins, the real Arca
GPR/scenarios, source-bound native queries compared with that checkout, and
disconnect/EOF cleanup. A standalone test-client batch alone is insufficient.
Retain actual commands, protocol/results, host/client versions and failures;
make no support promise before inspecting this consumer evidence. SDK 2 and
any broader client or performance work are subsequent separate topics.

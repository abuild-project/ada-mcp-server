# Permission-test identity preconditions

Base revision: `7b739b9b39db281388b5edaae277091d19cb562f`.

## 2026-11-16: Scoped local root skips and mandatory nonroot proof

Decision: keep the six mode-000 permission-denial cases and every existing
assertion and cleanup in tests/host/test_additional_inspection.py. A
module-local fixture skips those cases before fixture modification during
local root runs. With ADA_MCP_REQUIRE_PERMISSION_TESTS=1, root fails setup
instead. Nonroot runs retain the real filesystem denials. docker/check
supplies the flag explicitly and keeps its existing UID/GID rejection.

Decision: add four small policy cases for root/nonroot and optional/required
execution, replacing only the inspection module's private OS namespace.
Adapt the existing Docker-sentinel test with an owned id stub only for its
mocked successful path. Preserve early existing-output rejections, check the
required flag reaches docker run, and reject a fresh UID-0 attempt before
Docker use or output creation. Do not mock real denial or native identities.

Decision: measure collection and run the actual root default/required pytest
paths, real nonroot denial cases and complete AMD64 Trixie/GNAT 14/pinned-ALS
chain. Preserve the three blocked native cases, source guards, both artifact
UID checks and cleanup. Immutable fresh-worktree test and independent review
remain required before PR submission; source preparation alone is no proof.

Decision: only the developer edits the candidate. Keep product, tooling,
native controls, fixtures, pins, version and support unchanged. Update the
contributor guide and concise record/index, without a changelog entry.
Start this distinct package at local 0/3 and later PR 0/3; stop at the
checked PR before merge or release.

## 2026-11-16: Explicit identities in mocked launcher paths

Decision: give the existing Docker-stub launcher success and advisory paths
explicit --uid 1000 --gid 1000 arguments. A real root suite exposed that
those paths inherited UID 0 and stopped at the launcher's correct identity
guard before reaching their intended assertions. This changes only four
test invocation sites in test_launcher_roots.py, test_update_bytecode.py
and test_verified_helpers.py. Preserve the production launcher, real
permission denials, native identities and explicit rejection checks.

Decision: repeat the actual root default, mandatory and wrongly-skipping
helper controls and the complete immutable-candidate container chain.
Retain the earlier candidate and its evidence, including the unsuccessful
root run; a successful nonroot chain does not establish root ergonomics.

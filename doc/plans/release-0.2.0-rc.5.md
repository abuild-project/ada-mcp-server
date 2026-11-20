# RC5 release and subsequent Mac update check

Base revision: `e9760a8522065b26aca636677111c12d81777424`.

## 2026-11-20: Authorized release preparation and promotion

The maintainer requested merging the unknown-tool fix and publishing a new RC
to test the Mac update path. Prepare a standalone release PR for canonical
SemVer `0.2.0-rc.5` and Python/MCP `0.2.0rc5`. Include the accepted changes since
RC4: unknown-tool rejection before ALS startup and accurate missing-handler
errors, the expanded locked-SDK input-validation test basis, and user-wide
Codex discovery/configuration and worktree guidance. Update maintained install,
update, support and release references without changing runtime behavior beyond
the canonical version, dependencies, workflows or support scope. Retain RC4's
published bytes, historical notes and Mac acceptance assessment unchanged.

The coordinator has assigned developer, tester and independent reviewer. Only
the developer edits the candidate; leaf roles do not delegate. Local and PR
correction counters each start at zero and are separately bounded at three.
Keep operational counters and receipts outside tracked source. Freeze a
coherent unpublished commit after focused version/documentation/style checks;
the tester and independent reviewer assess that immutable candidate. Complete
AMD64 Trixie CI, packages and native probes run on the exact hosted head. Do
not build or import an image locally. Bounded CI-archive downloads and streaming
hash inspection are permitted as storage allows; retain the primary evidence.

The requested release authorizes the coordinator to submit the release PR,
merge it with a merge commit, create the immutable RC5 tag, and publish the
tested GitHub Release and public GHCR image through the existing gates. Select
the successful `main` push run of `.github/workflows/ci.yml` at the exact merged
source; topic or PR runs are insufficient. Use `promote.yml` and
`scripts/promote.py` with the reviewed source-bound notes, first in plan mode,
then promote those tested artifacts without rebuilding. Verify tag/source,
asset hashes, public package visibility and anonymous digest-pinned image
identity/access before claiming availability. Only the coordinator performs
external delivery actions.

After publication, the maintainer can test the real Mac update path from the
existing installation with verified target metadata, explicit approval and
retained rollback state. This package supplies no new Mac/update acceptance
evidence. RC4's bounded Mac evidence remains specific to RC4; SDK migration,
broader clients and expanded support remain separate work.

# Release procedure

Use this procedure for a maintainer-authorized release. Prepare release changes
in their own reviewed PR, then promote artifacts from the accepted `main`
revision. Merge, tags, publication, repository settings and account-plugin
updates need the maintainer's authorization; a reviewed PR alone is not that
authorization. Ordinary CI only builds/tests and uploads CI artifacts.
The promotion workflow is manually invoked for the approved release.

The initial version `0.2.0-rc.1` is a pilot prerelease, not a stable support
promise. Its [release notes](releases/0.2.0-rc.1.md) describe what it contains
and which client/platform tests still follow. The
[public repository assessment](assessments/public-release.md) distinguishes
observed settings from policy and unavailable administrative evidence.

## Artifact trust and version

The canonical SemVer is read from src/ada_mcp/_version.py. Python converts
`0.2.0-rc.1` to `0.2.0rc1`; package metadata and MCP initialization report that
project version, not the MCP SDK version. The SDK stays pinned by the lock.
Tooling/skill/container/source metadata uses the coordinated SemVer.

CI builds the source image once, runs the full check chain and packages that
exact immutable Docker target and source commit. It saves that target once,
derives the canonical config digest from the archived bytes and hashes all
artifacts. A verified descriptor proof binds an OCI index/manifest target to
exactly one AMD64 runtime config; classic config targets remain distinct from
OCI target IDs. The full tooling runtime manifest pins the image/archive and the
lightweight skill pins the full tooling and runtime manifest. Image IDs and
future registry digests are generated artifact metadata, not edited back into
source after a build. No latest tag or mutable branch is a trust identifier.

Python wheel/sdist bytes come from the completed check's source/hash receipt.
Receipt version 2 also pins the exact native image target actually checked.
The selected packaging target must match before export, even at the same
source/version, and promotion retains this tested-target relationship alongside
the authenticated canonical config/OCI identity proof.
Same-version files without matching committed-source provenance are refused;
promotion retains those checked bytes and their receipt rather than rebuilding
replacement Python distributions.

Before publication, release-manifest.json truthfully has registry_digest=null.
The later promotion loads the checked image archive, tags/pushes those bytes,
records the actual pushed registry digest and verifies config-image identity
after an anonymous digest-pinned pull and local-target export. It does
not rebuild a replacement image or repackage different tooling. Final promoted
metadata and checksums record the digest and exact tested artifact hashes.

## Manual gates

1. Merge the release PR with a merge commit and wait for the complete CI chain
   on that exact resulting `main` revision. The promotion workflow requires a
   successful `push` run on `main` from this repository's
   `.github/workflows/ci.yml`, with the selected source SHA. A PR or topic-push
   run does not meet this requirement, even if its tree is identical.
   Download that run's `release-candidate` artifact, verify its hashes and
   source/image/version correspondence, and run scripts/promote.py in plan
   mode. Retain the source SHA, run ID, command and output.
2. With merge/release authority supplied, create the intended immutable tag
   `v0.2.0-rc.1` on that same approved revision and verify the tag target.
   Verify repository/GitHub Actions permissions, release protection,
   GHCR publication rights and the exact redistributed components' required
   source delivery under [licensing](licensing.md). A declared environment name
   alone is not evidence
   of a working approval rule; verify the actual settings/access. The manual
   workflow takes the verified `run_id` and `source_sha`; keep
   `execute_publication` false for its plan-only invocation.
3. Promote the selected tested artifacts to GitHub Releases/GHCR. Do not rebuild.
   Retain the actual pushed registry digest and compare the config image ID
   with the tested image ID. If administration is blocked, report the exact
   setting and permission failure instead of assuming success.
4. GHCR packages initially can be private even for a public repository. Explicitly
   set/verify public package visibility. Then perform a separate anonymous
   digest-pinned pull with a new empty client config and verify its actual
   target-to-config relationship. An authenticated pull is not public-access
   evidence. The prepared code requires this check before creating a release;
   actual registry transport and publication are still unvalidated.
5. Check that the actual public versioned file URLs return the pinned bytes.
   Only then claim public availability, update the existing account plugin
   with separate authorization and test a fresh managed Cloud task using
   ordinary artifact acquisition. This follows release publication; a local
   CLI, temporary app-server or owner-only Plugin Creator download is not proof.

No PyPI publication, new account-plugin identity or public plugin-directory
submission is part of this workflow. The repository remains an independent
continuation, not an upstream mirror requiring automatic synchronization.

The pilot acceptance after publication checks the actual versioned download
URLs and pinned hashes, anonymous GHCR pull/config identity, the existing
account plugin's published-artifact references, and ordinary acquisition in a
fresh managed Cloud task. Keep source-bound semantic queries, explicit GPR
views and EOF cleanup in that test. A second worktree or cleared local binding
in the producer task is not a fresh Cloud environment. Actual macOS and native
Claude/OpenCode acceptance remain separate subsequent topics; they do not
block the agreed Cloud pilot prerelease.

Registry behavior reference:
https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

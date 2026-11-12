# Prepared release promotion

The current task stops at a fully checked PR. Do not merge, tag, publish a
GitHub release, push a GHCR image or update the account plugin without later
maintainer approval. Ordinary CI only builds/tests and uploads CI artifacts.
The prepared promotion workflow is manually invoked after that decision.

## Artifact trust and version

The canonical SemVer is read from src/ada_mcp/_version.py. Python converts
`0.2.0-rc.1` to `0.2.0rc1`; package metadata and MCP initialization report that
project version, not the MCP SDK version. The SDK stays pinned by the lock.
Tooling/skill/container/source metadata uses the coordinated SemVer.

CI builds the source image once, runs the full check chain and packages that
exact image ID and source commit. It saves the image once and hashes all
artifacts. The full tooling runtime manifest pins the image/archive and the
lightweight skill pins the full tooling and runtime manifest. Image IDs and
future registry digests are generated artifact metadata, not edited back into
source after a build. No latest tag or mutable branch is a trust identifier.

Before publication, release-manifest.json truthfully has registry_digest=null.
The later promotion loads the checked image archive, tags/pushes those bytes,
records the actual registry digest and verifies config-image identity. It does
not rebuild a replacement image or repackage different tooling. Final promoted
metadata and checksums record the digest and exact tested artifact hashes.

## Manual gates

1. Select a successful CI run for the approved immutable source revision.
   Verify its artifact hashes and source/image/version correspondence. Run the
   promotion validator in plan mode; retain its full command and output.
2. Approve merge/release separately, create the intended immutable tag at the
   approved revision and configure repository/GitHub Actions permissions and
   release protection. A declared environment name alone is not evidence of
   a working approval rule; verify the actual settings/access.
3. Promote the selected tested artifacts to GitHub Releases/GHCR. Do not rebuild.
   Retain the actual pushed registry digest and compare the config image ID
   with the tested image ID. If administration is blocked, report the exact
   setting and permission failure instead of assuming success.
4. GHCR packages initially can be private even for a public repository. Explicitly
   set/verify public package visibility. Then perform a separate anonymous
   registry-manifest/pull check with no account credentials and verify its
   digest/image ID. An authenticated pull is not public-access evidence.
5. Check that the actual public versioned file URLs return the pinned bytes.
   Only then claim public availability, update the existing account plugin
   with separate authorization and test a fresh managed Cloud task using
   ordinary artifact acquisition. This follows release publication; a local
   CLI, temporary app-server or owner-only Plugin Creator download is not proof.

No PyPI publication, new account-plugin identity or public plugin-directory
submission is part of this workflow. The repository remains an independent
continuation, not an upstream mirror requiring automatic synchronization.

Registry behavior reference:
https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

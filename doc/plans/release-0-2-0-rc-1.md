# Pilot release 0.2.0-rc.1

Base revision: `5253b21204c8da18031f417d0f35ef6732d1e7c5`.

## 2026-11-13: Scope and maintainer decisions

The bootstrap distribution was accepted by merge commit
`5253b21204c8da18031f417d0f35ef6732d1e7c5`. Prepare publication in a separate
release topic rather than adding release edits to the completed bootstrap PR.
The maintainer authorized the ordered release package: merge bootstrap, prepare
and review the release PR, merge it, publish `v0.2.0-rc.1` from its successful
exact-main CI artifacts, and resume the public acquisition and fresh Cloud
tests that require a published version.

Decision: retain coordinated SemVer `0.2.0-rc.1` and Python `0.2.0rc1`; publish
as a pilot prerelease. Keep the standalone AMD64 Trixie support contract and
all explicit tool/platform limits. Actual Mac and native Claude/OpenCode
acceptance remain subsequent topics, not gates for this pilot prerelease.

Decision: use merge commits for every PR in this repository, including release
and dependency topics. Disable squash/rebase merges in the repository settings.
Retain reviewed commits and author information. Fold only unpublished
corrections before initial submission; do not rewrite shared history.

Decision: review actual public-repository and release settings, comparing
Arca and Spawn Manager. Distinguish repository policy from effective remote
configuration and report inaccessible settings as evidence gaps. A public
repository does not prove public GHCR package visibility or publication rights.
No settings changes to the comparison repositories are part of this topic.

Decision: keep README, changelog, setup and support guidance valid before and
after publication by linking the release index and describing prerelease scope.
Do not replace a truthful pre-publication statement with an unverified claim
that a particular artifact or client deployment is already available.

## 2026-11-13: Release sequence

1. Prepare release notes, the release record, merge policy and repository
   assessment. Validate the immutable candidate through the documented role
   workflow and inspect hosted CI/Copilot at the actual PR head.
2. Merge the release PR with a merge commit. Require successful complete CI
   for that resulting `main` commit, retaining its run ID and artifact hashes.
3. Tag that same commit as `v0.2.0-rc.1`. Validate the promotion plan and reuse
   exactly that CI run's tested image and Python/tooling artifacts, without
   rebuilding a replacement for publication.
4. Verify effective release permissions/protection and public GHCR visibility.
   Publish the existing artifacts with actual registry digest and require
   anonymous digest-pinned pull/config identity before creating the release.
5. Verify actual public download URLs and hashes, update the existing account
   plugin to those published references, and test ordinary acquisition in a
   genuinely fresh managed Cloud task. Keep its evidence distinct from the
   producer environment's warm-cache or cross-store checks.

The release procedure and repository assessment retain the exact prerequisites
and any administrative blockers. Operational correction counters and transient
delivery status stay outside tracked source. Published artifacts and tags are
immutable; corrections require another version instead of replacement.

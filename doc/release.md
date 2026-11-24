# Release procedure

Use this procedure for a maintainer-authorized release. Prepare release changes
in their own reviewed PR, then promote artifacts from the accepted `main`
revision. Merge, tags, publication, repository settings and account-plugin
updates need the maintainer's authorization; a reviewed PR alone is not that
authorization. Ordinary CI only builds/tests and uploads CI artifacts.
The promotion workflow is manually invoked for the approved release.

The coordinated `0.2.0` target is the first stable release with bounded
client support. Its [release notes](releases/0.2.0.md) describe the changes,
source-delivery directions and client/platform limits. Publication remains
conditional on the exact gates below. Older published releases remain immutable
fallbacks. The [dated stable plan](plans/release-0.2.0.md) records this delivery.
The [public repository assessment](assessments/public-release.md) distinguishes
observed settings from policy and unavailable administrative evidence.

## Artifact trust and version

The canonical SemVer is read from src/ada_mcp/_version.py. Stable `0.2.0`
remains `0.2.0` in Python and MCP metadata. Prereleases convert, for example,
`0.2.0-rc.6` to `0.2.0rc6`. Metadata reports the project version, separately
from the MCP SDK version. The SDK stays pinned by the lock.
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
   mode. The plan and execution both require bounded UTF-8 notes from
   `doc/releases/<version>.md` in that approved Git commit, with its exact version
   heading and a nonempty body. Missing/malformed notes stop before publication;
   uncommitted worktree notes cannot replace them. Retain the source SHA, run ID,
   notes hash, command and output. Publication passes those reviewed bytes via
   a temporary notes file outside the release assets; it adds no artifact.
2. With merge/release authority supplied, create the intended immutable tag
   `v0.2.0` on that same approved revision and verify the tag target.
   Verify repository/GitHub Actions permissions, release protection,
   GHCR publication rights and the exact redistributed components' required
   source delivery under [licensing](licensing.md). A declared environment name
   alone is not evidence
   of a working approval rule; verify the actual settings/access. The manual
   workflow takes the verified `run_id` and `source_sha`; keep
   `execute_publication` false for its plan-only invocation.
3. Promote the selected tested artifacts to GitHub Releases/GHCR. Do not rebuild.
   Supported `-rc.N` tags use `--prerelease`. Stable tags use `--latest`, matching
   the release updater's stable/prerelease metadata contract.
   Retain the actual pushed registry digest and compare the config image ID
   with the tested image ID. If administration is blocked, report the exact
   setting and permission failure instead of assuming success.
4. GHCR packages initially can be private even for a public repository. Explicitly
   set/verify public package visibility. Then perform a separate anonymous
   digest-pinned pull with a new empty client config and verify its actual
   target-to-config relationship. An authenticated pull is not public-access
   evidence. The prepared code requires this check before creating a release;
   a previous release does not prove access for the selected new version.
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

For RC4, the maintainer chose publication before a separate clean **local**
Mac Codex/Arca installation test. Follow the
[dated release plan](plans/release-0.2.0-rc.4.md) for owned-state backup/removal,
an isolated sibling checkout and actual native agent discovery/source queries.
A test-client batch alone does not establish that acceptance. The previous
mandatory larger-project Mac benchmark is superseded by this order; its
[measurement procedure](assessments/project-selection-timing.md) is optional
later performance work. MCP SDK 2 work follows the local acceptance test.

For RC5, the maintainer authorized publication to enable a subsequent Mac
update-path test. Follow the [RC5 plan](plans/release-0.2.0-rc.5.md); retain
RC4's historical Mac assessment without treating it as RC5 acceptance.

For RC6, follow the [RC6 plan](plans/release-0.2.0-rc.6.md) for publication
and the subsequent update, installation and verification of the existing
private Managed Cloud plugin. The [RC6 consumer assessment](assessments/rc6-consumer.md)
retains the subsequent supplied checks and their limits.

Registry behavior reference:
https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry


## Public RC2 notification of RC3

After RC3 is actually published and its public assets/anonymous registry identity
are verified, dispatch the reviewed manual workflow with the exact approved
RC3 tag/source commit. Replace the placeholder; neither source preparation nor
a synthetic release fixture establishes this consumer acceptance:

```sh
gh workflow run public-notice-acceptance.yml --ref v0.2.0-rc.3 \
  -f expected_source=APPROVED_RC3_MAIN_SOURCE_SHA
```

The contents-read-only job authenticates actual public RC2/RC3 GitHub asset
digests, final manifests and tag/source correspondence. On an ephemeral hosted
AMD64 Docker runner, it acquires immutable public RC2 tooling through the trusted
legacy acquirer and pulls its public image by registry digest using a new empty
Docker client configuration. It uses pinned public Arca source, real arca.gpr
and ARCA_BUILD_MODE=validation for Bootstrap/Doctor/project queries.

Required evidence is actual MCP server `0.2.0rc2`, RC3 notice in initialization
instructions AND the complete selected project's update_notice, then a performed
manual fresh check within the same daily cache. An off query must suppress the
notice and create no update cache. Exact named-container EOF cleanup, raw
protocol/JSON/argv/streams and small provider/cache evidence are retained even
on failure. Image/runtime/source caches are excluded from the uploaded artifact.
The new script is included in the ordinary strict type/unit/style checks; the
manual public consumer run is not a replacement for full source CI.

A timeout, provider deadline or feed propagation delay is a real failed/pending
consumer result. There are no automatic retries or cache/header bypasses. Inspect
the retained actual provider deadlines and wait before a later approved retry.
Do not publish an acceptance claim from a mocked fixture or successful download.
This exercises the public protocol/query-client route, without installing RC3,
changing a private account plugin or proving fresh managed Cloud/native/Mac use.

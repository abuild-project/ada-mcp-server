# RC6 release and Managed Cloud update

Base revision: `8cc6a8a87ce23894aae48a83386c623c953a3aba`.

## 2026-11-20: Prepare and publish RC6

The maintainer authorized publication of pilot prerelease `0.2.0-rc.6`
(Python/MCP `0.2.0rc6`) from accepted main, followed by an update and
installation of the existing private Managed Cloud plugin. RC6 packages the
host Python and update-policy fixes, the full interpreter probe budget and
the separate Mac/Codex and Managed Cloud setup guidance. Move the Unreleased
entry into RC6, add reviewed release notes and update maintained guidance so
RC6 acquisition depends on actual publication and authenticated pins. Keep
the published RC5 PATH workaround, its trusted source acquirer and historical
release notes and assessments available. The tool catalog, workflow contract
1, locked MCP SDK 1.30.0 and ALS/GNAT pins carry forward. The unpublished ALS
2027.1 release is outside this delivery.

The developer prepares one coherent commit and runs focused version and
documentation checks. The tester and independent reviewer assess its exact
immutable revision. Start local and PR correction counters at zero for this
release topic. Use complete hosted AMD64 Trixie validation and retain
evidence outside source. The coordinator submits the checked release PR,
merges with a merge commit and verifies the complete `main` push CI for that
exact source. Use the existing promotion workflow first in plan mode with
source-bound notes, then publish the tested artifacts without rebuilding.
Verify the tag and source, authoritative public asset hashes and anonymous
digest-pinned GHCR identity before claiming publication.

After publication, update the existing private plugin with the authentic RC6
entry and runtime pins. Verify installation and activation in the intended
account, and use a fresh Managed Cloud task for actual entry discovery,
published-runtime acquisition or verified retained selection, Docker-backed
source queries and cleanup. Record evidence and limits for each step. The
actual Mac/Codex source and published consumer tests remain pending; release
and Cloud evidence do not establish Mac acceptance.

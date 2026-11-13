# Pilot prerelease preparation

The bootstrap distribution provides the tested server, container and host
tooling, but its maintained documentation describes only an unpublished
development candidate. Prepare `0.2.0-rc.1` as the first pilot prerelease of
the independent abuild-project continuation, without changing server behavior
or implying support for untested clients.

The README, changelog, setup and support guidance describe the coordinated
prerelease and refer to GitHub Releases for actual published versions. Versioned
release notes retain the AMD64 Trixie contract, explicit tool limits and
deferred Mac/native-client acceptance. Prepared artifact URLs and successful
source checks are kept distinct from verified public availability.

Release guidance requires the exact merged `main` revision's successful push
CI run and promotion of those tested artifacts without rebuilding. The same
source revision identifies the release tag and artifact provenance. Public
file access, anonymous registry identity and fresh managed Cloud acquisition
remain directly observed consumer gates rather than inferred compatibility.

Every PR uses a merge commit, preserving the reviewed commits and authorship.
Squash/rebase merges are excluded by policy; unpublished corrections are still
combined before initial submission. The repository assessment compares actual
public/release settings with Arca and Spawn Manager and separates observed
configuration from unavailable administrative evidence.

Development validation checked maintained local links, JSON/Bash examples and
coordinated version references with scripts/check_docs.py. The proposed
branch-protection JSON parses and selects the actual `standalone` check while
allowing merge commits. Whitespace checks passed. These documentation checks
do not replace the complete exact-revision AMD64 Trixie acceptance required
for release artifacts.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

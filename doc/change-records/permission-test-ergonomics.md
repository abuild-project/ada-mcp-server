# Permission-test identity preconditions

Local root pytest runs previously failed the six inspection regressions that
deliberately require a real nonroot identity. They now skip those cases
explicitly before the owned permission fixtures are modified. The existing
denial assertions, strict-runner failure evidence and cleanup remain intact.

Mandatory checks retain a stronger boundary: docker/check supplies
ADA_MCP_REQUIRE_PERMISSION_TESTS=1 and keeps its actual UID/GID guard.
Under that flag a root pytest invocation fails setup instead of skipping.
Nonroot runs execute the original filesystem-denial checks. Four small
policy cases cover root/nonroot and optional/required execution without
changing the process-wide identity.

The existing Docker-sentinel test uses an owned identity stub for its mocked
successful CLI path, checks that the mandatory flag reaches Docker, and
rejects a fresh UID-0 attempt before Docker use or output creation. Early
existing-output rejection and retained evidence assertions stay intact.
This mock is not a real identity or native acceptance result.

Four existing Docker-stub launcher invocation sites also pass explicit
nonroot runtime IDs. Their success and advisory assertions now reach the
intended mocked Docker calls when pytest runs as root. The production
launcher's identity rejection remains intact.

At implementation revision `09eb894ee6e6075b7e84de44b8a435ac8eeceac9`,
a fresh detached worktree and its exact-source AMD64 Trixie/GNAT 14/pinned-ALS
image established the actual root paths. Collection found 1,285 cases,
with one integration case deselected. The default run passed 1,278 cases
and skipped exactly the six permission cases. Mandatory mode produced
exactly six setup errors and no skips; the other selected cases passed.
A targeted fail-to-skip helper mutation made its policy counterexample
fail, with no skip. Actual UID 1000 passed all six mandatory denial cases.
Actual UID 0 was rejected by docker/check before Docker use or output
creation. These are real process identities inside rootless Docker, with
capabilities dropped; container UID 0 maps to host UID 2000. They establish
the container pytest paths, not host-root or macOS acceptance.

The complete nonroot container chain at
`b1f40a7ad1e1b6dc7012133018f50627ba71a992` passed unit, quality, coverage,
packaging, documentation and actual ALS/MCP controls. Its
[hosted validation ZIP](https://github.com/abuild-project/ada-mcp-server/actions/runs/43944041974/artifacts/14264082210)
was independently checked beyond job logs: committed source and
distribution hashes/payloads, OCI image binding, native/raw reading,
additional and diagnostic results, source guards, and generated-artifact
queries with real Linux identities 1000:1000 and 501:20 and cleanup.
The [dated plan](../plans/permission-test-ergonomics.md) records the
bounded decisions and immutable evidence revisions.

Product behavior, tooling, native controls, fixtures, dependencies, version
and support scope are unchanged. The three existing positional signature
cases remain blocked and unaccepted. This internal test adjustment adds no
user-facing changelog entry.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

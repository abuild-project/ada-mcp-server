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

Validation is pending for this candidate based on
`7b739b9b39db281388b5edaae277091d19cb562f`. The
[dated plan](../plans/permission-test-ergonomics.md) requires measured
collection, actual root default/required pytest flows, real nonroot denials
and the complete managed AMD64 Trixie chain before acceptance.

Product behavior, tooling, native controls, fixtures, dependencies, version
and support scope are unchanged. The three existing positional signature
cases remain blocked and unaccepted. This internal test adjustment adds no
user-facing changelog entry.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

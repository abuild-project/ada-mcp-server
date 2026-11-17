# Automatic local image tags

Images imported from a release archive could appear only by digest in Docker,
requiring a manual tag for every installed version. Successful bootstrap now
assigns `ada-mcp-server:<project-version>` after Doctor, including warm-cache
installs and restoration through an existing binding. Docker-compatible tags
replace `+` in SemVer build metadata with `_`.

The alias is verified against the selected immutable target and recorded in
the setup report. Repeated setup reuses the same alias; an existing different
target or unknown Docker state fails without deliberately overwriting it.
The check and Docker's tag operation are separate daemon calls, so concurrent
external retagging is outside this check's atomicity guarantee. Bindings and
launchers keep their digest pins. Doctor and queries remain read-only.

All 1,017 host tests pass with the locked development dependencies. Ruff,
formatting, strict Mypy, requirements and documentation checks pass. The new
bootstrap controls reject the original missing-alias behavior. A separate
tester and independent reviewer checked the same source candidate against
base `a3f16279c08dffbe87c6f09ea77e88ed9d6df04b`. Actual macOS Docker calls
through the source helper create then reuse the RC3 alias; they establish
source-helper behavior rather than generated-release bootstrap acceptance.

Full committed-source Trixie checks and release packaging remain required
before publication. Installed RC3 bytes and published archives are unchanged.
No new code or licensing material is imported. The registry-default/fallback
change is a separate topic.

Co-Authored-By: Codex <noreply@openai.com>

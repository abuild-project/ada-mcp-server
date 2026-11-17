# Automatic local image tags

Images imported from a release archive could appear only by digest in Docker,
requiring a manual tag for every installed version. Successful bootstrap now
assigns `ada-mcp-server:v<project-version>` after Doctor, including warm-cache
installs and restoration through an existing binding. Docker-compatible tags
replace `+` in SemVer build metadata with `_`.

The local `v` prefix matches the published GHCR version-tag convention. The
alias is verified against the selected immutable target and recorded in the
setup report. Repeated setup reuses the same alias. An existing different
target is reported as `image_tag.status: "conflict"` and left unchanged;
unavailable or failed tag operations report `"error"`. Neither naming outcome
blocks verified installation or binding publication after Doctor succeeds.
The check and Docker's tag operation are separate daemon calls, so concurrent
external retagging is outside this check's atomicity guarantee. Bindings and
launchers keep their digest pins. Doctor and queries remain read-only.

Host controls cover cold/warm and new/existing bindings, optional tag failures
and conflicts, immutable OCI targets, and Doctor-before-tag ordering. The
bootstrap regression controls reject the original behavior. Separate testing
and independent review assess the same immutable candidate against base
`a3f16279c08dffbe87c6f09ea77e88ed9d6df04b`. Actual macOS Docker calls
through the source helper create then reuse the RC3 alias; they establish
source-helper behavior rather than generated-release bootstrap acceptance.

Current-head host and hosted Trixie validation is recorded in the PR comment.
Installed RC3 bytes and published archives are unchanged.
No new code or licensing material is imported. The registry-default/fallback
change is a separate topic.

Co-Authored-By: Codex (GPT-6) <noreply@openai.com>

# Registry downloads with archive fallback

Normal bootstrap setup previously selected the release image archive, even
when the same published version was available through GHCR. New bindings now
prefer the release-specific GHCR version tag and use the hash-locked archive
if the pull fails or times out. `--image-cache` selects its cache and
`--transport archive` explicitly requests archive-only provisioning. Explicit
local archives and digest-pinned registry references retain their own routes.

The version tag locates data rather than granting execution trust. Successful
pulls still require the locked canonical config digest, platform, source and
version before execution; inspection/export/identity failures never fall back.
Reports retain pull evidence and the transport actually used. Warm defaults
can reuse an already pinned local target. Existing bindings keep their recorded
source; newly created fallback records require their matching runtime parser.
No installed runtime or published release archive is changed by this patch.

The existing daily GitHub Release advisory and consented update workflow are
unchanged. A Docker tag refresh alone does not retarget a running pinned MCP
installation or update its host helpers. The image-tagging topic is separate.

All 1,013 host tests and nine supplemental compatibility controls pass with
the locked dependencies, as do Ruff, strict Mypy, requirements and docs checks.
Default-source sensitivity rejects the base's archive selection. Separate
testing and independent review assess the same immutable candidate against
`a3f16279c08dffbe87c6f09ea77e88ed9d6df04b`. Source-helper checks on macOS verify
an actual anonymous GHCR pull and a real archive load after an injected pull
failure, preserving the installed binding. They do not establish a new
generated-release bootstrap or expand documented Mac support. Hosted Trixie
and artifact acceptance at the current head belong in the PR validation comment.
No third-party code or licensing material is imported.

Co-Authored-By: Codex (GPT-6) <noreply@openai.com>

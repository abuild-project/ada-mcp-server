# Registry downloads with archive fallback

Normal bootstrap setup previously selected the release image archive, even
when the same published version was available through GHCR. New bindings now
prefer the release-specific GHCR version tag and use the hash-locked archive
if the pull fails or times out. `--image-cache` selects its cache and
`--transport archive` explicitly requests archive-only provisioning. Explicit
local archives and digest-pinned registry references retain their own routes.

Without an explicit cache path, macOS uses its user Library/Caches directory;
Linux honors an absolute XDG_CACHE_HOME and otherwise uses ~/.cache, with
ada-mcp/images beneath each cache root. Empty/relative XDG values are ignored.
The resolved absolute path is saved in the binding, and existing cache paths
are never migrated. Registry version errors explain the supported stable/RC
forms and the archive override; acquisition/publication formats are unchanged.

The version tag locates data rather than granting execution trust. Successful
pulls still require the locked canonical config digest, platform, source and
version before execution; inspection/export/identity failures never fall back.
Reports retain pull evidence and the transport actually used. Warm defaults
can reuse an already pinned local target. Existing bindings keep their recorded
source; newly created fallback records require their matching runtime parser.
No installed runtime or published release archive is changed by this patch.

The existing daily GitHub Release advisory and consented update workflow are
unchanged. A Docker tag refresh alone does not retarget a running pinned MCP
installation or update its host helpers. The accepted optional image aliases
from main remain in place, including nonblocking conflict/error reporting.

Controls cover default/explicit sources, fallback and identity boundaries,
cache-platform rules, actionable version errors and the combined alias/binding
behavior. Sensitivity checks reject the prior defaults and diagnostics. Separate
testing and independent review assess the exact combined immutable candidate.
Current-head host, complete Trixie and generated-artifact validation are
recorded in the PR validation comment. Source-helper checks on macOS verify
an actual anonymous GHCR pull and a real archive load after an injected pull
failure, preserving the installed binding. Those earlier source-helper checks
remain development evidence and do not expand documented Mac support.
No third-party code or licensing material is imported.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

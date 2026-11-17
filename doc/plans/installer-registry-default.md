# Registry downloads with archive fallback

Base revision: `a3f16279c08dffbe87c6f09ea77e88ed9d6df04b`.

## 2026-11-17: Registry as the normal installation route

Use GHCR for new bindings, with the verified release archive as fallback when
the registry pull fails or times out. A release-specific version tag locates
the bytes; the authenticated runtime's canonical config hash, platform,
source revision and version remain the acceptance criteria before execution.
Inspection/export/identity failures after a successful pull stop setup and
never select a different transport. Preserve explicit digest-pinned --registry
and local --archive inputs. --image-cache selects the fallback cache;
--transport archive explicitly requests archive-only setup. Existing bindings
keep their recorded source, and an already pinned local image can be reused.

The new registry-fallback binding source stores that bounded locator/cache;
runtime and launcher execution still use a validated immutable target. Keep
binding version 2 and workflow contract 1, whose selected runtime validates
its own binding. Do not migrate existing bindings or change installed RC3
artifacts. No latest tag, automatic installation or update-policy change is
introduced. Record actual transport choice, pull failures and fallback proof.

This is separate from the accepted image-tag topic. The coordinator is the
developer and sole source editor; the same separate tester and independent
reviewer assess its new immutable candidate. Start local/PR correction
counters at zero for this topic and preserve failed evidence. Follow the
required local workflow and then create a dedicated PR. Hosted repository
checks remain separate from the completed native RC3 acceptance; no release,
merge, force-push or plugin publication is authorized.

## 2026-11-17: Combined installer validation

Integrate main at `cd21c0a39b109dae1e3008b3aed73a6e5bc2fe18`, retaining the
accepted optional v-prefixed image aliases. Resolve the CHANGELOG conflict
without dropping either feature and update combined-test fixtures with the
archive metadata now needed by default bindings. Isolate transport-only tests
from the alias helper and exercise their interaction with a conflicting alias.

Keep GHCR as the explicitly approved default. Use
`~/Library/Caches/ada-mcp/images` on macOS; on Linux use an absolute
`XDG_CACHE_HOME`, otherwise `~/.cache`, with `ada-mcp/images` beneath it.
Explicit --image-cache wins, and existing binding paths are never migrated.
For versions outside the existing coordinated registry formats, improve the
error to name supported forms and --transport archive without broadening
acquisition or release-promotion syntax.

Perform this as the first bundled PR correction, retaining the assigned
developer/tester/reviewer roles. Validate the exact combined commit through
the complete supported Trixie chain and generated-artifact acceptance, then
update this PR by normal push, current-head CI, Copilot review and a validation
comment. A PR merge or release still requires separate authorization.

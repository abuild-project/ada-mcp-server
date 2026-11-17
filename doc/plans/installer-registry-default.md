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

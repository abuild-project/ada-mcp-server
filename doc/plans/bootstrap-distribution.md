# Standalone bootstrap and distribution

Status: implementation; initial coordinated version `0.2.0-rc.1`.

## 2026-11-12: Agreed implementation

Decision: continue independently from personal fork revision
`961f532bcc633189e8618852732be289752cbcd7` while preserving all imported history,
upstream attribution and MIT notices. The new main import identifies the
development status before the distribution topic is published. Review both
commits against the imported source, rather than only the topic diff.

Decision: maintain server, pinned standalone AMD64 Trixie container, host
binding tools and lightweight skill plugin in one repository and coordinate
their version. Our imported host helpers may be distributed under MIT under
the maintainer's explicit rights confirmation; old pilot copies remain intact.

Decision: require complete local validation and independent review, then a
checked GitHub PR with hosted CI/Copilot. Stop before merge, tags, releases,
GHCR publication and the existing account-plugin update. Publication requires
a later maintainer decision. Reuse tested artifacts instead of rebuilding them.

Decision: use GitHub-hosted CI, GitHub Releases and GHCR without self-operated
services. Ordinary artifact acquisition must not require Plugin Creator owner
access or unsupported remote skill-file reads. Keep image IDs and release
digests in generated artifact metadata to avoid circular source dependencies.

Acceptance includes unit/style/typing/coverage/package/docs checks and real
ALS/MCP integration in AMD64 Trixie, host provisioning with the same tested
artifacts, exact source-bound project views, both numeric identities 1000:1000
and 501:20, readonly roots, isolated runtime and confirmed EOF cleanup. New
readable copies serve the second identity; original source permissions remain
unchanged. Actual Mac, other clients, a cold cache, registry transport and
fresh managed Cloud deployment stay unvalidated until specifically observed.

Additional functional changes from other forks or upstream proposals are
separate topics. The initial scope includes the selected ancestor-GPR fix and
new distribution boundaries, not a broader server feature expansion.

## 2026-11-12: Build and validation boundaries

Decision: derive the complete Docker build context and version metadata from
the committed Git tree, because a clean Git status does not bind ignored local
files to that source revision. The check harness uses the same source snapshot.

Decision: give only CI a private executable scratch mount and place its TMPDIR
there, because direct fixture execution is part of the required tests. Keep
production temporary files nonexecutable and preserve the other isolation flags.

Decision: require a source-bound malformed/repaired/malformed diagnostic
publication control with stable observed MCP/ALS processes in the real check
chain. Preserve command receipts for timeout/start failures before propagating
those errors, so failed attempts remain reviewable.

## 2026-11-12: Portable Linux process observation

Decision: observe MCP/ALS parentage and process start ticks through core Linux
procfs records rather than an optional task children interface. Require one
identifiable live ALS child and stable observed process births; missing or
ambiguous data must fail instead of being replaced by log-only evidence.

## 2026-11-12: Portable image identity and retained evidence

Decision: keep the canonical config digest separate from the locally executable
Docker target. Authenticate the target-to-config relationship using bounded
Classic/OCI archive metadata and immutable descriptor hashes/sizes. Verify the
loaded target as data before execution, including conversions between stores.
Reuse this identity contract for bindings, queries and prepared promotion.

Decision: reject reused check outputs before execution and require an explicit
new output for another attempt. Keep matching Python distributions explicit.
Retain safe inspect/graph metadata and partial command-timeout streams, and
ship the authoritative support guide inside the hash-verified tooling bundle.

## 2026-11-12: Hybrid exports and config byte counts

Decision: preserve the inspected native execution target independently of an
optional OCI archive root, and validate the supplementary graph even when the
native target is the canonical config ID. Bind runtime config descriptor sizes
to the actual config byte count and carry that count into the trusted runtime
metadata and host-binding checks.

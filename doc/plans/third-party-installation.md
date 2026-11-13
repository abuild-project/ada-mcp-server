# Public first installation

Base revision: `9fd401023eb990574b1806f0083799be0cb39d7f`.

## 2026-11-13: Scope and distribution decisions

Decision: provide a public first-install guide for the existing published
`0.2.0-rc.1` pilot, linked from README and host setup. Reuse its immutable plugin,
tooling, acquisition helper and host-binding commands. Do not introduce another
installer, server/runtime changes, a new version or replacement release assets.

Decision: describe a reader-owned private Cloud plugin import through available
Plugin Creator capabilities. Verify the public archive before saving its local
path; inspect the returned identity and audience, which can be the active
workspace or personal account. Preserve intended existing installations on
updates. The public package contains a skill, not native MCP registration.
No public directory listing, publisher-private plugin ID or self-operated
service is required. A separate-account import remains unverified until tested.

Decision: document a local route independent of Plugin Creator. Acquire the
public source tag into a new directory, verify its exact release commit, then
use the released acquisition helper and pinned archive/manifest hashes. Install
the verified skill into an explicit project discovery root and reuse explicit
Docker bindings across actual source/dependency roots and GPR views.

Decision: keep actual macOS and native Codex/Claude/OpenCode integration in
development. Generated TOML, local discovery and private-account execution do
not establish another client's registration or another account's acceptance.
Use client-specific guidance without invented registration commands or an
automatic-update promise. Keep compiler/test/coverage CI separate from MCP.

Decision: retain the repository's coordinator/developer/tester/independent-review
workflow. Targeted documentation and released-command checks can validate this
guide; they do not replace the exact-candidate container check chain or the
separate-account/native-host acceptance gates. Operational evidence and
correction counters remain outside tracked source.

## 2026-11-13: Supplied Cloud evidence boundaries

Decision: reflect the independently checked 15-call managed Cloud Arca
request/result batch at source `20564468d00024e6f949e92c1da79850abf59086`
as bounded source-result evidence. The supplied execution text is a summary,
not full process/protocol/Bootstrap/Doctor/command logs. Do not infer new
process, isolation or cleanup certification from it, expand tool-wide support,
or equate this reported private-account workflow with native Cloud registration,
separate-account plugin import or macOS/other-client acceptance.

## 2026-11-13: Direct README usage

Decision: make README itself a direct manual first-use entry point. Include
prerequisites, pinned public acquisition through the existing helper, shared
Docker Bootstrap, an actual GPR/source-bound batch and the exact query command.
Show native stdio fragment generation with explicit supported merge/reconnect
and development-only runtime boundaries. Describe skill/plugin installation
as optional convenience rather than a prerequisite for using Ada MCP.

## 2026-11-13: README audience refinement

Decision: supersede the command-heavy README quickstart with a concise user
entry point. A user includes an Ada developer applying MCP to their own project;
a contributor changes, builds, tests or releases Ada MCP itself. Explain
purpose, supported tasks, prerequisites and install-connect-use steps with
descriptive links to exact detailed sections. Keep all source/hash/acquisition,
Bootstrap, JSON batch and native TOML commands in the first-install/setup
guides. Users need no MCP build, CI run or publication-provenance knowledge.
Keep standalone MCP use independent of optional skills/private plugins and
link contributor development separately.

## 2026-11-13: Update notices and manual activation

Decision: supersede the documentation-only implementation scope with a host-side
release notice and a concrete manual update/rollback path, as requested by the
maintainer. Keep the existing documentation snapshot and published RC1 immutable;
RC1 has no notice hook and needs an initial manual upgrade after a future
notifier-capable release exists. No new version or publication is authorized here.

Decision: a fixed anonymous GitHub release-metadata request runs at launcher
startup, at most daily per channel, with a private cache, opt-out and a small
bounded delay. Stable installations follow stable versions; prerelease installs
can see newer prereleases or stable versions. Kill and reap a synchronous fetch
child at its two-second deadline. Offline, cache, rate-limit and parsing failures
never block MCP use or imply that an installation is current. A bounded feed
without a newer candidate cannot establish currency if it is incomplete.

Decision: pass only sanitized version/URL/freshness metadata through an explicit
environment snapshot into the unchanged network-isolated container. Add advisory
data to project_info and initialization instructions so both query clients and
native stdio clients can receive it; preserve existing instructions and protocol
stdout. The skill relays one notice per chat. Actual frontend rendering remains
client-specific. No background worker, protocol proxy, extra mount, executable
download, automatic updater or moving immutable pins is part of this scope.

Decision: document new-runtime/new-binding verification before user-controlled
activation, and retain the old runtime, image and binding for operational
rollback. A local skill switch preserves its old symlink and storage with
no-clobber guards. Native config changes require explicit supported merge and
reconnect, retaining the old fragment. Cloud updates preserve the intended
private identity/audience; providers may reject lower package versions, so
package rollback requires a supported restore or forward corrective version,
not an assumed re-upload of an older archive. Keep contributor internals out
of the user README and keep the existing role/correction budgets.

## 2026-11-13: Declared source for host advisories

Decision: load the shared host advisory validator and checker from their
declared Python source bytes, excluding ordinary sibling bytecode lookup.
Suppress bytecode writes before loading own source, including direct isolated
entry points and fetch children. Keep the one shared parser and locked
manifest/server version correspondence. Advisory use must leave the verified
runtime unchanged even when an unmanifested bytecode cache is already present;
do not delete or mutate that cache. Keep executor capacity and current delivery
status in operational evidence rather than the durable change record.

## 2026-11-13: Fresh searches and consent-gated agent execution

Decision: extend the skill from notification/link guidance to an explicit
ask-and-execute workflow. Inspect real target release provenance, compatibility,
active installation scope and capabilities before asking once. An identified
update request already supplies consent; a search request does not. On no/defer,
leave the installation unchanged and suppress repeated proposals. On yes, use
the known acquisition/bootstrap/Doctor/query tools with NEW trusted target pins,
then update the relevant installed skill/private Cloud copy/client entry and
verify actual activation. Preserve identity, audience and rollback artifacts;
report staged versus activated when a provider or reconnect step is unavailable.
The full and generated lightweight skills share one canonical workflow block.

Decision: GitHub target-release asset digests authenticate its release manifest;
cross-check the exact repository, tag commit, version, source and artifact
URLs/metadata before executing new tooling. The old embedded hashes and the
availability notice are not a trust source for a new version. Consent does not
authorize repository source/history edits, public publication or shared-service
changes. No separate automatic updater executable is introduced.

Decision: explicit updates check performs one fresh bounded request without
waiting for automatic success/offline TTL. Updates status stays cached/read-only,
and automatic snapshots remain daily. A one-shot manual auto/channel selection
works while automatic opt-out stays unchanged. Honor actual upstream numeric or
date Retry-After/rate-reset deadlines across both channel caches for the fixed
endpoint; separate them from artificial daily cooldowns. Lock contention and
provider blocks cannot be reported as a newly fetched up-to-date result.

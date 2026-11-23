# Changelog

## Unreleased

- Add short guides for installing and using Ada MCP on Mac/Codex, Managed
  Cloud and direct Docker, including first queries, updates and rollback.
  Prepare a GitHub Pages build from the Markdown user guides.

## 0.2.0-rc.6 — pilot prerelease

- Pin the working host Python in new native configurations, make update policy
  explicit, and diagnose missing/unsupported advisory Python or failed checker
  processes while keeping MCP usable. Bound the interpreter version probe to
  two seconds; invalid inherited channels disable only the startup/query advisory
  while generation and offline checks remain strict. Add host validation and clarify
  separate Mac/Codex and Managed Cloud setup, current-release onboarding and
  the supported PATH correction for immutable RC5 installations.

## 0.2.0-rc.5 — pilot prerelease

- Reject unknown tool names before starting Ada Language Server, and report
  advertised tools without handlers accurately.
- Expand the locked MCP SDK 1.30 input-validation test basis through real stdio
  rejection/startup controls and bounded real-ALS integration checks, without
  changing tool schemas, dependencies or supported behavior.
- Clarify once-per-user Codex installation across Ada repositories and worktrees,
  including actual client-managed worktree roots, explicit configuration merges
  and RC4's GHCR default. Record bounded macOS/Codex Desktop RC4 acceptance;
  published archives and already installed skills remain unchanged.

## 0.2.0-rc.4 — pilot prerelease

- Retain explicitly selected GPR views for queries anchored to imported source
  files outside their directories, including equivalent absolute paths.
  Shared imports use the most recent matching explicit selection unless an
  explicitly selected lexical ancestor applies. Project info observes the live
  view by default; optional Boolean `refresh: true` reevaluates changed source
  membership. Fresh startup avoids a redundant
  reload, and valid metadata remains available while indexing is pending,
  reported separately by the Boolean `indexing_complete` snapshot.
- Default new bootstrap bindings to GHCR with the hash-locked release archive
  as a fallback for pull failure or timeout. Preserve immutable runtime pins,
  explicit source overrides and existing binding sources; `--transport archive`
  selects archive-only provisioning. Use platform-native image cache defaults
  and explain the archive override for versions outside the registry format.
- Give successful bootstrap installations a local
  `ada-mcp-server:v<project-version>` alias, while preserving immutable runtime
  pins. Report conflicting or unavailable aliases without overwriting them or
  blocking the verified installation.
- Raise optional development minimums to Ruff 0.17.5, pytest-asyncio 1.5.0
  and Mypy 2.4.1.
- Attribute separate protected-body imports to their declared owner and include
  limited/private context imports in dependency graphs, excluding aspect
  specifications in generic formal parts or after the unit declaration.
- Attribute a separate task body's ordinary context imports to its declared
  task name, instead of an inner declaration or an omitted unit.
- Return integer zero for a malformed selected native parameter index and
  preserve its exact raw value and source in `parameter_selection_diagnostic`.
  Keep any simultaneous signature-selection diagnostic independently.
- Return the effective signature index used for parameter selection. A malformed
  native `activeSignature` selects the first signature and preserves its exact
  raw value in a conditional `selection_diagnostic` field.
- Attribute dependency imports to the actual generic unit instead of its
  formal subprograms, formal packages or access-to-subprogram profiles.
- Reject unsupported rename application (`preview=false`) explicitly instead
  of reporting that proposed changes were applied.
- Preserve legal bare code-action command identifiers and native rename
  preview replacement text without applying edits.
- Ignore Ada comments and quoted strings when identifying units in bounded
  dependency summaries, including doubled quote escaping and quote-character
  literals inside qualified expressions.
- Synchronize a queried source before evaluating its call hierarchy, so
  changes to that file replace its previously opened contents.
- Honor the selected signature's active parameter before the top-level
  fallback, including an explicit zero and documented index defaults. Apply
  defaults only within the LSP unsigned integer domain; retain malformed
  raw values for diagnosis.

## 0.2.0-rc.3 — pilot prerelease

- Validate selection inputs on the same non-symlink descriptor used to read
  their bytes; reject malformed nested image metadata with structured errors
  while preserving the active runtime selection.

- Let compatible full/local and lightweight entries reuse an exact verified
  runtime/binding selection without a plugin upload or skill replacement.
  Later sessions need retained files and the same default/custom locator.
- Check an explicit workflow contract and pinned selection before use; provide
  consented no-clobber activation, expected-state backups and rollback.
- Distinguish entry package version from active runtime version and fresh-session
  bootstrap from persistent state; preserve the public RC1/RC2 legacy routes.

## 0.2.0-rc.2 — pilot prerelease

- Provide RC2 first-install and initial-upgrade guidance using actual published
  asset digests and new target pins, retaining the verified RC1 fallback.
- Publish version-specific reviewed release notes from the approved source
  commit alongside the unchanged tested artifact set.
- Execute installed helpers from their verified source bytes and reject relative
  explicit notice-cache paths before client configuration or query startup.
- Dispatch setup queries through the retained verified client, preserving the
  query CLI and rejecting undeclared clients before startup.
- Retain verified checker/validator bytes through isolated release fetches and
  refuse undeclared installed sources before checking for updates.
- Require a manifest for packaged smoke startup and retain installed mode if
  metadata disappears; source fallback requires the contributor tooling/src layout.
- Check public release metadata from the host with a private daily cache,
  bounded timeout and opt-out; expose available-version advisories through
  MCP initialization/project results without moving installed pins.
- Recompute advisory freshness on each MCP read: snapshots at least one day
  old carry the stale warning; notices older than seven days remain omitted.
- Let explicit update checks search afresh without waiting for the daily cache,
  while honoring provider retry deadlines across stable/prerelease channels.
- Apply quota-reset waits only when no quota remains; preserve explicit
  Retry-After waits, including maintenance responses.
- Retain observed provider waits after successful responses and invalid,
  oversized or unreadable release feeds without discarding valid feed data.
- Honor surrounding HTTP space/tab padding on retry deadlines while retaining
  raw header-length, syntax and expiry limits.
- Ask once before a skill executes a verified update, including new target
  pins, matching runtime/skill/client activation and preserved rollback state.
- Add public RC1 first-install guidance for reader-owned private Cloud skill
  copies and local Codex/Docker setup, preserving native-client acceptance limits.

## 0.2.0-rc.1 — pilot prerelease

- Provide an independent, coordinated server/container/tooling distribution
  under abuild-project, preserving the original MIT history and authorship.
- Provide standalone AMD64 Trixie setup and explicit host bindings for multiple
  Ada repositories, retaining the selected ancestor-GPR behavior.
- Run supported project, symbol, navigation and file-diagnostic queries in a
  read-only, nonroot container with isolated imports and private evidence.
- Verify acquired tooling and images against immutable hashes and bind release
  packaging to the exact source, Python distributions and image checked in CI.
- Require MCP SDK `>=1.30.0,<2` and pin 1.30.0 in the container, excluding
  the advisory-affected older SDK versions.

This prerelease covers the documented Linux/AMD64 container workflow.
Actual macOS, native Claude/OpenCode integration and fresh managed Cloud
acquisition require their own acceptance. See the [release notes](doc/releases/0.2.0-rc.1.md)
for the pilot limits and [GitHub Releases](https://github.com/abuild-project/ada-mcp-server/releases)
for published artifacts.

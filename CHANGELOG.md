# Changelog

## Unreleased

- Execute installed helpers from their verified source bytes and reject relative
  explicit notice-cache paths before client configuration or query startup.
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

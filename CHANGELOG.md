# Changelog

## Unreleased

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

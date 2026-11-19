# Shared Codex installation

Base revision: `7864cda95a5dfc264926a5110416196279ff957c`.

## 2026-11-19: User-wide setup and bounded Mac acceptance

Document one persistent installation per user, shared across Ada repositories
and Git worktrees. Default Codex discovery to `~/.agents/skills/ada-development`
and native registration to `~/.codex/config.toml`; retain repository scope as
an explicit alternative. Use existing RC4 helpers without changing server,
helper, SDK, version or workflow contracts. Keep GPR, ordered search paths and
scenarios explicit per connection rather than pinning one global project.

Choose physical development workspace parents and actual client worktree roots
once with the user. Approval of a parent permits read-only access to all its
descendants; future descendants need no separate mount. Discover the actual
Codex worktree location, including custom homes, without changing CODEX_HOME
or mounting arbitrary directories. Preserve existing bindings and unrelated
client entries. Generate new bindings/fragments and activate only through
consented merges, expected-state selection changes and backups.

Make the current-release first-install path usable without an installed
acquirer, preserve GHCR as RC4's default and explain archive fallback. Document
supported full quit/reopen and new/resumed-chat checks without inventing UI.
Record the supplied curated Mac evidence in a sanitized assessment with its
archive hash, versions, source boundaries and limits. Published RC4 archives
and already installed skills remain immutable; these edits update source
documentation only. Historical release notes and plans remain unchanged.

The assigned developer alone edits the candidate. Prepare a coherent local
commit, modest documentation/example checks and the required short change
record. The assigned tester and independent reviewer assess that immutable
revision under AGENTS.md. No push, hosted PR, merge or publication is authorized.

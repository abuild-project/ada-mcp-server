# Native rename previews

Base revision: `68f93cfe5f0b91d797b01e3e5578bd02d9ded09a`.

## 2026-11-23: Authorized scope

Expose the existing `ada_rename_symbol` preview tool in newly generated
Codex native fragments alongside the unchanged 16 read tools. Configure its
per-tool `approval_mode = "prompt"` under
`mcp_servers.ada.tools.ada_rename_symbol`; keep server settings outside that
nested table. Current Codex configuration schema supports this setting, matching
the earlier Abuild native configuration policy.

Preserve the command helper's 16-name `READ_TOOLS` set and explicit
Boolean `preview=true` guard. Preserve the server's default preview, rejection
of `preview=false` and `applied=false` result. Add no writer, SDK/dependency
change, other tool exposure or broader semantic support claim.

Supplied RC6 macOS 26.5.1 arm64 evidence reports 37 native-runtime
STDIO calls, including 18 real Abuild and two fixture rename proposals with
exact old text and `applied=false`. Desktop omitted the tool from its native
catalog. The changed fragment still needs Mac acceptance. Retain historical
RC4/RC6 documentation and immutable release
artifacts. Existing users must acquire a verified runtime containing this
change, generate a new fragment, explicitly merge only the backed-up Ada entry
and reconnect; never patch authenticated installed helpers in place.

Add a regression that generates and parses an actual packaged native
fragment and rejects the missing-tool and missing-approval-policy behavior.
Reuse server preview/default/rejection tests and bounded semantic evidence.
Run focused host development checks, then freeze one coherent commit for a
separate tester's exact-source AMD64 Trixie chain and independent review.
The coordinator assigns developer, tester and reviewer without recursive
delegation and handles hosted delivery. This new topic starts at local 0/3
and later PR 0/3.

## 2026-11-23: Maintainer-approved normal policy

The maintainer supersedes the initial rename-specific prompt choice. Keep all
17 native tools, remove that approval override and annotate only
`ada_rename_symbol` with the locked SDK's `ToolAnnotations(readOnlyHint=True)`.
Normal Codex approval and trust policy applies. Preserve explicit policies.
Keep the helper's separate allowlist and explicit Boolean preview guard, server
default preview, false rejection and `applied=false` behavior unchanged.

Mac acceptance remains pending. Check normal configuration in new and resumed
Desktop chats, 17 direct native tools including rename, no special rename
prompt, `applied=false` and identical before/after source hashes. These are
acceptance criteria. Earlier published RC6 STDIO proposals and the missing
Desktop tool remain the observed Mac evidence. Cloud roles cannot rerun
Desktop on Mac.

Require negative controls against published parent
`fc913deeeadeb80949ff02ad8457b0cb7abba812` for both the generated TOML override
and serialized MCP catalog annotation. Reuse existing server behavior tests
and the exact-source Trixie chain. This is PR correction 1/3; local remains 0/3.
When preparing the first release containing this change, its release PR must
revise the unreleased-generator wording in [setup.md](../setup.md),
[first-install.md](../first-install.md), [support.md](../support.md) and
[integrations/full-skill.md](../../integrations/full-skill.md). The coordinator
handles hosted delivery. This correction authorizes no release or merge.

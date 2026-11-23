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

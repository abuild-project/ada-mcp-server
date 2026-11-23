# Native rename previews

The generated Codex native entry omitted `ada_rename_symbol`, although the
server already returns rename proposals without applying edits. Supplied RC6
Mac observations confirm that proposals work over STDIO while the Desktop
tool catalog excludes rename.

New fragments enable the existing 16 read tools plus rename under normal
Codex policy. The server marks only rename with MCP `readOnlyHint=true`.
Explicit approval and trust policies still apply. The command helper's read
allowlist and explicit `preview=true` guard remain unchanged.
The server still defaults to preview, rejects application and returns
`applied=false`.

Published RC6 artifacts remain unchanged. Existing users need a verified
runtime containing the generator change, a newly generated fragment, an
explicit backed-up merge of only the Ada entry, and reconnection. Earlier
rename-specific prompt overrides need an explicit removal when normal policy
is intended. The [plan](../plans/native-rename-preview.md) records scope and
activation limits.

Regressions reject the missing rename tool at the original base and the prompt
override and absent serialized read-only hint at `fc913de`. They check the exact
generated tool set and real SDK-serialized catalog. Focused host checks
cover generation, helper boundaries and existing server preview contracts.
The AMD64 Trixie chain runs the packaged regression with the existing server
tests. Mac acceptance of normal policy in new/resumed chats remains pending,
including 17 native tools, no special rename prompt, `applied=false` and
unchanged before/after source hashes.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

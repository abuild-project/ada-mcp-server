# Native rename previews

The generated Codex native entry omitted `ada_rename_symbol`, although the
server already returns rename proposals without applying edits. Supplied RC6
Mac observations confirm that proposals work over STDIO while the Desktop
tool catalog excludes rename.

New fragments enable the existing 16 read tools plus rename, with
`approval_mode = "prompt"` scoped to its native tool table. The command
helper's read allowlist and explicit `preview=true` guard remain unchanged.
The server still defaults to preview, rejects application and returns
`applied=false`.

Published RC6 artifacts remain unchanged. Existing users need a verified
runtime containing the generator change, a newly generated fragment, an
explicit backed-up merge of only the Ada entry, and reconnection. The
[plan](../plans/native-rename-preview.md) records scope and activation limits.

At base `68f93cfe5f0b91d797b01e3e5578bd02d9ded09a`, the packaged-generator
regression rejects the missing rename tool. It checks the exact parsed approval
table and tool set after the change. Focused host checks
cover generation, helper boundaries and existing server preview contracts.
The AMD64 Trixie chain runs the packaged regression with the existing server
tests. The
changed configuration has not been tested on Mac/Codex Desktop.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

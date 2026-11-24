# First stable 0.2.0 release

Prepare `0.2.0` from accepted main
`95cf6e6d70d556ee9547d849ce44dae2edd588f2`, coordinating server/Python,
image/tooling/skill metadata, changelog and reviewed release notes. XML/Ada
development exports, native rename previews and the user guides carry forward.
The locked MCP SDK 1.30.0, runtime behavior, workflow contract and bounded
tool/client support remain unchanged.

Promotion now distinguishes supported RC tags from stable tags. RCs retain
`--prerelease`; stable publication uses `--latest`. Exact source approval,
reviewed notes, trusted merged-main CI, tag correspondence, tested artifact
hashes and anonymous GHCR identity checks remain required. Focused argument
coverage rejects the previous stable-as-prerelease behavior while preserving
RC flags, note bytes and the asset set.

Current installation/update guidance targets stable only after actual
publication and authenticated pins. Existing native entries need explicit
regeneration, an Ada-entry merge and reconnect for rename. Historical RC
artifacts and bootstrap acquirer pins remain intact. The release notes place
versioned component metadata and exact Debian/ALS source directions beside
the image download, retaining notices and maintainer access responsibility.

The [supplied Mac assessment](../assessments/pre-stable-consumer.md) records
prepared-Abuild XML/Ada navigation and direct native rename previews in fresh
and resumed Desktop chats on the accepted implementation, with unchanged
sources and `applied=false`. This is bounded supplied evidence, separate from
independent Mac replay and final published stable-artifact acceptance.
The [dated plan](../plans/release-0.2.0.md) retains delivery gates and the later
project-build-derived image recommendation. No account-plugin update is included.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

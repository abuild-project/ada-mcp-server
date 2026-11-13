# AnyIO input and installed version alignment

The AnyIO input requests 4.16.0, but Docker continues installing 4.14.2 from
the unchanged hash lock. Passing tests on that revision do not establish
behavior under the requested upgrade.

Regenerate the single hash lock for AnyIO 4.16.0, preserving all other
package versions and hash sets. Keep the existing `mcp<2` dependency range,
pinned SDK and documented support boundaries.

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388448058),
but its build log installed AnyIO 4.14.2. Local preparation verifies
input/lock agreement and hash structure. The corrected merged revision
requires complete Trixie CI with the requested installed version, real
initialization/diagnostic controls, both numeric identities and
EOF/container cleanup, plus independent review.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

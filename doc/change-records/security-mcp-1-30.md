# Patched MCP 1.x dependency baseline

The pinned MCP 1.28.1 dependency and the previous public minimum admit SDK
versions covered by upstream advisories for
[HTTP session retention](https://github.com/advisories/GHSA-84m7-p3x7-pcfv),
[token audience validation](https://github.com/advisories/GHSA-w4fh-qvv9-3v23),
[external schema references](https://github.com/advisories/GHSA-rwrf-2pqf-9j8j)
and [cross-origin HTTP redirects](https://github.com/advisories/GHSA-5h93-6whr-6q8j).
Require the patched 1.30.0 baseline in the public `mcp>=1.30.0,<2` range and
pin 1.30.0 in the shared runtime input and hash lock. Keep the supported 1.x
API line; this change does not adopt SDK 2.

Lock regeneration changes only MCP and its distribution hashes. All other
accepted package versions and hash sets are preserved. Canonical project
version `0.2.0-rc.1`, Python/MCP server version `0.2.0rc1`, the builtin version
provider, strict provenance checks and support scope remain unchanged.

The accepted server uses stdio and the bundled command client uses its own
JSON-RPC process pipes. The advisory-affected HTTP session/auth/client routes
and SDK-client external-schema validation are not reachable in that workflow.
This is dependency security maintenance, not a claim that a demonstrated
product exploit was repaired or that unsupported HTTP wrappers were tested.
If HTTP bearer authentication is introduced, its resource/audience checks
still require explicit configuration; upgrading the SDK alone does not enable
them. Alert closure requires separate evidence rather than automatic dismissal.

Developer preparation resolves the hash lock for Linux/AMD64 with uv 0.13.5
and Python 3.13.5 and checks direct input/lock/public-range agreement,
unchanged unrelated package hashes, maintained documentation and whitespace.
Those checks do not replace the complete exact-source Hosted AMD64 Trixie
chain, actual installed MCP 1.30.0, semantic/two-identity acceptance or
independent review. New source and consumer artifact pins must come from the
newly accepted revision; earlier 1.28.1 receipts do not certify this update.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

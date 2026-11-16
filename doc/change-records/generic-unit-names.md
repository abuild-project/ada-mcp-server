# Generic unit dependency names

`ada_dependency_graph` could assign context imports to a generic formal
function, procedure or package instead of the actual compilation unit. An
access-to-function profile could produce the owner `return`, and a keyword
suffix inside `Callback_Function` could yield `is`. Import sets and unit
counts alone therefore did not establish correct dependency ownership.

Unit selection now consumes optional `with` or `access [protected]`
introducers together with each declaration candidate in one forward scan.
It skips those non-unit candidates and retains whole-keyword boundaries.
This avoids copying and searching the growing source prefix for every
formal. Existing masking preserves comments and line breaks as whitespace;
ordinary with-clause extraction, file/directory behavior and response shape
remain unchanged. This is a bounded lexical correction, without a complete
Ada parser or limited/private-with support.

Focused regressions reproduce the ownership defect against base
`4e8a5ebb70b879c7b5b2c7dd297ca6bd3dc72fc5`. They assert exact owners,
imports and counts with unchanged inputs, including ordinary/generic unit
controls and masking regressions. One generated-formals check fails the
repeated-prefix implementation at `8c0997ab1444c51f62b999d12c901f20955912fa`
by counting regex input against a small source-size budget. This is a
deterministic regression guard, not a timing threshold or performance SLA.

The existing integration script queries a small Ada/GPR fixture over real
MCP STDIO and compiles a fresh owned copy with a timeout. It requires a new
ALI artifact in the configured owned object directory and checks hashes of
the three known Ada/GPR inputs. It does not observe arbitrary filesystem
writes. Compiler validity belongs to the managed GNAT 14 chain, not host
parser tests. Pins, version, client policy and the [capability assessment's
support limits](../assessments/additional-tool-capabilities.md) are unchanged.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

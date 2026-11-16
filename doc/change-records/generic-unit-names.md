# Generic unit dependency names

`ada_dependency_graph` could assign context imports to a generic formal
function, procedure or package instead of the actual compilation unit. A
formal access-to-function profile could even produce the owner `return`.
The import set and unit count alone therefore did not establish correct
dependency ownership.

Unit selection now skips candidates introduced by `with` or
`access [protected]` in the already masked source. Comments and line breaks
between those tokens remain meaningful whitespace. Whole-keyword boundaries
also prevent `Callback_Function` from being mistaken for `function is`.
The actual generic
package, procedure or function then owns its context imports. Existing
comment/string masking, ordinary with-clause extraction, file/directory
behavior and response shape remain unchanged. This is a bounded lexical
correction, without a complete Ada parser or limited/private-with support.

Focused regressions reproduce incorrect formal owners at base
`4e8a5ebb70b879c7b5b2c7dd297ca6bd3dc72fc5`; the named access-type case
also rejects the incorrect `is` owner at
`076cfee91dcb055519db01990beacc2f447215da`. They assert exact owners,
imports and counts with unchanged inputs, alongside ordinary and generic
unit controls and existing masking regressions.
A small Ada/GPR fixture combines the distinct formal declarations. The
existing integration script checks its exact dependency result over real
MCP STDIO and compiles it with GPRbuild in a fresh owned copy. Compilation
has a timeout, requires a new ALI artifact in the configured owned object
directory and verifies hashes of the three known Ada/GPR inputs. The GPR
also configures an owned executable directory; this check does not observe
arbitrary filesystem writes. Compiler validity
is assessed in the existing managed GNAT 14 chain, not inferred from host
parser tests. No ALS/SDK pin, version, client policy or support boundary
changes are included; the [capability assessment](../assessments/additional-tool-capabilities.md)
retains the tool's development status and native signature limitations.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

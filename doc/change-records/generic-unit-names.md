# Generic unit dependency names

`ada_dependency_graph` could assign context imports to a generic formal
function, procedure or package instead of the actual compilation unit. A
formal access-to-function profile could even produce the owner `return`.
The import set and unit count alone therefore did not establish correct
dependency ownership.

Unit selection now skips candidates introduced by `with` or
`access [protected]` in the already masked source. Comments and line breaks
between those tokens remain meaningful whitespace. The actual generic
package, procedure or function then owns its context imports. Existing
comment/string masking, ordinary with-clause extraction, file/directory
behavior and response shape remain unchanged. This is a bounded lexical
correction, without a complete Ada parser or limited/private-with support.

At base `4e8a5ebb70b879c7b5b2c7dd297ca6bd3dc72fc5`, five focused checks
reproduce the wrong owners, while three unit-selection controls pass. The
regressions assert exact owners, imports and counts with unchanged inputs.
A small Ada/GPR fixture combines the distinct formal declarations. The
existing integration script checks its exact dependency result over real
MCP STDIO and compiles it with GPRbuild in a fresh owned copy. Compilation
has a timeout, requires a new ALI artifact, verifies source/GPR hashes and
confines outputs to owned object/executable directories. Compiler validity
is assessed in the existing managed GNAT 14 chain, not inferred from host
parser tests. No ALS/SDK pin, version, client policy or support boundary
changes are included; the [capability assessment](../assessments/additional-tool-capabilities.md)
retains the tool's development status and native signature limitations.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

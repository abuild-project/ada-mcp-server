# MCP input validation contract

The locked MCP SDK 1.30 rejects invalid advertised tool arguments before
the server handler acquires ALS. A future SDK 2 migration could silently
remove that boundary. This test-only change records the existing
behavior at base `103bf4cdb9608317686f354e19eb505be49da929`; it changes
no runtime code, schemas, dependencies, locks, versions or supported
behavior.

The real stdio host contract covers eight invalid calls: integer and
Boolean types, missing file and omitted arguments, an invalid direction,
and nested project-path and scenario-value types. Each requires exactly
one text input-validation error, an untouched ALS startup sentinel, a
subsequent reply from the same server process and protocol-only stdout.
Four controls preserve valid input, allowed extra properties, explicit
false refresh and the existing unknown-tool server error. Unknown-tool
errors do not constrain ALS startup. The handler's own refresh Boolean
guard remains unchanged and is currently shadowed by SDK validation.

The existing real-ALS integration probe adds one raw rejected reference
call with unchanged known Ada/GPR input hashes and a separate normal
extra-property document-symbol result, retaining the ordinary call.
Development guidance requires SDK 2 to reproduce server validation or
document a deliberate contract decision.

The sensitivity experiment disables only decorator validation in an
independent owned source copy: the contract must fail, then pass with
the original source restored. No runtime mutation is committed.
Hash-locked host checks use SDK 1.30; complete container and real-ALS
evidence remain separate from these host protocol controls.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

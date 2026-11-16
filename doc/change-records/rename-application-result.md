# Rename application result

`ada_rename_symbol` previously returned `success=true` and `applied=true` for
`preview=false` while leaving sources unchanged. Application is unsupported;
that result incorrectly claimed that native edit proposals had been written.

The handler now returns an explicit unsupported-application failure with
`success=false`, a meaningful error, `changes=[]`, `total_changes=0` and
`applied=false`. Rejection precedes source synchronization and native
prepare/rename requests. The existing shared server connection selection may
initialize ALS before dispatch; this change does not promise otherwise.

Explicit preview and the default continue returning the actual native edit
text with `applied=false`. The tool catalog describes this boundary while
retaining its Boolean parameter and default true. Current support and
assessment documentation agree; historical records remain unchanged. No
writer, client-policy change, support expansion, dependency or version change
is included.

At base `4d688e159339b8ae72726b99cca7be3f8d6d2dc8`, the focused regression
reproduces false application with unchanged owned source bytes. Rejection
controls check that rename-handler synchronization/native requests are absent.
Positive preview/default, catalog and
dispatch controls preserve the existing behavior. The required integration
script adds one real STDIO MCP rejection check on its initialized sample
project, with unchanged Ada/GPR input hashes. Host checks validate the focused
behavior, typing and documentation; native execution remains part of the
existing exact-source managed container chain.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

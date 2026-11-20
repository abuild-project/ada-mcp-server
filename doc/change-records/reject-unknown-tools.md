# Reject unknown tools before ALS startup

Unknown tool calls previously attempted ALS client acquisition before the
dispatch fallback could identify the name. With ALS unavailable, callers
received a connection failure instead of a meaningful unknown-tool error.

The server now checks names against its own advertised catalog before client
acquisition or project selection. An unknown name returns the existing JSON
server-error convention with `Unknown tool: <name>`, `context.tool` and an
available-tools hint; the SDK response retains `isError=false`. Known-tool
schema validation, the handler's refresh guard and routing remain unchanged.
There is no separate name registry, SDK-private cache dependency, schema,
dependency, version or workflow change.

The focused unit test forbids any ALS client acquisition for an unknown name.
The existing real-stdio unknown-tool control requires an absent startup
sentinel, its JSON error, process liveness and subsequent catalog response.
The three known-tool startup controls and eight SDK rejection cases remain
unchanged. An owned source copy of base
`4e80d63e46bbb04d37bb1d9b1689ef39ca453566` supplies the original runtime
for sensitivity checks; both strengthened tests reject it. All 24 focused
host tests, Ruff, strict Mypy and maintained-document checks passed. Locked
SDK 1.30 host checks are development evidence. Complete native validation
uses the existing exact-source AMD64 Trixie/GNAT 14/pinned-ALS chain.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

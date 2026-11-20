# Reject unknown tools before ALS startup

Unknown tool calls previously attempted ALS client acquisition before the
dispatch fallback identified the name, allowing connection failures to hide
the actual problem. The server now checks its advertised catalog before
client acquisition or project selection. Unknown names return the existing
JSON server-error convention with `Unknown tool: <name>`, `context.tool` and
an available-tools hint; the SDK response retains `isError=false`.

The defensive dispatch fallback identifies a different fault: an advertised
tool has no handler. It returns `Advertised tool has no handler: <name>` and
`context.tool`, without directing callers back to the catalog. Known handlers,
schema validation, the refresh guard, dependencies and versions are unchanged.
No duplicate name registry, SDK-private cache or catalog refactor is added.

Unit and real-stdio unknown-tool controls forbid ALS acquisition/startup and
preserve the JSON error, process liveness and subsequent catalog response.
The three known-tool startup controls and eight SDK rejection cases remain.
One mocked advertised tool exercises the missing-handler fallback without
live ALS. It rejects the runtime at
`3a29c62e44d4843e1fbe8272a74ce9b4b7ff4c78`; the unknown-tool controls
reject the original runtime at
`4e80d63e46bbb04d37bb1d9b1689ef39ca453566`. Owned source copies preserve
the candidate during these sensitivity checks. All 25 focused host tests,
Ruff, strict Mypy and maintained-document checks passed with locked SDK 1.30.
This development evidence remains separate from full native validation in
the existing exact-source AMD64 Trixie/GNAT 14/pinned-ALS chain.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

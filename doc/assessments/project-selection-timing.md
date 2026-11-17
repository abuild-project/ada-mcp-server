# Larger-project Mac selection measurement

Status: **pending before release**. Cloud/Linux checks do not establish Mac
startup or indexing latency. Use one real larger GPR view on the actual Mac,
with unchanged source commit, ordered project paths and scenario values.

Compare accepted artifacts for baseline `ced1076fb1e87df0bc73f4702d31160aa0c8cfde`
and the final candidate. Record each source SHA, tooling hash, immutable image
target, ALS/GNAT/Python versions, Mac architecture, Docker version/backend and
whether AMD64 emulation is active. Use separate private bindings/evidence;
preserve the installed runtime and global client/Docker settings.
Provision each binding through its checked CI image archive using explicit
`--archive` and `--archive-sha256`, preserving the exact candidate identity.

For each artifact, run three fresh MCP sessions serially, retaining their raw
protocol and stderr. Use the bundled query client's 90-second request timeout.
In each session:

1. Select the exact GPR with `ada_project_info` once. Record elapsed request
   time, `complete`, `indexing_complete` and any actual error.
2. Query `ada_workspace_symbols` using a known unique project symbol and an
   absolute source anchor. Honor `complete` and `truncated`; allow at most
   three such requests to observe later readiness, without reselecting between
   them. Record elapsed time and compare the exact target with the source.
3. Reselect the same GPR once and repeat the bounded semantic-readiness check.
   Record warm-selection time, membership and whether the same MCP/ALS process
   births remain. Retain actual failures rather than treating a retry as the
   original result.
4. Send EOF, require normal client/ALS exit and verify exact owned-container
   cleanup. Do not remove unrelated containers or reuse evidence directories.

Use matched request IDs and the `at` timestamps in `mcp/protocol.jsonl` to
measure selection separately from semantic waiting. Identify first-run cache
effects; do not label these sessions as a machine-wide cold Docker cache.
Report all six sessions, ranges/medians for cold and warm selection, time to
confirmed semantic readiness, process births, source preservation and cleanup.
No fixed latency improvement is claimed in advance. A still-running index may
leave `indexing_complete=false`; this must preserve valid metadata and its live
selected client. Wrong-view/load failures remain failures. New findings need
maintainer assessment before release.

# Local Mac acceptance and optional selection timing

Status as of **2026-11-18**: RC4 publication precedes a separate clean local
Mac Codex/Arca functional acceptance test. The maintainer's
[RC4 release decision](../plans/release-0.2.0-rc.4.md) supersedes the previous
mandatory before-release larger-project benchmark. Cloud/Linux checks do not
establish Mac startup, native client lifecycle or indexing latency.

The functional test uses a fresh Arca checkout beside the abuild
checkout, outside its directory and ancestor discovery scope, and a new local
Codex chat opened only on Arca. First inventory and back up the maintainer's own
Ada plugin/skill/MCP entries, runtimes and bindings, then remove those installed
entries and active state so the chat cannot discover the build project's Ada
MCP. Preserve unrelated configuration and rollback data outside discovery.
Acquire the actually published RC4 normally, verify native agent tool discovery
and actual server identity, select Arca's real GPR/scenarios, compare native
source-query results with its source, and check disconnect/EOF cleanup. A
separate query-client batch alone is insufficient. This is planned acceptance,
not completed Mac support; SDK 2 work follows it.

## Optional later performance comparison

Project selection no longer waits for the former 25-second indexing gate, and
default exact-view repeats no longer reload or reset readiness. A 30-second
ALS RPC timeout and the 25-second guarded semantic wait remain. Index readiness
is a separate conservative snapshot, not a promise of instant semantic results.
No latency improvement is established by this structural change alone.

If performance investigation is needed after functional acceptance, use one
real larger GPR view on the actual Mac with unchanged source commit, ordered
project paths and scenario values. The following procedure is optional and
does not block RC4 publication.

Compare accepted artifacts for baseline `ced1076fb1e87df0bc73f4702d31160aa0c8cfde`
and the final candidate. Record each source SHA, tooling hash, immutable image
target, ALS/GNAT/Python versions, Mac architecture, Docker version/backend and
whether AMD64 emulation is active. Use separate private bindings/evidence;
preserve the installed runtime and global client/Docker settings.
Provision each binding through its checked CI image archive using explicit
`--archive` and `--archive-sha256`, preserving the exact candidate identity.

For each artifact, read its verified guide and actual tool catalog first. The
baseline lacks `refresh` and `indexing_complete`; record those as absent, not
false, and retain its documented selection behavior. Use explicit refresh only
for a candidate which advertises the Boolean parameter. Run three fresh MCP
sessions serially, retaining raw protocol and stderr with a 90-second request timeout.
In each session:

1. Select the exact GPR with `ada_project_info` once. Record elapsed request
   time, `complete`, `indexing_complete` and any actual error.
2. Query `ada_workspace_symbols` using a known unique project symbol and an
   absolute source anchor. Honor `complete` and `truncated`; allow at most
   three such requests to observe later readiness, without reselecting between
   them. Record elapsed time and compare the exact target with the source.
3. Repeat default project info once with the identical context. The candidate
   should observe current readiness without reloading; record default-repeat
   time separately from cold selection. If advertised, make one explicit
   `refresh: true` request and repeat the bounded semantic-readiness check.
   Record refresh time, membership and the same MCP/ALS process births. Label
   the baseline's older default-repeat behavior accurately; do not treat it as
   support for explicit refresh. Retain actual failures instead of replacing
   their results with retries.
4. Send EOF, require normal client/ALS exit and verify exact owned-container
   cleanup. Do not remove unrelated containers or reuse evidence directories.

Use matched request IDs and the `at` timestamps in `mcp/protocol.jsonl` to
measure selection separately from semantic waiting. Identify first-run cache
effects; do not label these sessions as a machine-wide cold Docker cache.
Report all six sessions, with separate cold-selection, default-repeat and
advertised explicit-refresh timings, plus time to confirmed semantic readiness,
process births, source preservation and cleanup.
No fixed latency improvement is claimed in advance. A still-running index may
leave `indexing_complete=false`; this must preserve valid metadata and its live
selected client. Wrong-view/load failures remain failures. Report new findings
for maintainer assessment without turning optional timings into a support claim.

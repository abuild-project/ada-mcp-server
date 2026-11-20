# Input validation contract

Base revision: `103bf4cdb9608317686f354e19eb505be49da929`.

## 2026-11-20: Preserve the installed SDK validation boundary

Decision: pin the observable input-validation contract of the locked MCP
SDK 1.30 before a future SDK 2 migration. Add tests and development
guidance; do not change runtime code, tool schemas, the refresh guard,
dependencies, locks, versions, changelog or CI workflows.

Decision: start the actual `python -m ada_mcp` stdio server and use raw
MCP initialization, catalog and tool requests. Eight small invalid cases
cover integer and Boolean types, required arguments, an enum and nested
collection types. Each must return one text input-validation error,
avoid an owned ALS startup sentinel and leave the same process answering
the next request. Controls cover valid input, an allowed extra property,
explicit false refresh and the existing unknown-tool error. Keep stdout
protocol-only checks.

Decision: extend the existing real-ALS sample integration check with one
raw invalid reference call, unchanged known Ada/GPR input hashes and one
valid extra-property call returning a normal result. Document the
currently shadowed handler refresh guard without changing it. SDK 2 must
reproduce server validation or receive an explicit contract decision.

Decision: independently test sensitivity by disabling only the call-tool
decorator's SDK validation in an owned untracked source copy. The
contract test must fail; preserve the accepted candidate unchanged. Host
checks are development evidence. A fresh detached tester runs the
complete exact-source AMD64 Trixie/GNAT 14/pinned-ALS chain and
independent review before the normal prepared-PR handoff. Only the
assigned developer edits the candidate; local and PR correction counters
start at zero for this new topic. No external push, PR, merge, tag,
release or publication is authorized.

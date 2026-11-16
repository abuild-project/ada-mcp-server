# Retire optional additional-tool exploration

The optional additional-tool observation scenario duplicated work now owned
by the required control. scripts/observe_additional.py now retains only the
same-path --serve-trace child entry and dispatches directly to the unchanged
shared tracer. The exploratory run_observation function and --output mode
are removed. Invalid CLI input exits before dispatch or writes; valid trace
dispatch adds no nonprotocol stdout.

Only the optional scenario's mocked runner fixture and 16 exclusive test
cases are retired. The existing shared hash, mutation, decoder and tracing
guards and strict required-control negative assertions remain. Two narrow
CLI tests cover retired-option rejection and unchanged trace dispatch. The
[dated plan](../plans/retire-exploration.md) lists every retired and added
case ID and accounts for the selected unit collection changing from 1,294
to 1,280. It supersedes only the earlier optional-retention decision;
published plans, records and evidence remain intact.

Development checks of this candidate based on
`faa98a122f0f5c0f84351c32c07cd5b287f471d3` pass 451 affected host tests,
Ruff/format, strict Mypy for the five additional-tool harness modules and
documentation validation. The new --output rejection case fails against
the original runner before it can create an output directory. These host
checks do not establish native acceptance; the managed AMD64 Trixie/GNAT 14/
pinned-ALS chain and immutable independent review remain required.

The required control, native oracles, shared support, fixture inputs,
product sources/tooling, pins, version, support scope and CI configuration
are unchanged. The required evidence still covers 53 calls with 50 accepted
and three blocked with semantic_acceptance=false, eight source states and
57 native request/result pairs plus shutdown, alongside the existing
reading, diagnostic, nonroot identity and cleanup checks. This internal
retirement adds no user-facing changelog entry.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

# Retire optional additional-tool exploration

Base revision: `faa98a122f0f5c0f84351c32c07cd5b287f471d3`.

## 2026-11-16: Approved optional-runner retirement

Decision: remove run_observation and the optional --output mode from
scripts/observe_additional.py. Retain that same file as a minimal
--serve-trace entry point dispatching to the unchanged
additional_support.observed_server, with protocol-only stdout. Reject the
retired option before dispatch or filesystem activity. This supersedes only
the optional-runner retention decision in the
[harness-maintenance plan](harness-maintenance.md); preserve that plan,
existing change records and historical evidence unchanged.

Decision: remove only scenario-exclusive tests and their mocked runner
fixture. Retain shared hashing, mutation, decoding and tracing guards and
all strict required-control negative assertions. Record the retired pytest
case IDs and replacement CLI cases so the lower unit count is explicit.
Use a small CLI regression check without a new framework or test matrix.

Decision: keep product src/, tooling/, additional_support.py, the required
real_additional.py control and native oracles, fixtures, pins, version,
support scope, .github/ and CHANGELOG.md byte-identical. The full native
basis remains 53 calls, 50 accepted and three blocked with
semantic_acceptance=false, eight states and 57 native request/result pairs
plus shutdown; reading remains 27 calls, diagnostics 2/0/2, both nonroot UID
checks and cleanup remain required. Update only the related development
documentation and the concise final-state change record/index. This
internal deletion needs no user-facing changelog entry.

Decision: only the assigned developer edits the candidate. Reuse the
existing development venv for modest affected host tests, Ruff/format,
strict Mypy and documentation checks; do not install packages or run a
native build. Host checks remain development evidence. Prepare one coherent
unpublished local commit above the base and freeze edits with a receipt for
the coordinator. The coordinator owns final commit transport, immutable
fresh-worktree testing, independent review, full managed CI and the checked
PR. Preserve the task's local and PR correction counters; no recursive
delegation, external writes, push, merge or release action is authorized.

## 2026-11-16: Unit-case accounting

Decision: retire the following 16 scenario-only cases, including each
parameterized case ID. The mocked optional-runner fixture also goes away;
none of the shared guard or strict required-control cases is retired.

In `tests/host/test_additional_observation.py`:

```text
test_existing_output_is_never_replaced
test_exploratory_template_and_restore_writes_use_the_shared_batch_guard
test_full_observation_allows_only_owned_compiler_products
test_full_observation_keeps_eof_failure
test_full_observation_keeps_semantic_failures_unaccepted
test_full_observation_records_changed_process_birth_before_failure[als_pid]
test_full_observation_records_changed_process_birth_before_failure[als_start_ticks]
test_full_observation_records_changed_process_birth_before_failure[mcp_pid]
test_full_observation_records_changed_process_birth_before_failure[mcp_start_ticks]
test_full_observation_rejects_and_preserves_unexpected_changes[additional.gpr]
test_full_observation_rejects_and_preserves_unexpected_changes[manifest/alire.toml]
test_full_observation_rejects_and_preserves_unexpected_changes[src/main.adb]
test_full_observation_rejects_and_preserves_unexpected_changes[states/main-after.adb]
test_full_observation_rejects_and_preserves_unexpected_changes[stray.o]
test_full_observation_rejects_original_fixture_change
```

In `tests/host/test_additional_inspection.py`:

```text
test_exploratory_runner_propagates_real_scan_failure
```

Decision: add these two CLI cases in
`tests/host/test_additional_observation.py`:

```text
test_trace_cli_dispatches_without_nonprotocol_stdout
test_trace_cli_rejects_retired_output_before_dispatch_or_write
```

The selected nonintegration collection therefore changes from 1,294 to
1,280 cases: 1,294 minus 16 retired cases plus two CLI cases. One integration
case remains deselected in each collection. All 26 existing shared cases
in test_additional_observation.py remain under their original IDs; the six
shared/strict inspection cases remain, including actual nonroot scan errors.
The whole-batch mutation guard and the required control's native corruption,
missing-pair, input-change, process-birth and lifecycle negative assertions
remain unchanged in their existing modules. This count change does not
reduce or replace any required native proof.

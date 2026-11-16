# Parameter selection result contract

Signature help returned a malformed selected native activeParameter directly
in public active_parameter, including null, booleans, negative integers and
values outside the LSP unsigned integer domain. Consumers could receive an
unusable parameter index even though malformed signature selection already
had an effective zero fallback and labeled evidence.

Nonempty replies now return exact integer zero for a malformed parameter
index actually selected by the existing presence-based precedence. A separate
conditional parameter_selection_diagnostic preserves the exact raw value
and its type, with reason malformed-active-parameter, source
selected-signature or top-level, and fallback zero. It can coexist with the
unchanged selection_diagnostic for a malformed signature index. A malformed
present selected-signature parameter still overrides a valid top-level
parameter; conversion never hides it by switching sources.

Missing values default to zero without a diagnostic. Valid indices, explicit
selected-signature zero, top-level fallback, domain-valid per-signature
out-of-range values and empty/missing-parameter-list defaults retain their
behavior. An unused malformed top-level or other-signature value adds no
public parameter diagnostic. Explicit null is malformed. Empty signature
replies retain their negative shape and native request errors retain the
existing failure path. The [approved plan](../plans/parameter-selection-contract.md)
supersedes only the previous malformed public-parameter behavior.

The updated regressions reject the original handler at base
`e73e5dae0cc9538fe7d2c992a00746e18bb302ec`: malformed selected values
remain raw and simultaneous diagnostics are absent. Existing cases cover
raw types, selected-signature precedence, unused malformed fields and the
unsigned-domain boundary. The actual server-dispatch check requires both
independent diagnostics and exact raw Boolean/null types in the JSON payload.
Focused development checks pass 298 affected handler, dispatch and existing
native-oracle control tests, Ruff/format, strict Mypy and documentation
validation. These reused-image checks do not establish native acceptance;
complete exact-source container validation and independent review remain
required.

The native oracle continues to reject every malformed raw field, including
unused fields, before defaults or classification. Safe public fallback does
not promote malformed native data into accepted evidence. The three known
positional signature cases remain blocked and unaccepted. Native requests,
the integration harness, fixtures, dependency pins, version and support scope
are unchanged.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

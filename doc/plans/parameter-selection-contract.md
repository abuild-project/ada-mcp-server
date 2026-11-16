# Parameter selection result contract

Base revision: `e73e5dae0cc9538fe7d2c992a00746e18bb302ec`.

## 2026-11-16: Approved parameter result contract

Decision: the maintainer approved treating malformed active-parameter results
analogously to malformed active-signature results. For nonempty signature
replies, a malformed parameter index actually selected by the existing
presence-based precedence becomes exact integer zero in public
active_parameter and adds this separate conditional field:

```json
{
  "parameter_selection_diagnostic": {
    "reason": "malformed-active-parameter",
    "raw_active_parameter": null,
    "source": "selected-signature",
    "fallback": "zero"
  }
}
```

Decision: source is selected-signature when that signature contains
activeParameter, otherwise top-level. Preserve the exact malformed raw
value and its JSON type. Valid raw indices are exact integers in
0..2147483647, excluding booleans. Explicit null, negatives, oversized
integers and other nonintegers are malformed. Missing values default to
zero without a diagnostic. The selected signature's present value,
including zero or malformed null, still overrides the top-level value.
Do not add a parameter diagnostic for an unused malformed raw field.

Decision: retain selection_diagnostic unchanged and independently when
both selected indices are malformed. The zero fallback also applies to
malformed selected parameters with empty or missing parameter lists.
Domain-valid selected-signature out-of-range values remain unchanged;
the existing nonempty-list top-level out-of-range default remains zero,
without a diagnostic. Empty/no-signatures replies retain their negative
shape. Native request failures still propagate through the existing error
path. This supersedes only the raw malformed public-parameter behavior
preserved by the earlier [signature plan](signature-selection-contract.md).

Decision: retain the independent native oracle's strict rejection of
every malformed raw index, including unused fields, before classification.
Do not alter native requests, fixtures, the three unaccepted positional
signature blockers, the native harness, dependency pins, version or support
scope. A safe public fallback is not native semantic acceptance.

Decision: adapt existing handler regressions, unsigned-domain and default
controls, and one real server-dispatch envelope check for simultaneous
diagnostics. Retain a failing reproduction against the unchanged base.
Update current development/assessment policy, the user changelog and a
concise record with sorted index entry; preserve earlier plans/records.
Host or reused-image checks are development evidence. Complete exact-source
container validation, fresh detached testing and independent review remain
required. Only the assigned developer edits candidates; no external writes,
publication, merge or release are part of this implementation work.

## 2026-11-16: Completed implementation validation

Decision: record the completed implementation checks at revision
`1f0621446d95abc63d1875d559c9b797f4efc7de`. The tester used a fresh
detached worktree and the exact-source image target
`sha256:74e6e600020996ac860f907e72575ed3b923caf1d933422c66c86215f4e1f1d8`.
The committed source archive has SHA256
`a51e9e486985dbaffb54840ad4ebc4864c81301250781b97f1abcd4c1ef39f03`.
The complete docker/build and docker/check chain passed: 1,289 selected
unit tests, one integration deselection, no skips, Ruff/format, strict
Mypy, distributions/Twine, documentation, completed-check provenance and
the real pinned-ALS/MCP probes. Reading and diagnostic controls passed;
additional controls retained exactly the three known unaccepted positional
cases with semantic_acceptance=false, unchanged native defect descriptors,
complete raw traces, source guards, stable process births and cleanup.

Decision: retain the original base counterexample and the tester's six
independent contract controls, including actual MCP serialization of both
diagnostics, exact raw types and unchanged native-oracle rejection of
malformed fields. These supplied-ALS-reply controls establish conversion
behavior, separately from the real native chain. No malformed native value
gains semantic acceptance, and no new host/artifact-identity or macOS proof
is claimed. Earlier plans, records, refs and primary evidence remain intact.

Decision: complete the record using this identified tested revision.
The documentation-only completion still requires exact-head validation
and independent review before the coordinator's PR handoff. Do not claim
that future validation has already passed; stop before merge or release.

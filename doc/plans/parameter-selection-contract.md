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

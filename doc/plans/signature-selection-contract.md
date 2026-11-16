# Signature selection result contract

Base revision: `c0eaf2b3fb8b85fa6323de8e87d82d7a46d344ff`.

## 2026-11-16: Approved result contract

Decision: the maintainer approved returning the effective selected signature
index as `active_signature` for nonempty signature results. A present malformed
native `activeSignature` selects the first signature and adds only this
conditional field:

```json
{
  "selection_diagnostic": {
    "reason": "malformed-active-signature",
    "raw_active_signature": -1,
    "fallback": "first-signature"
  }
}
```

Decision: retain the exact malformed raw value in that diagnostic. Valid raw
indices have exact integer type in 0..2147483647, excluding booleans. Negative,
oversized and noninteger values, including explicit null, are malformed.
Missing and domain-valid out-of-range indices still select zero without a
diagnostic. Empty/no-signatures results retain the existing negative shape.
This narrowly supersedes the earlier requirement to expose malformed
`activeSignature` directly in public `active_signature`; public diagnosis is
preserved by the labeled diagnostic instead.

Decision: preserve parameter behavior, selected-signature precedence including
explicit zero, top-level fallback/defaults and malformed parameter evidence.
The independent oracle must still reject every malformed raw native index
before defaults or classification, including unused fields. Keep all three
native positional signature cases blocked with their exact raw envelopes,
coordinates and unaccepted classification. Do not change native requests,
the 53-call harness, SDK/ALS pins, version, support scope or unrelated code.

Decision: update the small existing handler regressions and retain valid,
missing, out-of-range and negative controls. Use two signatures with different
active parameters to reject mixed raw/effective results and accidental Python
indexing. Preserve a failing reproduction of the approved contract against
the unchanged base. Add one focused server-envelope check if needed to verify
the conditional diagnostic survives serialization. Update current policy
documentation, the user changelog and a concise final-state topic record.

Decision: only the assigned developer edits candidates. Continue this topic
without resetting earlier packages' counters or evidence. The developer runs
modest focused host tests and quality checks, then freezes one coherent initial
commit directly above the accepted base. The coordinator arranges the required
exact-source managed container chain, fresh detached testing and independent
review. Host mocks are development evidence, not native acceptance. The
developer performs no external writes, recursive delegation, publication,
merge or release actions.

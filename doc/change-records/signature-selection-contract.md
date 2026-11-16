# Signature selection result contract

For a malformed native `activeSignature`, signature help safely read the first
signature's parameter but returned the malformed raw signature index. The two
public fields therefore described different selections.

Nonempty replies now return the effective zero-based `active_signature` used
for parameter selection. A malformed native index selects the first signature
and adds `selection_diagnostic` with reason `malformed-active-signature`, its
exact `raw_active_signature` and fallback `first-signature`. This preserves
public diagnostic evidence without presenting it as the selected index.
Booleans, explicit null, negative integers, integers above 2147483647 and
other nonintegers are malformed.

Valid selections, missing and domain-valid out-of-range defaults add no
diagnostic. Empty replies retain the existing negative shape. Parameter
precedence and malformed-parameter policies are unchanged. The approved
[contract decision](../plans/signature-selection-contract.md) supersedes only
the previous public raw-signature field semantics. No dependency, version,
support, native request or integration-harness change is included.

At base `c0eaf2b3fb8b85fa6323de8e87d82d7a46d344ff`, the updated regressions
reject the mixed selection and absent diagnostic while preserving valid
controls. Focused host checks pass for the exact two-signature result, raw-value
types, unsigned-integer boundaries and JSON serialization through actual
server dispatch. The independent raw-index rejection and original native
blocker controls remain in place. Host checks are development evidence;
exact-source managed container checks and independent acceptance remain
required. The three known native positional signature cases remain blocked
and unaccepted.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

# Additional-tool regression boundaries

The ten tools outside the reading baseline remain in development under the
[support matrix](../support.md). Their catalog entries are not support claims.
The bounded fixture checks use exact source expectations and preserve native
requests/replies, MCP results, source states, hashes and process cleanup.

| Tool | Bounded checks | Boundary |
| --- | --- | --- |
| Call hierarchy | Exact incoming/outgoing sets, native call sites, unrelated-name exclusion, leaf/comment negatives, removed and moved edge | Synchronizes the queried file; other changed open files need explicit synchronization |
| Dependency graph | Exact ordinary with-clause edges/counts, actual generic unit ownership, changed import, missing path, comment/string/character-literal masking | Skips generic formals/access profiles; a bounded text parser without complete Ada or limited/private-with coverage |
| Completions | Exact controlled qualified members, signatures and insertions, limit and comment cases, renamed members | Native completeness is distinct from the tool's requested result limit |
| Signature help | Exact declaration/formal order, named association selection, changed types/arity and comment case | Three native positional selections remain blocked below |
| Code actions | Known named-parameter proposal and exact summary/native command arguments, trigger removal and comment cases | Discovery only; summary API omits native edits/command arguments and executes none |
| Rename preview | Exact local and three-file edit sets, changed locations/counts, invalid/comment negatives | Preview/default returns proposals; application is unsupported and preview=false is rejected |
| Formatting | Bounded nonoverlapping edits reconstruct fixed formatted bytes; already-formatted native null | Returns edits; explicit writes occur only in the fresh test fixture |
| Spec selection | Exact body-to-declaration target, separate sibling fallback and no-sibling negative | File fallback is a 1:1 file-level result, not semantic navigation |
| Build | Real owned GPRbuild success/executable and deliberate source-bound compiler errors | Outputs confined to explicitly owned obj/bin; no consumer build support promotion |
| Alire information | Every exposed TOML field, changed metadata and missing/malformed negatives | Manifest metadata only, without an Alire toolchain/dependency workflow |

## Native positional signature defect

These exact cases use zero-based indices into the signature's ordered formal
array. The second actual must select Right, and the third must select Extra.

| Fixture state and public cursor | Expected correct index | Observed native/MCP index | Status |
| --- | --- | --- | --- |
| Initial Main 5:33, second actual | 1 | 0 | Blocked, unaccepted |
| Changed Main 7:31, second actual | 1 | 0 | Blocked, unaccepted |
| Changed Main 7:34, third actual | 2 | 1 | Blocked, unaccepted |

The initial managed observation used exact source revision
`0950488ebbdc9710d59c5a5ed28b288d4ba00deb` and retained unchanged native
initialize negotiation and signature requests. MCP sent the correct
public-minus-one LSP coordinates. The native reply already contained the
wrong index. The pinned ALS source at
[commit 4a2d3d5](https://github.com/AdaCore/ada_language_server/blob/4a2d3d5e67bb52160d9fc17fbc52d3293274469a/source/ada/lsp-ada_completions-generic_assoc.adb#L837)
counts unnamed actuals then decrements a positive cursor position. This
explains the observed discrepancy; no upstream implementation is imported.

The strict runner fails these results. CI's explicit assessment option
recognizes only these three label/state/path/cursor combinations and their
exact original raw defect envelope: both explicit native parameter fields
carry the same wrong value, with the original selected signature and raw
declaration/formal fields. Missing or changed raw fields cannot borrow that
exception. General signature conversion uses the selected signature's
`activeParameter` when present, including zero, before the top-level/default
fallback. Valid differing native fields can pass through normal effective
selection. Documented valid out-of-range signature/top-level indices use
zero. Public `active_signature` is the effective selected index. A present
malformed native `activeSignature` selects zero and adds `selection_diagnostic`
with reason `malformed-active-signature`, the exact `raw_active_signature` and
fallback `first-signature`. Missing and valid out-of-range indices add no
diagnostic; empty replies keep the existing negative shape. Malformed parameter
indices retain their existing public evidence. Malformed raw indices remain
unaccepted, and per-signature out-of-range selection is not silently clamped
or accepted. The raw integer domain is 0..2147483647, excluding booleans.
Validate top-level and all per-signature fields, including unused signatures
and missing/empty parameter lists, before precedence or defaults. An invalid
unused top-level field
cannot replace a valid per-signature selection or gain acceptance. The oracle
independently checks that effective selection and unchanged request/cursor,
without importing the production conversion helper. A correct effective native
index paired with a wrong MCP index fails, and a wrong native index cannot
be hidden by a semantically correct MCP value. Each known
case retains its correct expectation and wrong observation with
`accepted=false` and `semantic_acceptance=false`; the overall status is
`assessed-with-native-blocker`. Other mismatches fail the chain. This does
not repair ALS or accept positional selection. Named association checks
provide separate evidence while preserving the positional limitation.

## Native application

`ada_rename_symbol preview=false` returns an explicit unsupported-application
failure with no proposed changes and `applied=false`. The rename handler
rejects that mode before source synchronization or native prepare/rename
requests; the server's shared ALS connection setup is unchanged. Preview
and the handler's default return native proposals without applying them.
No writer is implemented. The shipped read-only client continues to require
explicit preview=true and rejects false, absent and nonboolean preview values,
as well as formatting and build calls.

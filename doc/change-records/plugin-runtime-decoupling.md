# Independent entry and runtime selection

A version-pinned skill/plugin previously needed replacement for each runtime
upgrade, even when its workflow and permissions were unchanged. Add an explicit
compatible runtime/binding selection so the full/local and lightweight entries
can remain installed while using another exact verified pair. Entry package
version and actual runtime version remain separate.

Generated release tooling metadata and runtime manifests declare workflow
contract 1. The entry accepts only that exact integer contract; absent/unknown
contracts require a compatible entry update before activation. Published
RC1/RC2 stay immutable legacy packages and gain no selection support retroactively.
The feature and future compatible artifacts remain unreleased.

The existing trusted acquirer gains read-only selection inspection and explicit
activation, preserving its original acquisition interface. It checks private
bounded records, manifest/source hashes and binding pins before source-only
helper validation. Bounded inputs use one non-following, nonblocking read-only
descriptor; its type, owner, mode and size are checked before consuming bytes
from that same descriptor. A record path swap cannot substitute unchecked pins.
Malformed nested OCI binding metadata returns structured invalid JSON without
changing the active pair or creating a backup. Initial writes refuse replacement;
switches require the
expected old record hash and a new backup, preserving operational rollback.
Discovery checks explicit selection, environment, then user-local state without
writing on reads. No automatic installer or global client configuration is added.

Both entry forms share the same discovery, compatibility, bootstrap and approved
update instructions. New sessions can select the recorded runtime only when
its files and locator are available there. A custom path must be supplied again
or explicitly retained through supported host/provider configuration; activation
does not write that configuration or a persistent pointer. Otherwise report
session-only use and the necessary locator/bootstrap action. Fresh Cloud
sessions with absent state follow real verified
release bootstrap without assuming persistence. Compatible runtime updates keep
the entry unchanged; instruction/permission/compatibility changes use the guarded
entry-update flow. Native clients still need their own explicit configuration,
reconnect and actual version/query checks. Support scope is unchanged.

Targeted development validation covers unchanged-entry version switching and
rollback, legacy/incompatible contracts, source/pin/binding corruption, ignored bytecode,
no-clobber/expected-state guards, write failures and generated entry invocation.
Fresh-process controls show that a custom selection is absent from an unrelated
private default HOME, while an explicitly supplied or next-process environment
locator recovers the exact pair without changing the entry or default state.
That process fixture does not claim provider or Cloud persistence. Deterministic
record-swap controls reject symlink and permission-changing substitutions before
helper execution, check descriptor ownership/size/type and closure without
privileged chown, and retain bounded reads when file size changes. Actual CLI
controls for malformed OCI descriptor platforms preserve old selection and
return invalid JSON. The original entrypoint executes the harmless swapped-record
helper and emits a traceback for that malformed binding; the corrected controls
reject both behaviors.
Ruff/format, strict Mypy, documentation/examples and whitespace checks passed.
The generated-artifact acceptance now includes selection activation/readback
after the existing real Doctor and source queries for both Linux identities.
Targeted host checks are development evidence; complete exact-source Trixie
CI and post-publication release-to-release consumer tests remain separate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

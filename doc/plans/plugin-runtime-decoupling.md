# Entry and runtime separation

Base revision: `5448ee1eeedb76723d2c726e4d19535743f2b437`.

## 2026-11-14: Compatible runtime selection

The maintainer approved a long-lived full/local skill and lightweight plugin
entry that can use later compatible exact runtimes without replacing/uploading
the entry for every server release. Distinguish entry package version from
actual MCP runtime version. Update the entry itself for its own instructions,
permissions or compatibility changes, preserving private identity/audience.

Use integer workflow contract 1, separate from SemVer, in authenticated release
tooling metadata and the runtime manifest. Both must agree with the entry's
supported contract. Missing, boolean and unknown values fail before activation;
legacy RC1/RC2 packages have no contract and remain unchanged. This feature
stays unreleased until a separate accepted version package is published.

Reuse the existing trusted stdlib acquirer for read-only selection inspection
and explicit activation. Discovery is an explicit path, ADA_MCP_SELECTION, then
a user-local default, with no read-time writes. Private records pin the exact
runtime manifest, binding bytes and version/source/image identity. Check bounded
inputs and source hashes before captured helper execution; reuse the existing
binding parser without unchecked imports or bytecode. Preserve binding-v2 and
all immutable source/image/acquisition checks.

Initial activation is no-clobber. Replacement requires the expected current
record hash and a new backup, with a cooperative private lock and atomic record
switch. Keep old runtime/image/binding and record for validated rollback. No
implicit download, global client configuration, background service or updater
is added. Native clients still need an explicit supported switch/reconnect.

Full and lightweight entries share one canonical discovery/update workflow.
A later chat resolves selection before fallback pins; fresh Cloud sessions with
absent files perform verified published-release bootstrap after consent rather
than assuming persistence. Unknown compatibility or unavailable persistence/tools
must be reported accurately. Keep the existing fresh checks, notice consent,
provider waits, read-only query policy and Mac/client acceptance boundaries.

Validate unchanged-entry switching across controlled versions, legacy/unknown
contracts, pin/source/binding corruption, bytecode, expected-state backups and
rollback. Exercise the actual generated acquirer/selection commands after real
Doctor/source queries in the existing two-identity artifact acceptance. Controlled
fixtures are not a published RC2-to-RC3 update; that remains a later consumer
test after a justified separately reviewed release. Full exact-source AMD64
Trixie CI and independent review remain acceptance requirements.

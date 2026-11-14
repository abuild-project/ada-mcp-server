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
helper validation. Initial writes refuse replacement; switches require the
expected old record hash and a new backup, preserving operational rollback.
Discovery checks explicit selection, environment, then user-local state without
writing on reads. No automatic installer or global client configuration is added.

Both entry forms share the same discovery, compatibility, bootstrap and approved
update instructions. New sessions select the recorded runtime instead of stale
embedded pins. Fresh Cloud sessions with absent state follow real verified
release bootstrap without assuming persistence. Compatible runtime updates keep
the entry unchanged; instruction/permission/compatibility changes use the guarded
entry-update flow. Native clients still need their own explicit configuration,
reconnect and actual version/query checks. Support scope is unchanged.

Targeted development validation passed 108 cases covering unchanged-entry
version switching and rollback,
legacy/incompatible contracts, source/pin/binding corruption, ignored bytecode,
no-clobber/expected-state guards, write failures and generated entry invocation.
Ruff/format, strict Mypy, documentation/examples and whitespace checks passed.
The generated-artifact acceptance now includes selection activation/readback
after the existing real Doctor and source queries for both Linux identities.
Targeted host checks are development evidence; complete exact-source Trixie
CI and post-publication release-to-release consumer tests remain separate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

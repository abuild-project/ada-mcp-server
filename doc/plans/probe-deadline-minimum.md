# Minimum host Python probe deadline

Base revision: `77c934f71c836c6f0e0741e5be5c34c77ac1a8f5`.

## 2026-11-20: Preserve the full two-second probe budget

The maintainer authorized this narrow follow-up because Bash's whole-second
`SECONDS` deadline can terminate the documented two-second Python version
probe early. Replace that deadline with twenty completed foreground sleeps
of 0.1 seconds, checking for an exited probe between sleeps. Preserve Bash
3.2 compatibility, selected-process kill/reap, private-output cleanup, normal
fail-open behavior and strict offline `--check`; keep all version parsing,
minimum-version and update-policy behavior unchanged.

Strengthen the existing normal/check hanging-probe test with an opt-in delay
in fake Docker's platform inspection and flushed monotonic heartbeats from
the fake interpreter. Require at least 1.9 seconds of observed probe lifetime
and retain the independent four-second launcher bound and existing cleanup
and protocol assertions. Retain an owned-copy failure against the unchanged
base launcher and candidate success, including raw timestamps outside source.

Add the short final-state change record and sorted index entry. The documented
two-second contract does not change, so no changelog or user-guide edit is
needed. The assigned developer alone edits the isolated topic; the assigned
tester and independent reviewer assess its immutable candidate. Focused host,
style, Bash and documentation checks precede the coordinator's canonical
hosted AMD64 Trixie/GNAT 14/pinned-ALS chain. No local Docker, public release,
Mac acceptance claim, external write or change to the existing topic is in
scope. This follow-up starts its own local 0/3 and later PR 0/3 counters;
the earlier topic's counters and history remain preserved.

## 2026-11-20: Coordinator delivery scope

The external-write restriction above applies to the developer role. The
coordinator's authorized checked-PR workflow includes pushing this immutable
candidate for exact-head hosted CI and opening its narrow stacked follow-up
PR. It authorizes no merge, release or change to the earlier PR.

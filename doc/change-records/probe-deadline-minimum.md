# Minimum Python probe deadline

Bash's whole-second `SECONDS` comparison could terminate the documented
two-second host Python version probe early. The launcher now waits for twenty
completed foreground sleeps of 0.1 seconds before killing a hanging probe,
and still exits early when the probe completes. Selected-process kill/reap,
private-output cleanup, Bash 3.2 compatibility, normal advisory fallback and
strict offline `--check` behavior are preserved. Version parsing, Python 3.11
minimum and update-policy logic are unchanged.

The existing hanging-probe regression records flushed monotonic heartbeats
and aligns fake Docker's platform-inspection return to a fractional wall-clock
phase. Both normal and check modes require at least 1.9 seconds of observed
probe lifetime, retain the independent four-second launcher bound and verify
process absence, output cleanup and protocol behavior. The strengthened test
fails its lifetime assertion against the unchanged launcher at base revision
`77c934f71c836c6f0e0741e5be5c34c77ac1a8f5` and passes with this fix.
Focused host tests, Ruff, Bash syntax and maintained documentation checks
pass. Exact-head canonical hosted validation and independent acceptance are
recorded separately; these host checks do not replace that chain.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

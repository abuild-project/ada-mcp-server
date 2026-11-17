# Routine update documentation

The plan exception is now defined once in
[AGENTS](../../AGENTS.md#dependency-update-plans). Dependency roles follow
the direct input files, and required lock alignment inherits the update's
eligibility. The development guide links to that rule. Short records still
carry the durable rationale; existing size guidance is preserved.

The PR description remains the record verbatim; later head validation goes
in a short PR comment. Operational counters and attempt logs stay outside
tracked source. Tester/reviewer roles, complete CI and actual installed-version
evidence requirements are unchanged.

At prepared revision `cc5f5122a39b69ccd2cbf122f1096dc55f4213fc`,
existing documentation checks and their regressions passed in a retained
container with an explicit DEV snapshot. These are developer documentation
checks; final-head acceptance remains separate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

# Routine update documentation

Routine dependency patch updates and lock-only alignment to approved input
pins may now omit a separate plan. All other changes retain dated topic
plans. A short record with durable rationale remains required; a few
sentences suffice for those routine cases. Existing size guidance is
preserved.

The PR description remains the record verbatim; later head validation goes
in a short PR comment. Operational counters and attempt logs stay outside
tracked source. Tester/reviewer roles, complete CI and actual installed-version
evidence requirements are unchanged.

At prepared revision `094882894687044bf84fff83cd43e4984000e46b`,
existing documentation checks and their regressions passed in a retained
container with an explicit DEV snapshot. These are developer documentation
checks; final-head acceptance remains separate.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

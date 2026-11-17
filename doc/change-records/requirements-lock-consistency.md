# Requirements input and lock consistency

An input-only dependency update could pass CI while the container still
installed the previous version from development.lock. The Ruff mismatch
between input 0.17.5 and locked 0.17.4 demonstrated this gap.

The CI entrypoint now checks input/lock consistency before lint and tests.
A stdlib checker follows relative -r includes, including runtime.in,
normalizes package names and compares every declared exact version with
the lock. Missing or different pins produce stderr diagnostics and failure.
Conflicting declarations, include cycles and unsupported relevant lines
also fail; generated hash continuations and transitive lock packages are
accepted. The [development guide](../development.md) describes the narrow
format and validation boundary.

At prepared revision `9fa9320acd02c63093a94ba88e8e6a3dfbf0259e`,
15 focused guard, CI and documentation tests passed, alongside Ruff/format,
strict typing, shell syntax and the current repository lock. The early-failure
counterexample fails against the original CI entrypoint, which reaches lint
despite drift. These retained-image developer checks are separate from
canonical container and independent-review evidence at the reviewed head.

The existing ALS assessment and support notes also link their upstream
signature report while retaining every acceptance restriction. Dependency
pins, runtime behavior, pyproject and AGENTS are unchanged.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

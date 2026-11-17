# Ruff hash lock update

The development input requested Ruff 0.17.5 while the hash lock still
selected 0.17.4. The canonical container installs that lock, so successful
checks of the input-only update exercised the previous Ruff version.

The lock now pins Ruff 0.17.5 with its release artifact hashes. All other
67 package pins and hash sets are preserved, including runtime dependencies.
The original dependency commit and accepted main history are retained
through a normal merge.

At prepared revision `babe7ba8b1072d6a352bbdb59f653957f8cd48df`,
uv regenerated the lock for CPython 3.13/LinuxAMD64. All 18 Ruff hashes
matched the versioned release index, and the selected wheel was verified
before installation. Actual Ruff 0.17.5 passed repository lint and format
checks; documentation validation passed. These focused developer checks
are separate from canonical container and independent-review acceptance
at the reviewed head.

This update changes development tooling, without changing server behavior
or the CI workflow. The [plan](../plans/pip-main-ruff-0.17.5.md) records the
targeted regeneration procedure.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

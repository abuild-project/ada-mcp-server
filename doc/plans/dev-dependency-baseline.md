# Development dependency baseline

Base revision: `888f3879cd0578335bfc5d7e224cabe3cbf40f63`.

## 2026-11-17: Approved metadata alignment

Raise only the optional dev floors for Ruff to 0.17.5 and pytest-asyncio to
1.5.0. This manual package-metadata change needs a plan, outside the
Dependabot exception. Preserve the other dev floors, runtime dependencies,
input pins, locks and CI. Distinguish the checked hash-locked baseline from
the open ranges installed by .[dev]. Check retained tool Requires-Python
metadata, built wheel/sdist requirements and unchanged runtime payloads.
Use existing focused documentation/packaging checks without an unlocked
extra install or version matrix. Add one concise changelog entry and
record; final canonical acceptance remains separate.

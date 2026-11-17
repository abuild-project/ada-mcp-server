# pytest-asyncio hash lock update

The development input requested pytest-asyncio 1.5.0 while the hash lock
still selected 1.4.1.post1. Because the canonical container installs the
lock, successful checks of the input-only update used the previous plugin.

The lock now pins pytest-asyncio 1.5.0 and its release artifact hashes.
All other 67 package pins and hash sets are preserved. The original bot
commit and accepted main history are retained through a normal merge.

At prepared revision `2dceea2f94c7d5e2928ea0d61e1b2cd6f4b55c7c`,
uv regenerated the lock for CPython 3.13/LinuxAMD64. Both new hashes
matched the versioned release index and the selected wheel was verified
before installation. A private, fully hash-verified environment imported
pytest-asyncio 1.5.0 with pytest 9.2.0; all 43 focused ALS client, pool and
server tests passed, as did documentation validation. These host developer
checks are separate from canonical container and independent-review
acceptance at the reviewed head.

This changes the async testing plugin without changing server behavior or
the CI workflow. The [plan](../plans/pip-main-pytest-asyncio-1.5.0.md) records
the targeted regeneration procedure.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

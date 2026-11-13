# Hatchling input and installed backend alignment

The backend input requests Hatchling 1.33.0, while the unchanged hash lock
still installs 1.29.0. The original green CI therefore does not test builds
with the requested backend.

Regenerate the single hash lock for Hatchling 1.33.0 and add its required
tomlkit 0.15.2 dependency. Retain every other package version and hash set.
The source version and public dependency ranges are unchanged.

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388432266),
but its build log installed Hatchling 1.29.0. Local preparation verifies
input/lock agreement and hash structure. The corrected merged revision
requires real wheel/sdist builds, Twine checks, coordinated
version/payload/provenance validation, complete Trixie checks and
independent review.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

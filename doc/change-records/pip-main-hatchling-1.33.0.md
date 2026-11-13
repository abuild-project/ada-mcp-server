# Hatchling input and installed backend alignment

The backend input requests Hatchling 1.33.0, while the unchanged hash lock
still installs 1.29.0. The original green CI therefore does not test builds
with the requested backend.

Regenerate the single hash lock for Hatchling 1.33.0 and add its required
tomlkit 0.15.2 dependency. Retain every other package version and hash set.
The source version and public dependency ranges are unchanged.

Newer Hatchling preserves the version provider's original spelling in core
metadata while normalizing distribution filenames. Reading the raw SemVer
literal therefore gives the files a Python-normalized name but leaves the
metadata with the SemVer prerelease spelling, which the existing provenance
receipt correctly rejects. Use Hatchling's builtin code version source to
evaluate the Python form from the same dependency-free canonical VERSION.
Both wheel and sdist metadata then use the promised Python version. No extra
version constant, plugin dependency or relaxed receipt check is introduced.

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388432266),
but its build log installed Hatchling 1.29.0. A later real Hatchling 1.33.0
build exposed the raw metadata spelling despite passing unit tests and
Twine; the unchanged provenance check rejected those distributions. Local
preparation verifies input/lock agreement and hash structure. The corrected
revision requires actual wheel/sdist metadata and payload checks, Twine,
coordinated version/provenance validation, complete Trixie checks and
independent review.

The actual failed wheel/sdist pair remains rejected by the unchanged receipt
helper. A private, hash-pinned Hatchling 1.33.0 build produced metadata 2.5
with Python Version 0.2.0rc1 in both distributions; the same helper and the
committed server-payload comparison accepted those bytes. This developer
metadata check does not replace the final Trixie receipt and host acceptance.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

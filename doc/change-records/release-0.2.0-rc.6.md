# RC6 prerelease preparation

Prepare `0.2.0-rc.6` (Python/MCP `0.2.0rc6`) from accepted main
`8cc6a8a87ce23894aae48a83386c623c953a3aba`. RC6 packages the pinned host
Python in native Codex fragments, explicit update policy, strict offline
validation, fail-open advisories and the full two-second version probe budget.
The release notes and setup guides distinguish local Mac/Codex configuration
from private Managed Cloud plugin activation and Docker-backed queries.

The release delta updates the canonical version, changelog and maintained
documentation. RC6 acquisition requires actual publication and authenticated
new pins; the existing checked RC5 acquirer can acquire the compatible RC6
runtime. The published RC5 PATH procedure remains available. The locked MCP
SDK 1.30.0, ALS/GNAT pins, 19-tool catalog and workflow contract 1 carry forward.

The [dated plan](../plans/release-0.2.0-rc.6.md) covers promotion from complete
CI at the exact merged-main source, then installation and verification of the
updated existing private plugin. Focused development checks passed for
maintained links, example syntax, sorted index, version and requirements pins,
plus documentation, packaging and release-note contract tests. Complete hosted
CI and independent review provide the remaining source evidence. Actual Mac
source and published consumer checks remain pending.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

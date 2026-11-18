# RC4 prerelease preparation

Prepare canonical `0.2.0-rc.4` and Python/MCP `0.2.0rc4` for the accepted
changes since RC3. Move Unreleased user changes into RC4 and add reviewed,
version-specific notes covering project-view retention/refresh, bootstrap
transport/aliases and bounded reading-tool fixes. Preserve RC1–RC3 history,
immutable fallback pins, MCP 1.30.0, pinned ALS/GNAT, workflow contract 1 and
the 19-tool catalog. No runtime behavior or installer changes are added here.

Current release, setup, install, update and support guidance requires actual
publication and verified target metadata before acquisition. Promotion retains
the existing workflow and uses the exact successful merged-main push CI's
tested artifacts and source-bound notes without rebuilding. The historical
public RC2-to-RC3 consumer workflow remains unchanged.

The dated release plan records publication before a clean local Mac Codex/Arca
test and defers SDK 2 until afterward. The timing assessment now treats a
larger-project benchmark as optional later work. Planned functional acceptance
requires owned-state inventory/backup/removal, a sibling Arca checkout, a new
Arca-only local chat and actual native agent discovery/source queries. Native
installation/lifecycle support remains in development pending that evidence.

Development checks of this package based on
`f69fbba0eb68e004896d75097befd931b8d19950` passed maintained documentation,
example syntax, sorted index, requirements and whitespace checks. A small
synthetic OCI fixture verified RC4 propagation into authenticated tooling,
runtime and lightweight metadata, contract 1, 19 tools and the preserved
project-selection instructions. These host checks do not establish image,
native client or publication acceptance; complete exact-head hosted Trixie CI
and independent review remain required. The same three pinned-ALS positional
signature cases remain unaccepted; the remaining RPC/semantic guards are
documented explicitly.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

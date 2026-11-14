# RC3 prerelease and public notification check

Prepare coordinated `0.2.0-rc.3` server/distribution and `0.2.0rc3` Python/MCP
metadata for the accepted entry/runtime separation workflow. Version-sensitive
fixtures already derive from the canonical version; explicit historical examples
remain intact. Versioned source-reviewed notes describe contract 1, guarded
selection, descriptor-bound input validation and the initial legacy entry upgrade.

The first-install prompt authenticates actual published metadata and new target
pins before setup, without inventing future hashes or assuming publication.
README/setup/support/update guidance distinguishes RC3 selection-aware entries
from immutable RC1/RC2 baselines, entry and runtime versions, retained locators
and session-only activation. Licensing, SDK and support scope are unchanged.
Promotion still reads approved Git notes and publishes exact tested artifacts
from the accepted merged-main push CI run without rebuilding.

Add a small manual contents-read-only public consumer workflow at the approved
RC3 source. It authenticates actual public RC2/RC3 release/tag/source/asset pins,
acquires legacy RC2 tooling and anonymously pulls its immutable registry image
with a fresh private Docker config. Doctor and real pinned Arca GPR/scenario
queries must deliver actual server `0.2.0rc2`, RC3 availability in initialization
instructions and complete project info, and a performed fresh check inside the
same daily cache. An off query must suppress notices and cache creation.

The probe retains raw JSON/protocol, argv/streams, exact named-container cleanup
and small provider/cache evidence on failure. It honors actual provider waits
without automatic retry/cache bypass and uploads no image/runtime/source caches.
It installs no target update and changes no private account plugin. Its protocol
route does not establish native, fresh managed Cloud or Mac acceptance.

Development validation passed 86 focused cases, including 33 consumer controls
for wrong tag/source/digest/URL/contract, missing or wrong
notices/server/GPR/scenarios, stale/cached versus performed fresh results, actual
HTTP header paths and isolated invalid-source rejection before network/runtime.
Ruff/format, strict Mypy, maintained documentation and shell checks passed;
the new script is included in the full CI type list. Fixture success is not
public acceptance: complete exact-source Trixie CI and the actual post-publication
consumer outcome remain separate evidence gates.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

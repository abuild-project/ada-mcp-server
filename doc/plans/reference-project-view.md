# Imported sources in selected project views

## 2026-11-17 — Investigation and implementation scope

Reproduce the anchor-dependent reference results reported with an explicitly
selected CLI GPR importing library sources outside its directory. Use a small,
valid library/importer fixture and record the actual ALS instance and loaded
GPR for both the call and declaration anchors before attributing the defect.

If the wrapper chooses different views, retain evaluated project membership
from ALS and make the smallest correction to file-only routing. Preserve
explicit ancestor and nested selections, lexical path boundaries, forced
project roots, ordered project paths, scenario values and selection retention
across pool eviction. Unrelated files must not inherit the last selected view.
Resolve ambiguous shared membership with the maintainer before changing its
selection contract. Do not change the pinned ALS or MCP SDK.

Add a regression that fails the original defect, exercise the existing
selection controls and document the final user-visible behavior. Validate the
committed candidate through `docker/build`, `docker/check` and `scripts/ci` in
the documented AMD64 Debian Trixie environment, including both nonroot numeric
identities. Host checks supplement that evidence. Keep the existing source,
artifact and installed-runtime identity checks intact.

Use the coordinator, developer, tester and independent reviewer workflow with
at most three local correction rounds, followed by at most three PR rounds.
Prepare the checked PR and stop before merge, release or publication. This
topic excludes SDK migration, installer/registry work, broader host setup and
unrelated open pull requests.

## 2026-11-17 — Causal result

The installed main baseline reproduces three references from the CLI call and
two from the imported library declaration. The pool uses two ALS instances:
the explicitly selected CLI GPR for the call and the automatically discovered
library GPR for the declaration. Querying that same declaration through the
existing CLI instance returns all three references. The correction therefore
belongs in wrapper routing. ALS already reports exact evaluated source files
for every imported project, separately from its runtime sources.

Retain the existing precedence of explicit lexical ancestor and nested views.
Before implementation, obtain the maintainer's choice for an imported source
shared by several selected views when none is a selected lexical ancestor:
the most recently explicitly selected matching view, or an ambiguity error.

## 2026-11-17 — Published baseline alignment

Fast-forward the topic to published main
`cd21c0a39b109dae1e3008b3aed73a6e5bc2fe18`, preserving its existing commits
and authorship. Its optional local image aliases, host controls and related
documentation do not change server project routing. The causal reproduction
remains identified with its original baseline
`a3f16279c08dffbe87c6f09ea77e88ed9d6df04b`; validate the complete final
candidate, including the imported main changes, before PR acceptance.

## 2026-11-17 — Approved imported-source selection

The maintainer approved preserving the deepest explicitly selected lexical
ancestor, including nested overrides. Only when none applies, use exact
evaluated imported-source membership; the most recently successfully selected
matching view wins. Explicit reselection refreshes that order and membership.
Ordinary file calls and pool eviction do not change selection order. Keep
runtime sources and unlisted files outside this fallback.

Local disk capacity permits source-mounted development checks in the verified
baseline runtime. The complete committed-source `docker/build`, `docker/check`,
artifact and identity chain runs in the existing managed GitHub CI environment;
source-mounted checks do not replace its acceptance evidence.

## 2026-11-17 — Refresh evaluated membership

Reproduction confirmed that reading ALS's cached project tree after an added
imported source did not refresh membership. Explicit selection must first
await the existing `als-reload-project` fence and its fresh indexing generation
before reading the evaluated view. Preserve the MCP and ALS process births.
Extend the existing compiling control with one owned added caller, requiring
the expanded four-location reference set after reselection. Retain hashes of
the original inputs and the explicit addition separately. Publish the
correction as an appended commit, preserving the already published topic.

## 2026-11-17 — Native trace contract alignment

The additional-tool control must require the refreshed selection's exact
native setup sequence: reload with empty arguments and a null result, then
project-view information and mains. Align its command guard, native projection
and mocked trace with that sequence. Reject missing or reordered reloads;
retain the existing forbidden-action controls and positional-signature limits.
Keep the runtime selection implementation unchanged.

## 2026-11-17 — Published registry baseline alignment

Merge published main `180ecbcf8f279bf00e75a3f926ef2fb430670320` normally,
preserving both histories and the accepted registry provisioning behavior.
Retain both changelog entries, the sorted record index and the independent
installer and project-selection setup guidance. Check the combined registry,
alias and verified-helper controls, then validate the exact merged candidate
through the complete managed CI chain. The topic scope and correction budget
continue unchanged.

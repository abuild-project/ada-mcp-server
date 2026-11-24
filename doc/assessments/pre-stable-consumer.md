# Pre-stable Mac consumer observations

Date: 2026-11-24. The maintainer supplied local reports for macOS 26.5.1 arm64
using source `7596a91f200e4b951bbbb0ffa3450c8fa9917cdc`. Its tree matches
accepted main `95cf6e6d70d556ee9547d849ce44dae2edd588f2`. Raw files remain
on the maintainer's Mac. These reports were not independently replayed on Mac
and do not establish acquisition or acceptance of future published 0.2.0 assets.

The image was obtained from PR CI run `45344624342`, artifact `14897424259`.
Reported index digest:
`sha256:4400adee286f39c7bd8fc3cd76f011d117bdddb631f0e8b64d90b3d6abc23a59`.
Reported config digest:
`sha256:7046b431d34e7a735557bfb249f789b29c6bb625c5a98ca80207afb941b69bbc`.
Image identity was cross-checked with that CI evidence.

All checks selected Abuild `136ca84f0f5c49acae5fdd22f43359a32ca26e70`,
`abuild.gpr`, `project_paths=[]` and scenarios `BUILD_TYPE=tests`,
`ABUILD_ANALYSIS=enabled`, after normal project dependency preparation.

- The temporary Docker/STDIO binding returned complete project metadata and
  indexing. XML/Ada navigation reached the installed
  `/usr/share/ada/adainclude/xmlada_schema/schema-schema_readers.ads:43:9`
  declaration from `libxmlada-schema-dev 25.0.0-4 amd64`. The reported hash
  query found two symbols and the XML parser file had zero diagnostics.
- Direct native `ada_rename_symbol` calls in both a resumed and a fresh Codex
  Desktop chat used explicit `preview=true`, returning 18 proposed edits in
  eight files with `applied=false`. Declaration, body and call sites agreed
  with source. The fresh report also checked the body end identifier and
  15 calls. Neither reported log observed a special approval/elicitation event.
- The resumed check retained 443 unchanged Ada source hashes. The fresh check
  retained 2,228 unchanged Ada/GPR hashes, unchanged Git status and unchanged
  HEAD. Explicit client approval and trust policies still apply.

These bounded observations add prepared-Abuild XML/Ada navigation and native
rename-preview evidence for this implementation. They do not establish all-tool
support, applied edits, other client/host versions or compiler correctness.

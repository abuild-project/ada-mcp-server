# XML/Ada image dependencies

The standalone image lacked the XML/Ada development exports needed by projects
importing `xmlada`. Add pinned Trixie `libxmlada-schema-dev=25.0.0-4`, supplying
Schema and installing DOM, SAX, Input and Unicode development dependencies.
Independent archive inspection
verifies all five development packages, six GPR files and retained Debian
notices and component source links.

At `2872442e1963f1b9c00ffb1eb84bac7f7163aeb5`,
[complete AMD64 Debian Trixie CI](https://github.com/abuild-project/ada-mcp-server/actions/runs/45342790725)
passed 1,412 tests, one E2E test, 32/32 real integration checks and both Linux
identities `1000:1000` and `501:20`. The XML/Ada fixture compiled and produced
ALI. The independently reviewed STDIO probe selected its exact GPR completely
with `project_paths=[]` and empty scenarios. Definition navigation from `Core`
at fixture position 2:10 reached the independently located package-owned
`/usr/share/ada/adainclude/xmlada_dom/dom-core.ads:38:9`, with the exact
declaration preview, unchanged fixture hashes and clean EOF shutdown.

The [published RC6 countercheck](https://github.com/abuild-project/ada-mcp-server/actions/runs/45344330337)
runs the identical harness against the installed release. Genuine ALS selection
returns `project-load-failed` (`-32603`) before package or navigation oracles.
The same-image compiler reports
`imported project file "xmlada" not found` with no ALI. Raw MCP/stderr,
unchanged input hashes and EOF exit zero corroborate this negative control.

Prepared Abuild navigation remains optional additional consumer acceptance
after its normal dependency preparation. The [plan](../plans/xmlada-image.md)
retains the scope and later project-build-derived image recommendation.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

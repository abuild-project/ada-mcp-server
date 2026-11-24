# XML/Ada image dependencies

The standalone image contained XML/Ada runtime libraries but lacked the
development exports needed to resolve GPR projects and Ada sources for
projects importing `xmlada`.

Install pinned Trixie `libxmlada-schema-dev=25.0.0-4` in the existing package
step. Its dependencies supply Schema, DOM, SAX, Input and Unicode development
projects and sources. Independent archive inspection verifies all five development
packages at `25.0.0-4`, six XML/Ada GPR files and the original Debian notices
and component source links.

A small repository-owned fixture imports the XML/Ada aggregate and all five
package families. The existing real integration runner compiles a fresh copy,
retaining compiler output, ALI and known-input hashes. At
`f72e9381fb709e6dbd0c225c074586505a314fd6`, the
[canonical AMD64 Debian Trixie CI](https://github.com/abuild-project/ada-mcp-server/actions/runs/45332249867)
passed 1,412 tests, one E2E test and 32/32 real integration checks with 79.34%
coverage. Identity checks covered Linux `1000:1000` and `501:20`. The
matching-source XML/Ada fixture compiled and produced ALI. Published RC6 fails
the same fixture specifically because the `xmlada` GPR is missing, producing
no ALI.

The supplemental prepared-Abuild navigation pilot with `project_paths=[]`
is optional additional consumer acceptance after normal dependency preparation.
The added real STDIO control requires complete selection with empty project
paths, then exact navigation from the fixture's `DOM.Core` import to the
independently located installed package declaration. It retains protocol,
stderr, input hashes and cleanup evidence on failure. Its candidate and
published-RC6 runs remain to be verified.

The [plan](../plans/xmlada-image.md) records the scope. A project-build-derived
image remains a later release recommendation.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

# XML/Ada image dependencies

The standalone image contained XML/Ada runtime libraries but lacked the
development exports needed by projects importing `xmlada`. Their GPR project
resolution and source navigation therefore require more than the existing
runtime packages.

Install pinned Trixie `libxmlada-schema-dev=25.0.0-4` in the existing package
step. Its dependencies supply Schema, DOM, SAX, Input and Unicode development
projects and sources. The image's generated Debian component and copyright
inventory records these packages under their existing terms.

A small repository-owned fixture imports the XML/Ada aggregate and all five
package families. The existing real integration runner compiles a fresh copy,
retaining compiler output, ALI and known-input hashes. Validation requires the
canonical AMD64 Trixie check chain and a separate prepared Abuild pilot with
explicit project/scenario selection, package identity and XML/Ada navigation,
compared with RC6's missing exports. Abuild's own project dependencies still
need normal preparation.

The [plan](../plans/xmlada-image.md) records the scope. A project-build-derived
image remains a later release recommendation.

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

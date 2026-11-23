# User documentation on GitHub Pages

The README and five user guides lead with the tasks readers came to do.
Choose Mac with Codex Desktop, Codex in Managed Cloud or direct Docker,
then query a real Ada project. Short setup prompts, a terminal example and
plain-language help cover the differences between Desktop's direct tools
and the Cloud skill's Docker helper. The guides give an alternate setup
when Plugin Creator is unavailable and show how to verify the selected
project and a known symbol. The optional tool reference explains how to
inspect the installed catalog and which tools the client routes can call.
The guides also cover approved updates and rollback.

GitHub Pages renders the Markdown in `doc/user/` at the project subpath.
The advanced installation, host setup, update and support references keep
their GitHub paths and headings so current skill, release and developer
links continue to work. The tooling bundle still carries its three
technical references. The [RC6 consumer assessment](../assessments/rc6-consumer.md)
retains the supplied Mac and Cloud observations and their evidence limits.

The site contains the original MIT license text. Host tests cover relative
and GitHub main links to rendered and advanced guides. They verify navigation
at the project subpath, unchanged GitHub reference and tag URLs, and rejection
of missing pages and heading fragments. Development checks also cover shell
and JSON examples and packaging contracts. CI retains the site in
`user-documentation-preview`. Publication uses a separate manual workflow on
main after an authorized maintainer configures Pages to use GitHub Actions.
See the [dated plan](../plans/user-documentation-pages.md).

Co-Authored-By: Codex (GPT-6.2) <codex@openai.com>

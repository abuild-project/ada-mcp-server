# Dependency unit and context forms

Dependency graphs attributed a separate protected body's context imports
to its first operation instead of the protected owner. They also omitted
limited with, private with and the combined limited private with clauses.
Multiline subprogram aspects could also appear as false dependencies.

The existing forward scan now recognizes complete protected body
declarations alongside task bodies. The import scan accepts the valid
optional limited/private prefix order and collects names in the existing
sorted, deduplicated depends_on list. Owners remain unqualified and no
visibility fields are added. Import collection stops before generic formals
or the selected unit declaration, excluding their aspect specifications.
This remains a lexical dependency summary; it does not model Ada visibility
semantics.

Focused regressions cover protected ownership, each context form,
comma-separated imports, comments and line breaks. Stop regressions exclude
Inline/No_Return aspects after the owner and No_Return on generic formal
subprograms, with and without real context imports.
A four-input Ada/GPR fixture includes those valid multiline aspects, requires
exact specification/subunit results over real STDIO and compiles with GNAT 14.

The [plan](../plans/dependency-unit-forms.md) bounds this correction.
At implementation revision `2dda1b68c5062eedcaa7bc2de69e7fecc415a0f8`,
45 focused tests, Ruff/format, strict Mypy, documentation checks and the
actual STDIO/GNAT fixture checks passed using an explicit source snapshot
in a retained project image. These are developer checks; canonical
container and independent-review evidence is reported separately for the
reviewed head.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

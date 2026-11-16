# Dependency unit and context forms

Dependency graphs attributed a separate protected body's context imports
to its first operation instead of the protected owner. They also omitted
limited with, private with and the combined limited private with clauses.

The existing forward scan now recognizes complete protected body
declarations alongside task bodies. The import scan accepts the valid
optional limited/private prefix order and collects names in the existing
sorted, deduplicated depends_on list. Owners remain unqualified and no
visibility fields are added. This remains a lexical dependency summary;
it does not model Ada visibility semantics.

Focused regressions cover protected ownership, each context form,
comma-separated imports, comments and line breaks. A four-input Ada/GPR
fixture requires exact specification and subunit results over real STDIO
and compiles the parent with GNAT 14. That fixture also compiles at the
unchanged base, where the graph omits all three qualified imports and
reports Touch instead of Guard.

The [plan](../plans/dependency-unit-forms.md) bounds this correction.
At implementation revision `09d9ee023b2dfa8b935b8f22024a1ef9cb7ae22b`,
41 focused tests, Ruff/format, strict Mypy, documentation checks and the
actual STDIO/GNAT fixture checks passed using an explicit source snapshot
in a retained project image. These are developer checks; canonical
container and independent-review evidence is reported separately for the
reviewed head.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

# Bounded additional-tool regressions

The ten tools outside the reading baseline had individual mocked coverage
without a shared source-derived MCP-to-ALS regression basis. This change adds
controlled real-Ada fixtures and exact expectations for call hierarchy,
dependencies, completions, signatures, actions, rename previews, formatting,
spec selection, builds and Alire manifest metadata. It preserves the reading
probe and complete existing validation chain. SDK 1.30.0, version 0.2.0-rc.3
and the documented support boundaries remain unchanged.

Five production corrections accompany that basis:

- Code-action discovery accepts a legal bare LSP Command string without
  calling dictionary methods on it, preserving the existing summary response.
- Rename previews retain each native replacement in both WorkspaceEdit
  shapes, so callers see the actual proposed text rather than a substituted
  requested name.
- Dependency summaries mask comments, strings and character literals before
  ordinary with-clause/unit matching, including doubled quotes and qualified
  quote-character literals that previously exposed false declarations.
- Call hierarchy synchronizes the queried source before native preparation.
  Changes to that file replace its opened contents; other changed open files
  still require explicit synchronization.
- Signature help honors the selected signature's explicit active parameter,
  including zero, before the top-level fallback. Documented defaults apply
  within the LSP integer domain; malformed used values remain diagnostic,
  and per-signature indices are not silently clamped.

The final test basis covers positive and negative queries, unrelated names,
warm source changes, exact call sites, ordered formals and meaningful action
proposals. It checks complete local and three-file rename edits, semantic
spec targets separately from filename fallback, formatting reconstructed in
memory, owned GPRbuild success and deliberate errors, and exact changed TOML
metadata. Independent fixture expectations remain the semantic authority.
Native request/result correlation and exposed-field fidelity are required
before accepting a call. Coordinate checks precede arithmetic while
preserving opaque protocol metadata.

Fixture snapshots reject links, special entries and unreadable directories;
scan, stat and read errors propagate. Source mutations validate the complete
owned batch before writing, and build products stay in declared obj/bin
paths. Source hashes, stable process identities, cleanup checks and targeted
counterexamples protect the evidence. Detailed mechanics and tool-specific
limits are in the [capability assessment](../assessments/additional-tool-capabilities.md)
and [development guide](../development.md).

This bounded basis does not promote the additional tools beyond the
[support matrix](../support.md). Three pinned-ALS positional signature
results remain wrong and unaccepted. Strict mode fails them; CI's explicit
assessment recognizes only their original native envelopes and contexts,
retaining correct expectations, wrong observations, `accepted=false` and
`semantic_acceptance=false`. Other discrepancies fail. Named-association
checks supplement these cases rather than accepting positional selection.

Native rename application remains an inherited gap: `preview=false` reports
application without writing sources. This work adds no writer. The shipped
read-only client requires explicit rename preview and denies formatting and
build calls. Actions are discovery proposals, formatting returns edits, and
Alire checks read manifest metadata without establishing an Alire workflow.

The existing [managed CI run 43766438216](https://github.com/abuild-project/ada-mcp-server/actions/runs/43766438216)
passed at source `147983437b71832fb84cfcd61814852633fa7aa2` on
Linux/AMD64 Debian Trixie with GNAT 14 and pinned ALS: 1,278 unit tests plus
one MCP end-to-end test, coverage of 2,985/3,802 lines, real ALS/MCP and
owned compiler probes, packaging, documentation and artifact checks.
Arca/Spawn/Anet acceptance passed under Linux identities 1000:1000 and
501:20. The additional control retained 53 calls: 50 accepted results and
three blocked signatures. These results belong to that exact source.
Linux identity checks do not establish macOS or native client compatibility;
the documented platform and client support limits remain unchanged.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

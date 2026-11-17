# Merge and validation history

Corrections hidden in a main-integration merge are difficult to follow in
ordinary commit history. Replacing a validation comment also removes the
visible evidence for its original head. Repository guidance now requires
main-integration merges to resolve conflicts only, with corrections in
separate commits, and each head's validation to be posted as a new short
comment. Existing published commits and comments remain intact.

Both requirements live in the versioned AGENTS.md and therefore apply to
every contributor. A concise validation comment identifies the head, relevant
results and evidence links; detailed logs remain separate. This changes agent
workflow guidance rather than runtime or integrator behavior, so no changelog
entry is needed. Validation uses the existing documentation checker and diff
hygiene, with separate tester/reviewer verification that source and test bytes
are unchanged. Hosted checks are recorded against the resulting PR head.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

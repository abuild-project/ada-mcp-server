# Pull request record check

GitHub Actions checks that a PR body matches the canonical change record at
the PR head. The checker derives the record path from the head branch,
normalizes CRLF, ignores trailing whitespace and reports a missing record
or a short unified diff. It reserves the exact derived topics `CLAUDE` and
`CLAUDE.local` for consistency with the sibling Arca Claude review workflow.

The read-only workflow checks out the event's exact base and head separately
with credential persistence disabled. It runs the base checker from the head
checkout to read the proposed record. When the base has no checker, the job
logs its use of the head checker. An unusable base checker or a failed
comparison fails the job. The action metadata at the existing CI pin confirms
SHA selection, workspace-relative checkout paths and credential controls.
[Pinned action inputs](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/action.yml) ·
[GitHub event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request) ·
[GitHub variables](https://docs.github.com/en/actions/reference/workflows-and-actions/variables)

Dependabot follows the same rule. Comparing the seven merged Dependabot PR
bodies with the records at their final heads found byte-for-byte agreement.
The regression tests exercise checker selection and reserved names against
the previous behavior at `eb8f80e46e20fa47d915360ea6271de41116502d`. See the
validation comment for the exact PR head and its results. Required-check
settings are a separate repository decision.

Co-Authored-By: GPT-6 <noreply@openai.com>

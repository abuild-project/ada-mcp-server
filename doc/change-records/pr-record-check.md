# Pull request record check

GitHub Actions now checks that a PR body matches the canonical change record
at the PR head. The check derives the record path from the head branch,
reports a missing record and shows a short unified diff on mismatch. It
normalizes CRLF and ignores whitespace at the end of the body and record.

The separate workflow uses read-only contents permissions and the checkout
pin already used by CI. The pinned action's inputs confirm SHA selection and
credential persistence controls. GitHub documents the head SHA, activity types
and event payload file.
[Pinned action inputs](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/action.yml) ·
[GitHub event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request) ·
[GitHub variables](https://docs.github.com/en/actions/reference/workflows-and-actions/variables)

Dependabot follows the same rule. Comparing the seven merged Dependabot PR
bodies with the records at their final heads found byte-for-byte agreement.
Required-check settings are a separate repository decision. See the
validation comment for the exact PR head and its results.

Co-Authored-By: GPT-6 <noreply@openai.com>

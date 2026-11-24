# Code review rules

Reviewers need consistent P1 criteria for validation, merge history and the
PR record. Claims in a change record or validation comment that the PR head
passed must use evidence from that head. Earlier negative controls and
development evidence may be cited with the revisions they tested. New or
changed checks must reject the original defect or a targeted invalid input.

Merges integrating `main` must stay within conflict resolution. The
contributor guide, other guides, active plan and change record must agree.
Submit the PR description from the committed record verbatim and ignore
trailing whitespace when comparing the posted body with the record at the
PR head. The record must explain how any external pins, versions and
upstream behavior the change relies on were verified.

See the separate validation comment for the final PR head and its results.

Co-Authored-By: GPT-6 <noreply@openai.com>

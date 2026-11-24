# Code review rules

Reviewers need consistent criteria for raising P1 findings about validation,
merge history and the PR record. The contributor guide now specifies those
criteria. Any validation cited by the change record must cover the PR head,
and new or changed checks must detect the difference from the previous
behavior. Merges integrating `main` must stay within conflict resolution.
The contributor guide, other guides, active plan and change record must
agree, and the PR body must match the committed record. The record must
explain how external pins, versions and upstream behavior were verified when
the change relies on them.

The repository documentation checker covers maintained links, examples,
index order and version references. The head-specific validation comment
identifies the checked commit and its results.

Co-Authored-By: GPT-6 <noreply@openai.com>

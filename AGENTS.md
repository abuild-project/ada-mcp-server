# Ada MCP agent guide

Read README.md, doc/development.md, doc/licensing.md and, when required, the
active topic plan before editing. SECURITY.md covers vulnerability reporting.
Preserve unrelated work. This guide applies to every agent and contributor,
regardless of vendor.

## Scope and implementation

- This is an independently maintained MIT project. Keep original copyright
  notices and third-party license terms. Record imported material and immutable
  origins in doc/licensing.md; generated checksums are not license grants.
- Use `codex/<topic>` for Codex branches. Other authors may choose their own
  single-segment prefix. Continue an existing topic and its correction counters.
- Obtain maintainer decisions for changes to compatibility, licensing, support
  scope or public contracts. Routine implementation choices within an agreed
  plan or authorized plan-free update need no extra permission.
- Follow the existing Python style: annotated public functions, Ruff formatting,
  100-character lines and strict Mypy. Dynamic protocol objects may use explicit
  `Any` at their serialization boundary. Add concise behavioral docstrings.
- Preserve MCP stdout as protocol only. Diagnostics belong on stderr. Do not
  equate a successful transport, empty cache or advertised tool with complete
  semantic results. Keep project views, paths and scenario values explicit.
- Host bindings and global client/Docker configuration must not be silently
  overwritten. Downloads need immutable version/hash metadata before execution.

## Dependency update plans

Pins in requirements/runtime.in are runtime dependencies. Other direct
requirements/development.in pins are development dependencies;
development.in includes runtime.in.

Dependabot patch or minor updates of development dependencies, runtime patch
updates, and the lock alignment they require may omit a separate plan.
Major updates, runtime minor updates and every other change need a dated
topic plan. This exception changes no tester/reviewer, CI or actual
installed-version evidence requirement.

## Validation and roles

- Use docker/build and docker/check for the AMD64 Debian Trixie, GNAT 14 and
  pinned ALS checks. A host compiler is not replacement evidence. Host setup
  checks run on their intended host; Linux UID tests do not prove macOS.
- scripts/ci defines the complete check chain, including unit tests, Ruff,
  strict typing, coverage, packaging, documentation and real ALS/MCP probes.
  New or changed checks must reject the original defect or a targeted
  invalid input.
- Triage findings by a reproducible or plausible defect in promised behavior
  or evidence, and value versus harness complexity. Fix or escalate an
  invalidated existing boundary even when exposed by a mock or malformed input.
  Explain deferral/rejection of optional, speculative or new-scope requests.
  Use the smallest useful counterexample; expand matrices only for a distinct
  gap or changed behavior, not to mechanically satisfy bot feedback.
- The coordinator assigns developer, tester and independent reviewer once for
  the task. Leaf roles do not recursively delegate the same workflow. Only the
  developer edits candidates; other roles report findings without fixing them.
- Test the immutable candidate in a fresh detached worktree. The independent
  reviewer starts without developer dialogue and reviews that same revision,
  all imported changes and the tester's primary evidence. Shared filesystems do
  not provide enforced role isolation; describe evidence accurately.
- Use at most three bundled local correction rounds. Start at zero and count
  each correction plus revalidation once. After local acceptance, start one
  separate PR phase with up to three rounds. Retain counters across agents,
  rebases and replacement PRs. Infrastructure retries without candidate edits
  consume no round. Findings after round three block the phase pending a
  maintainer decision. Do not defer unresolved local defects into PR review.
  A specific maintainer-authorized exception records its limited file/action
  scope in the dated plan and retains counters/evidence; it opens no new round.
- Keep operational logs/counters outside tracked source or under ignored
  build/. Durable decisions belong in an append-only dated plan section when
  required; plan-free routine updates keep their durable rationale in the
  required short change record.
  Both test and independent-review evidence must cover the final candidate.

## Code Review Rules

Report each of these findings as P1.

- A change record or validation comment uses evidence from a different
  revision to claim the PR head passed. Earlier negative controls and
  development evidence may be cited with the revisions they tested. Post
  actual PR-head results in that head's own validation comment.
- A new or changed check would also pass against the previous behavior because
  it lacks an effective lower bound, negative control or other way to detect
  the difference. See the sensitivity requirement in
  [Validation and roles](#validation-and-roles).
- A merge integrating `main` includes changes beyond conflict resolution.
- `AGENTS.md`, the guides, the active plan or the change record contradict one
  another.
- The change relies on an external pin, version or upstream behavior without
  recording how it was verified in the change record. This includes action
  SHAs, image digests, ALS behavior and SDK behavior.
- The PR body differs from the change record committed at the PR head when
  trailing whitespace is ignored.

## History, records and external actions

- Use Conventional Commit subjects of at most 50 characters. Capitalize the
  description and wrap prose at 72 columns without dangling one-word lines.
  Explain problem, behavior and reason; validation belongs in the change
  record. End with an accurate model `Co-Authored-By` trailer when applicable.
- Before first submission, fold unpublished corrections into coherent commits.
  Preserve imported/published authorship and history. Rewriting shared history
  or force-pushing needs explicit permission.
- Merge every pull request with a merge commit, preserving the reviewed
  commits and authorship. Squash and rebase merges are not used. This also
  applies to release and dependency updates. Use the commit subject/body
  conventions above for the merge message; do not rewrite published topic
  commits to obtain a single-commit PR.
- Merge commits that integrate main resolve conflicts only. Put corrections,
  including fixes needed for the combined state, in a separate following commit.
- Add doc/change-records/<topic>.md and its sorted index entry. Derive the topic
  from the branch by dropping the first prefix and replacing other slashes
  with hyphens. Use the committed record verbatim to submit the PR description.
  Ignore trailing whitespace when comparing the posted body with the record.
  End the record with the same accurate coauthor attribution. Keep ticket
  identifiers out of these texts.
- Post each head's validation as a new short comment; never rewrite
  an earlier validation comment.
- After merge, temporary validation-ref cleanup needs maintainer authorization
  for that occasion's named refs and permitted actions; later cleanups need new
  authorization. Preserve active work and open-PR refs, and never move or
  overwrite archive tags. Follow the detailed
  [cleanup safeguards](doc/development.md#validation-reference-retention).
  Do not repeat approval requests for the same already-authorized operations.
- Write records around the final problem, behavior, scope, validation at an
  identified revision and remaining limits. Size records to the change: a
  few-line fix needs about 100–250 words. For substantial changes, use
  300–700 words as guidance. For plan-free routine updates, a few sentences
  suffice. Link detailed mechanics in assessments/development docs; place
  durable history in the dated plan when required and operational attempts
  in logs. Omit chronological test counts and review-round narratives.
- Mention standing blockers or unrelated controls only when the change touches
  them. State each evidence boundary once.
- Update CHANGELOG.md for user/integrator changes, not internal agent-process
  adjustments. Keep transient review rounds and delivery status out of records.
- Prepare the complete PR packet before the normal handoff. A request to submit
  a PR with Copilot can authorize the necessary push, PR creation, review request
  and factual replies. Preparation alone does not grant external writes.
  At each handoff, the coordinator and independent reviewer check the record
  and PR description against the final state, agreed scope and actual evidence.
- Read hosted CI and all Copilot feedback at the actual head. Copilot supplements
  independent review; it does not replace it. Merge, tags, releases, image/plugin
  publication, settings changes and force-push need separate authorization.

Write maintained documentation in English for readers without the conversation
history. Distinguish tested support from work in development. Never describe
future release URLs as already available artifacts, or expose private host
paths/credentials in tracked examples and PR text.

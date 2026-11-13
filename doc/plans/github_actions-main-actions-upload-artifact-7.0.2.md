# Upload artifact action update

## 2026-11-13: Scope and decisions

Continue the existing dependency topic
`dependabot/github_actions/main/actions/upload-artifact-7.0.2` from
published revision `424c0876755271f070bb22e7c548f7f4d025b902`. Integrate
accepted main `7bff9e7f911af3a14d32de5f1f72fd6235ff2492` with an ordinary
merge, preserving published author information and history. Temporary Codex
preparation refs do not replace the existing topic or reset its correction
counters.

Retain full pin cf430e030ddbb5b0abf93d22962f4752f3646cd9 at both upload
sites. Preserve exact artifact naming, retention, source/image receipts and
least-privilege permissions.

Add the topic change record and sorted index entry. Keep this dependency
work separate from the frozen pilot release revision; it does not retag,
rebuild or replace that release's artifacts. No additional supported
platform, client or tool contract is introduced. No unrelated CI guard is
part of this update.

## Validation boundary

The original dependency revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388341426),
including 399 unit tests, the later ALS/MCP controls and generated-artifact
host checks. These results belong to that original revision. The merged
preparation requires its own complete Hosted CI and independent review; no
manual release promotion was exercised by that CI run.

Apply the existing bounded role workflow to the final immutable candidate.
Local preparation grants no remote push, review request, merge or
publication.

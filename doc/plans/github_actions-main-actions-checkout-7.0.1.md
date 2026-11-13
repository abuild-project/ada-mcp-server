# Checkout action update

## 2026-11-13: Scope and decisions

Continue the existing dependency topic
`dependabot/github_actions/main/actions/checkout-7.0.1` from published
revision `534046ff3c64b2ec65f563154c8e1c66f22c0192`. Integrate accepted main
`7bff9e7f911af3a14d32de5f1f72fd6235ff2492` with an ordinary merge,
preserving published author information and history. Temporary Codex
preparation refs do not replace the existing topic or reset its correction
counters.

Retain full pin 3d3c42e5aac5ba805825da76410c181273ba90b1 at all checkout
sites and keep existing workflow triggers, exact ref inputs and token
scopes.

Add the topic change record and sorted index entry. Keep this dependency
work separate from the frozen pilot release revision; it does not retag,
rebuild or replace that release's artifacts. No additional supported
platform, client or tool contract is introduced. No unrelated CI guard is
part of this update.

## Validation boundary

The original dependency revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388353044),
including 399 unit tests and the later complete Trixie and
generated-artifact checks. This run did not execute the manual promotion
jobs. The merged preparation requires its own complete Hosted CI and
independent review, including inspection of those promotion call sites.

Apply the existing bounded role workflow to the final immutable candidate.
Local preparation grants no remote push, review request, merge or
publication.

## 2026-11-13: Integrate the accepted artifact workflow

The maintainer selected the five accepted dependency updates for inclusion
before the first pilot release. Integrate accepted main
`bf9e664fdd9eff13409cd76613fc0eb3736e636e`, whose tree is the independently
checked artifact-upload update, into this existing checkout topic with an
ordinary merge. Retain both published parent histories and their authorship.

Keep checkout pin `3d3c42e5aac5ba805825da76410c181273ba90b1` at all three
sites and upload pin `cf430e030ddbb5b0abf93d22962f4752f3646cd9` at both
upload steps. Preserve the sorted union of change records and the existing
workflow inputs, token permissions and hash-locked Python dependencies.
The new immutable merged revision requires complete Trixie CI and independent
review before acceptance; earlier receipts remain evidence for their own
source revisions.

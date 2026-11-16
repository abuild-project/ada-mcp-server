# Review follow-ups

Base revision: `ebed7fd59c848b6a0fb2354a4feeff233ec99efc`.

## 2026-11-16: Bounded review evidence

Decision: retain the existing generated-formals input and four-times-source
regex budget. Count masking substitutions as well as the existing searches,
require a positive measurement, and reject unmeasured callable regex APIs
explicitly. One compiled-pattern helper attempts repeated prefix searches
before returning the real handler result; the same guard must reject its
measurement bypass. This establishes instrumentation coverage, not a timing
SLA or general complexity proof.

Decision: add one mocked launcher default call with an owned id stub
returning distinct nonzero UID/GID values and assert exact Docker identity
arguments. Preserve the production launcher and real identity boundaries.
Explain null's current signature-parameter contract beside its check,
including the need to revisit it before advertising LSP 3.18 support.
Remove only the generic-owner changelog's implementation half-sentence.

Decision: separately ignore Dependabot MCP major updates while retaining
minor/patch eligibility and current requirements/locks. Keep this topic
independent of dependency-owner product fixes. Start at local 0/3 and PR
0/3. Run targeted development checks in the existing project image; fresh
candidate testing, independent review and exact-head hosted CI follow.

# Host interpreter and update-policy setup

Base revision: `d723cd23261e0973a8e8e9d41383a3744f7fcf85`.

## 2026-11-20: Native setup and distinct Mac/Cloud routes

The maintainer authorized the next change after supplied Mac RC4-to-RC5
acceptance exposed a deliberately disabled native update policy and GUI PATH
selecting unsupported Python 3.9 while CLI Python 3.13 worked. Pin the supported
host interpreter already running setup in newly generated native fragments.
Add one optional absolute launcher `--python` argument, retaining existing
configurations and their PATH fallback. Diagnose unavailable/unsupported
advisory interpreters and checker failures on bounded stderr while continuing
MCP with protocol-only stdout and untouched stdin. Keep Python 3.11 minimum,
existing advisory network budgets, binding schema and workflow contract 1.

Make intended/effective update policy explicit in generated configuration and
setup reports. Honor explicit flags, environment choices and default auto;
retain deliberate off without rewriting installed configuration. Offline
launcher checks and Doctor validate the chosen host interpreter without
networking. Distinguish Doctor's forced-off MCP probe from the user's intended
native policy. Use one selected interpreter, with no registry, candidate search,
SDK/dependency changes or global environment/configuration writes.

Document local Mac user-wide skill discovery and native configuration separately
from account-owned Cloud skill-plugin activation, verified runtime acquisition
and Docker query-helper use. Check retained selection/pins or bootstrap a fresh
environment; assume neither Mac/Cloud synchronization nor Cloud task persistence.
Offer current published release metadata/provenance for new Cloud installations;
retain the immutable legacy fallback and one-time RC1/RC2 entry upgrade. Preserve
private identity/audience on explicitly requested entry updates. Compatible
later runtimes need no plugin replacement. Mark implementation changes as
source/unreleased, since published RC5 lacks the new argument. Preserve published
RC4/RC5 notes and assessments; supplied Mac outputs do not establish independently
verified archive bytes, new-fix Mac acceptance or third-party Cloud import.

The assigned developer alone edits candidates. Use the smallest counterexamples
for GUI PATH versus explicit Python, fail-open diagnostics, generated pin/policy
and offline checks; each added test must reject an original defect or targeted
invalid input. Run focused style/type/documentation checks, then freeze one
coherent unpublished commit. The assigned tester runs the existing complete
AMD64 Trixie/GNAT 14/pinned-ALS hosted chain from that immutable revision; the
independent reviewer assesses the same candidate. Local correction phase starts
at 0/3, followed only after acceptance by a separate PR phase at 0/3. Infrastructure
retries without candidate changes consume no round. Preserve prior artifacts;
no local Docker, weaker compiler, version bump, push, PR, merge, tag, release or
plugin/account write is authorized for this developer handoff.

## 2026-11-20: Bound offline probes and preserve advisory fallback

Apply a fixed two-second deadline to the host-interpreter version probe using
Bash 3.2-compatible host process supervision, independent of the selected
interpreter. Terminate and reap the timed-out probe and its watchdog, preserve
MCP stdin/protocol stdout, and make offline validation fail visibly. This bounds
only the new version probe; the existing checker's network deadline is unchanged
and no general runtime-process watchdog or process-tree contract is introduced.

Keep malformed inherited update policy advisory during ordinary launcher/query
use: emit one bounded stderr warning, disable the advisory and continue MCP
without checker/cache/network work. Native configuration generation, Doctor and
launcher --check remain strict so incorrect configuration cannot be validated
as successful. Preserve valid explicit flags, environment precedence, deliberate
off and default auto. Verify the two defects with small hanging-interpreter and
invalid-environment counterexamples against the prior immutable implementation;
retain that published commit and add one following correction commit.

## 2026-11-20: Require a valid supported probe version

Offline interpreter acceptance requires both successful probe exit and a
bounded, well-formed reported numeric Python version meeting the 3.11 minimum.
An empty response, malformed version or zero-exit older version must fail
validation; ordinary MCP startup keeps the existing bounded warning and
advisory-only fallback. Preserve the two-second probe deadline, process reaping,
private output cleanup, stdin/stdout and intentional off bypass. Check empty,
malformed and older zero-exit counterexamples against the prior immutable
implementation, retaining the real supported interpreter control. This is
version-response validation, not executable authentication or interpreter search.

## 2026-11-20: Validate the complete version response

Require the complete private probe output to contain exactly one canonical
numeric version and its terminating LF, with at most 64 version bytes plus LF.
Compare the complete standard Unix byte count with the parsed line length so
valid-prefix responses with trailing data cannot pass offline validation.
Preserve successful exit, the Python 3.11 minimum, timeout/reaping/cleanup,
advisory-only runtime fallback and intentional off bypass. Use only the small
trailing-text and oversized-trailer counterexamples against the prior immutable
implementation; no interpreter authentication or broader parser scope is added.

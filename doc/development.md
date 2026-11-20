# Development and validation

Read AGENTS.md and, when required, the active plan before editing. Use topic
branches and the coordinator/developer/tester/independent-reviewer workflow
described there.
The developer makes modest targeted checks; the tester runs the complete chain
from a fresh detached worktree of the immutable candidate. Review the complete
topic against its accepted base, including any newly imported changes. The
bootstrap acceptance covered all changes since imported revision
`961f532bcc633189e8618852732be289752cbcd7`, including the independent import
README on main; later release work uses that accepted bootstrap as its base.

Plan eligibility is defined by the
[dependency-update plan rule](../AGENTS.md#dependency-update-plans).
A short record with durable rationale is always required; a few
sentences suffice for those routine cases. Keep operational counters and
attempt logs outside tracked source. The same tester/reviewer roles,
complete CI and actual installed-version evidence requirements apply.

## Reproducible check environment

```sh
docker/build --tag ada-mcp-server:candidate
docker/check ada-mcp-server:candidate
```

docker/build supplies Docker with a tar context made from the exact committed
Git tree, including the Dockerfile and version metadata. Ignored local files,
virtual environments and logs are not build inputs, regardless of their names.
The recipe needs no private checkout or previous Abuild image. It uses
an immutable official AMD64 Debian Trixie base, GNAT 14/GPRbuild pins, pinned
ALS archive/license checksums and hash-locked Python dependencies. In managed
Cloud, pass `docker/build --proxy-ca /path/to/combined-ca.pem` using the provided
CA bundle; the BuildKit secret is transient and never copied into the image.
Do not disable TLS verification. The default Docker host/context remains under
the caller's control; choose the actual managed socket when needed.

docker/check unpacks the committed Git snapshot into a private executable
`/ci-work` tmpfs and sets TMPDIR beneath that mount. This narrow CI scratch is
needed for directly executed scripts and test fixtures. `/tmp` remains noexec;
the production launcher and its read-only/noexec runtime boundaries are unchanged.
The harness runs scripts/ci under
the caller's nonroot identity, no network, readonly source/root mounts, dropped
capabilities and private HOME/tmp. Evidence defaults to build/check. An existing
output is rejected before Docker/check execution or evidence writes. To repeat
the chain, retain that directory and select a new absolute output:

```sh
docker/check ada-mcp-server:candidate --output /absolute/new-check-attempt
```

Before lint/tests, scripts/check_requirements.py compares exact pins from
requirements/development.in and its relative -r includes with development.lock.
It accepts this repository's pin/include lines, comments and generated SHA256
hash continuations; unsupported relevant lines fail rather than disappear.
Missing, conflicting or different pins fail with stderr diagnostics. Extra
transitive lock packages are allowed. This checks input/lock agreement,
not dependency resolution or artifact-hash validity.

The chain runs Ruff/format, strict Mypy, unit tests with coverage, distributions,
documentation/link/example validation, and real ALS protocol, parent-GPR and
diagnostic-publication probes. The required diagnostic control changes a new
malformed source to valid text and back in one MCP/ALS session, requiring
source-bound errors, complete file publications and stable observed process IDs.
Process parentage and start ticks come from core Linux procfs stat/cmdline
records; optional task children entries are not required. Missing or ambiguous
identities fail, and process start ticks guard against PID reuse.
An always-empty diagnostic corruption fails its negative control. Host
compilers and mocked ALS tests are not integration evidence.

The imported-view control compiles a library and an importing CLI, requiring
the same exact three references from the initial call and declaration anchors.
The declaration query uses an equivalent absolute path containing `..`.
It adds and compiles one imported caller, reselects the CLI project and requires
four references from both the new call and original declaration. Procfs
identities require the same MCP/ALS births through those queries. Positive and
negative workspace queries exercise an unlisted source's separate project.
The retained protocol, compiler output and known Ada/GPR input hashes identify
the bounded fixture; the explicit addition has its own hash, and generated
compiler outputs are excluded from the input inventory.

The required reading probe uses a fresh owned Ada/GPR fixture for exact
definition, implementation and object-type targets, document hierarchy,
workspace matches and reference sets with and without declarations. An
unrelated object shares the queried name. A comment supplies a no-target
case, and an owned source mutation moves the declaration, changes its type
target and replaces one reference with two in the same observed MCP/ALS
processes. Exact post-mutation locations, reference counts/sets and hover
declarations must replace the warm results. Ada/GPR hashes, including both
committed source states, surround each read-only call. The probe
retains raw protocol, results, both source states and failure summaries;
EOF cleanup must remove the observed ALS birth. Mocked oracle guards reject
empty, wrong, duplicated and stale payloads, including old locations paired
with fresh disk previews. Full-runner mocked controls also reject source
changes during calls, changed process births and changes to an owned temporary
original-fixture copy, preserving the intended failure and available evidence.
The initial state's comment line is serialized metadata; no-target calls
exercise the changed state. These mocked controls do not establish live proof.
The documentation checker also enforces alphabetical change-record titles.

The additional-tool control requires exact fixture-derived call edges and
native call-site ranges, qualified members, signatures, code-action discovery,
single- and cross-unit rename previews, spec targets, formatting edits,
manifest fields and actual owned GPRbuild success/error results. An isolated
main-only change tests hierarchy synchronization before any other handler;
a later package/signature change explicitly synchronizes those other files.
Ada/GPR/TOML/template hashes exclude only the fixture's declared obj/bin
outputs. Native requests/results, MCP envelopes, complete source states,
process births and cleanup survive failure. Actions and rename previews
never execute edits; formatting is reconstructed in memory before an explicit
write to the fresh owned fixture for the already-formatted check.
Its cold project-selection trace requires initialize, then exactly
`als-project-view-information` and `als-mains`. Default repeats on the same
GPR/context use those two metadata commands without initialization or reload.
Only explicit `refresh=true` on a reused client requires `als-reload-project`
with empty arguments and a null result before metadata. A new exact client
avoids that redundant reload even with true. Redundant default/cold reloads
and missing/reordered explicit warm reloads fail; actions remain forbidden.

Refresh is validated as a strict Boolean before client acquisition. Fresh
explicit startup is one-shot state independent of source-list contents, used
only to avoid redundant explicit refresh; cache hits clear it. Default metadata
observations never invalidate readiness, so they can observe false become true
on the same live client. Explicit refresh invalidates prior readiness while
preserving progress identities and generation. Project metadata does not wait for semantic
indexing: `complete` describes the evaluated GPR view, while the Boolean
`indexing_complete` snapshots observed progress with the same 0.1-second
quiescence interval as the existing semantic wait. Warm readiness additionally
requires an indexing begin newer than the captured reload generation; merely
ending an older active index is insufficient. False includes pending and
unconfirmed states, including a view with no observed progress. Deterministic
progress controls check that pending metadata keeps its client and can later
become ready, without changing semantic query guards. The
[larger-project Mac timing check](assessments/project-selection-timing.md)
is an optional later performance assessment. The
[RC4 release plan](plans/release-0.2.0-rc.4.md) records the original
publication-before-Mac-test order. The supplied
[RC4 Mac assessment](assessments/macos-codex-rc4.md) retains the later bounded
evidence. The [RC5 release plan](plans/release-0.2.0-rc.5.md) prepares a new
published target for a subsequent Mac update check, without claiming acceptance.
The [RC6 release plan](plans/release-0.2.0-rc.6.md) packages the host Python and
policy fixes for the Managed Cloud update. The actual Mac source and published
consumer checks remain pending.

The locked MCP SDK 1.30 validates advertised tool input schemas before server
dispatch. `tests/host/test_input_validation_contract.py` checks that boundary
through actual stdio with an ALS startup sentinel; `scripts/test_integration.py`
adds a rejected call and an allowed extra-property call against real ALS.
The handler's strict refresh Boolean guard is currently shadowed by SDK
validation on stdio. An SDK 2 migration must reproduce server-side validation
or document a deliberate contract decision before changing this behavior.

Three pinned-ALS positional signature cases remain unaccepted. The default
control fails their incorrect active indices. CI explicitly assesses only
the three evidenced cases, requiring the unchanged native request/cursor,
the exact original raw defect envelope and effective native/MCP index fidelity.
The selected signature's explicit parameter index takes precedence over the
top-level fallback, including zero. Only documented defaults normalize valid
out-of-range signature/top-level indices for native acceptance; malformed raw
indices and a per-signature out-of-range index remain unaccepted. Public
`active_signature` reports the effective index used for parameter selection.
For nonempty replies, a present malformed native `activeSignature` selects zero
and adds `selection_diagnostic` with reason `malformed-active-signature`, the
exact `raw_active_signature` and fallback `first-signature`. Missing and valid
out-of-range indices produce no diagnostic. A malformed parameter index
actually selected by the existing presence-based precedence also reports
integer zero, with a separate `parameter_selection_diagnostic`: reason
`malformed-active-parameter`, exact `raw_active_parameter`, source
`selected-signature` or `top-level`, and fallback `zero`. Both diagnostics
can coexist. Missing, domain-valid out-of-range and unused malformed parameter
fields add no parameter diagnostic. Explicit null is malformed; a present
malformed selected-signature parameter still overrides the top-level value.
Domain-valid selected-signature out-of-range values and empty/missing-list
defaults remain unchanged. Empty replies retain the negative shape.
The [parameter contract plan](plans/parameter-selection-contract.md) bounds
this public fallback; it does not establish native acceptance.
Validate every raw index,
including unused fields, against LSP's 0..2147483647 integer domain before
precedence or defaults; MAX is valid and MAX+1 remains malformed. It retains expected-correct
and observed-wrong values with `accepted=false`, `semantic_acceptance=false`
and status `assessed-with-native-blocker`. Named associations supplement the
selection checks. New coordinates, candidate conversion defects and every
unrelated mismatch fail. This bounded test basis does not promote the
additional tools beyond the [support limits](support.md) or fix ALS itself.

The additional-tool harness keeps strict orchestration and its ordered query,
preview, source-change, manifest and build phases in scripts/real_additional.py.
One private control context holds the session, total deadline, process identity
and per-call evidence guards. scripts/additional_support.py supplies shared
owned-fixture inspection/hashing, batch mutations, MCP decoding and native
tracing. scripts/additional_native.py and scripts/additional_oracles.py retain
the native and semantic checks. scripts/observe_additional.py retains only
the --serve-trace child entry used by the required control, dispatching directly
to the shared tracer with protocol-only stdout. The optional exploratory
--output runner is retired. Shared fixture, mutation, decoder and native-trace
guards and the strict control's negative tests remain in CI; the CLI tests
require retired-option rejection before dispatch or writes and unchanged trace
dispatch. See the [retirement plan](plans/retire-exploration.md) for test-case
accounting and the superseded optional-retention decision.

For fast development only, a local venv may run a targeted check:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements/development.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pytest tests/test_als_pool.py -q
```

requirements/development.lock records the checked reproducible development
baseline. The optional .[dev] extra uses lower bounds from pyproject.toml
and may install newer allowed releases. Use the lock-based commands above
when reproducing the checked setup.

Local pytest runs as root explicitly skip the six mode-000 permission-denial
cases in tests/host/test_additional_inspection.py. This is a development
convenience, not permission or native acceptance. Use a real nonroot account
to exercise those assertions. Set ADA_MCP_REQUIRE_PERMISSION_TESTS=1 when
these checks are mandatory: root then fails setup instead of skipping.
docker/check sets that flag explicitly and retains its real nonroot UID/GID
guard, so the complete container chain cannot silently skip this proof.
The Docker-sentinel source-guard test uses an owned identity stub only for
its mocked CLI path; actual permission tests and native checks use real
identities.

These host checks are labeled as development evidence; they do not replace the
container chain. Update input requirements and regenerate the hash lock
deliberately. Python package notices and exact Debian/ALS versions are retained
in the image's component index; see licensing.md.

### Task-subunit fixture check

scripts/test_integration.py copies tests/fixtures/separate_task_project
into fresh scratch and requires the task source's exact STDIO dependency
reply. It compiles the parent with
`gprbuild -P tasks.gpr -p -c -u task_probe.adb`, using a 60-second timeout
and retaining command/output. The parent obj/task_probe.ali must be absent
before compilation; its resulting hash is retained. Hashes of tasks.gpr,
src/task_probe.adb and src/task_probe-worker.adb must remain unchanged.
These hashes cover the three known inputs, not arbitrary filesystem
writes. The compiler establishes fixture validity separately from the
lexical dependency query.

## Generate and test the actual artifacts

After committing the candidate and passing container checks:

```sh
python3 scripts/artifacts.py --image ada-mcp-server:candidate \
  --output /absolute/new-release-artifacts \
  --python-dist /absolute/new-check-attempt/python-dist
python3 scripts/host_acceptance.py --release /absolute/new-release-artifacts \
  --output /absolute/new-host-evidence \
  --arca /absolute/arca --spawn /absolute/spawn --anet /absolute/anet
```

For the default build/check output, artifacts.py's existing --python-dist
default is build/check/python-dist. A different check output needs the explicit
matching --python-dist shown above; never substitute stale distributions.
The complete committed-source check writes python-dist/provenance.json only
after every check passes. Receipt version 2 records the exact native immutable
image target actually passed to docker/check's container and its linux/amd64
platform, the exact generating commit, Git tar
snapshot SHA256 and both distribution hashes, verifies that the checked source
still matches that snapshot, and compares both package payloads to the committed
server files. docker/check supplies the source SHA and read-only snapshot;
invoking a build alone does not produce this completed-check receipt.
Packaging compares the selected native inspect ID to that checked target before
any image export/runtime use. Selecting another immutable image, even at the
same source/version, needs a new complete check and new output receipt. A new
tag for the identical tested target does not change its identity. Legacy receipts
without the checked image binding are refused. A native ID can be a Classic
config ID or an OCI index/manifest ID. It does not replace the canonical config
digest.
Default and explicit --python-dist paths require the receipt. Missing/stale
source or changed bytes are rejected before image export/packaging, even when
the version matches. The generated release retains that receipt as
python-distributions-provenance.json and rechecks copied distribution hashes.
The artifact command checks the source label against the clean Git revision,
saves the inspected immutable target once, and checks the archived config's
source/version/platform. It records a canonical config digest separately from
the executable Docker target. OCI index/manifest descriptors must authenticate
the path to exactly one AMD64 runtime config; attestations are not runtime
candidates. Safe bounded inspect/descriptor metadata is retained in
image-inspect-evidence.json and image-identity-evidence.json, including failures,
and the hosted evidence upload includes them. Config.Env is excluded.
The command creates the full tooling, lightweight plugin, source and release
manifest. Host acceptance acquires the generated
tooling instead of importing source helpers. It uses exact GPRs/scenarios and
real source-bound calls for both identities 1000:1000 and 501:20. It creates
new readable copies for identity tests and never chmods original source roots.
It records warm-cache state, complete args/results, isolation and exact cleanup.
The tester retains every failed attempt and does not silently replace evidence.
Host-command receipts include attempted argv, cwd, timeout and available partial
streams even if the command times out or cannot start. Existing receipts are
not replaced by a later attempt.

Production Python starts in isolated mode, excluding project cwd, user-site and
Python environment paths from imports while retaining installed venv modules
and the actual project cwd for explicit Ada views. The stdlib-only Docker-exec
probes, generated acquisition stdin and build version parser are also isolated.
The CI harness intentionally overrides the image entrypoint and imports the
committed check snapshot through its explicit PYTHONPATH; those source tests
remain separate from the installed production server's imports.

## Validation reference retention

After merge, temporary validation-ref cleanup requires explicit maintainer
authorization for each cleanup occasion's named refs and permitted actions.
This guidance grants no standing authorization; later cleanups require new
authorization. Do not repeat approval requests for the same operations already
authorized within that scope. Preserve active work and open-PR refs.

An unchanged source head reachable from main may lose its redundant temporary
branch. For a superseded snapshot, first create an annotated
`archive/<original-branch>` tag at its exact source SHA, recording the original
branch, SHA and reason. Verify the remote tag object and peeled target and
effective archive-namespace protection against updates/deletion before guarded
deletion of the unchanged branch. Stop on changed heads, active work,
conflicting tags or failed preservation/protection. Never move or overwrite
archive tags.

Retain required CI logs and artifacts separately: source tags preserve Git
history and do not extend the workflow's fourteen-day artifact retention.
Append dated substitutions to earlier retention decisions without rewriting
history or counters. The
[retention assessment](assessments/validation-ref-retention.md) identifies the
specifically authorized source inventory and separately archived CI evidence.

Small source-snapshot tags remain required for superseded heads. The binary
CI-evidence Git archive identified in the assessment is a one-off exception.
Prefer release assets outside Git object history for future CI evidence.
Before the next CI-evidence archive, obtain an explicit maintainer decision
on storage method and destination; the destination has not been selected.
That decision must respect immutable product releases and update-feed behavior.
Preserve the existing protected archive unchanged.

## Release and hosted review

Prepare coherent unpublished commits before the first submission. The PR
description is the change record verbatim; post later head validation in a
short PR comment. Hosted CI must test the same head; read all Copilot feedback
and preserve the separate PR correction counter.
Stop at the checked PR until merge/release permission is supplied.

Every PR is merged with a merge commit, including release and dependency PRs.
Squash and rebase merges are disabled by repository policy. Retain the tested
topic commits and their authorship; combine unpublished corrections before
first submission rather than rewriting published history. The merge commit
uses the same Conventional Commit subject and prose rules as topic commits.
Actual GitHub settings are verified separately in the
[public repository assessment](assessments/public-release.md).

Release promotion uses the already tested CI artifacts and source/image hashes;
it must not rebuild an untested replacement. GitHub Releases/GHCR publication
is prepared separately and is not performed by ordinary CI. GHCR packages may
start private even for a public repository. A later release needs an explicit
visibility decision and an anonymous manifest/pull proof before public
availability is claimed. Authenticated pulls do not prove anonymous access.
The account plugin and future fresh-Cloud deployment follow only after actual
public artifacts exist. See release.md for the manual promotion gates.

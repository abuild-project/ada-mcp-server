# Public installation and approved updates

Users need a clear way to install Ada MCP for their own projects, learn when
a release is available and approve an update that the skill can carry out.
README explains purpose, supported tasks and install-connect-use steps.
Detailed public RC1 acquisition, GPR-bound queries and client instructions
stay in the user guide, separate from contributor work and optional skills.

The host launcher checks fixed public GitHub release metadata with private
channel caches, opt-out and a two-second synchronous fetch deadline. Stable
installations follow stable versions; prerelease installations also see newer
prereleases. Automatic startup snapshots remain daily. Explicit updates check
requests fresh metadata without waiting for successful/offline cache TTL;
updates status stays cached and read-only. A one-shot check works with
automatic opt-out unchanged. Actual provider Retry-After/rate-reset deadlines
apply across both channels; contention and provider blocks never claim that a
fresh current result was fetched. Bounded/invalid feeds, offline/cache failures
and rate limits remain distinct from being current.

The checker does not install anything or move pins. The child is killed and
reaped at its deadline. Validated advisory metadata reaches initialization
instructions and project_info without changing protocol stdout or container
isolation. Query/native configuration roundtrips channel/cache settings;
Doctor and CI disable checks. Host entry points execute declared shared
source directly and exclude unverified sibling bytecode without changing the
verified runtime.

Manifest checks retain the exact declared helper bytes for a shared source-only
loader across image validation/archive import, acquisition, client policy and
Doctor sessions, update checks and packaged smoke startup. An unchecked sibling
bytecode cache cannot replace those verified sources. Explicit relative notice
cache paths fail before client fragment/log creation or query launch; valid
absolute Unicode/space paths, no-replace writes and implicit advisory failures
retain their existing behavior.

Full and generated lightweight skills share one consent workflow. They inspect
the actual route, capabilities, target release compatibility and installation
scope before asking once. A declined update leaves the old pair active; an
identified update request already supplies consent, while a search does not.
On yes, the agent authenticates NEW target pins through GitHub target-asset
digests and its release manifest, cross-checking repository/tag commit/source,
version and asset metadata rather than reusing embedded old hashes. It uses
existing acquisition/bootstrap/Doctor/query helpers with new paths, updates
the installed skill and relevant native/private Cloud selection, and checks
actual post-activation versions and queries. Missing host/provider capability
is reported as staged versus activated with the necessary user action, not
as completion.

Rollback retains old runtimes/images/bindings, absolute no-clobber skill
backups and native configuration. Cloud updates preserve intended identity,
audience and private metadata; a lower package re-upload is not promised
where the provider rejects it. No unattended updater executable, repository
source edit or public publication is authorized by this update consent.

Published RC1 assets/tag remain immutable and contain no notifier. An initial
approved upgrade requires an actually published notifier-capable release.
This change creates no version/release or cross-account/Mac/native frontend
acceptance claim. Reviewed Cloud Arca evidence remains bounded to its concrete
source requests/results without new process/cleanup certification.

Development validation used Python 3.12 with the exact development lock,
including MCP 1.30.0. The source/host checks passed 268 cases, covering fresh
search/cache/provider rules, unchanged opt-out/install state, protocol,
packaging, image/archive validation and source-only helper execution. Valid
poisoned sibling-bytecode controls exercise real status, native, query, Doctor,
acquisition, export and smoke-help entry paths without executing the cache or
changing runtime bytes/modes. Explicit cache-path controls reject relative
values before outputs/logs and preserve valid Unicode/space paths, no-replace
writes and implicit advisory fail-open behavior.
Ruff/format, strict Mypy over 35 files, documentation/link/example checks and
Bash/whitespace checks passed. Stdio controls ran outside the sandbox after
its independent asyncio thread-wakeup control failed. Application-cache paths
were explicit workspace/tmp paths and unrelated checks opted out.

The additional isolated installed-server import control requires an installed
candidate; the dependency-only host interpreter does not supply that boundary.
That unchanged control belongs to the documented container chain, which
installs the candidate before testing it.

Packaging checks confirm that full and generated skills share the same consent
workflow. They do not establish real provider updates, conversational execution
or client activation; synthetic release fixtures are not published evidence.

Earlier public RC1 hash/acquisition and no-replace installation evidence is
retained separately. Focused host checks do not replace the required exact
AMD64 Trixie/GNAT/ALS container chain. No live release API request, image/Docker
execution or external publication is part of these development checks.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

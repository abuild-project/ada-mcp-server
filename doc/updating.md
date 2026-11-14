# Release checks, approved updates and rollback

This workflow requires **RC2 or later**. Confirm that the target is actually
published in the [release index](https://github.com/abuild-project/ada-mcp-server/releases)
before acquiring it. Published RC1 archives have no notice hook and remain
unchanged. They need one initial user-approved upgrade, using the
[RC2 installation prompt](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/first-install.md#install-or-upgrade-to-rc2).
No future artifact hash or source commit is supplied in advance.

## Keep the entry and runtime independent

The selection extension in this source is **unreleased**. Published RC1/RC2
entries and runtime manifests do not implement it; keep those immutable bytes
and their [RC2 workflow](https://github.com/abuild-project/ada-mcp-server/blob/v0.2.0-rc.2/doc/updating.md)
as the legacy route. One initial entry update is necessary to gain selection.
A prepared candidate with an unchanged version label is not a new public release.

A compatible entry can then keep its own instructions/package version while
using another exact verified runtime. Its supported workflow contract is integer
`1`, separate from SemVer and MCP server version. Require that exact value in
both the authenticated target release's `tooling.workflow_contract` and the
runtime manifest's `workflow_contract`. Missing, boolean or unknown values stop
before activation with a compatible-entry update requirement; never guess a
version range or silently use latest. This contract covers acquisition, binding-v2,
setup/query/update interfaces and selection; it expands no semantic tool support.

Read selection before acquiring or running a runtime. The trusted full entry's
acquirer provides this read-only command:

```sh
python3 -I /absolute/entry/scripts/acquire.py selection show \
  --file /absolute/private/selection.json
```

For a lightweight entry, execute its embedded acquisition source through
`python3 -I - selection show --file /absolute/private/selection.json` with the
same source here-document, replacing the fallback acquisition arguments. This
mode never downloads anything. Do not execute the fallback first. The explicit
`--file` wins over `ADA_MCP_SELECTION`, then `~/.config/ada-mcp/selection.json`.
Omitting `--file` on both activation and reads uses that default. It is
rediscoverable only where the host actually retains the files. A custom
`--file` does not save a pointer, write environment settings or teach future
sessions its path. Supply that same path in each session, or explicitly retain
`ADA_MCP_SELECTION`/the locator through the host/provider's supported environment
or discovery configuration. A command-local environment or current chat text
is not proof of future persistence. No host/provider setting is changed by the
selection CLI; unavailable persistence means report session-only activation and
one necessary user action, such as supplying the custom path next time.
Reading an absent default writes nothing. The private record pins runtime and
binding paths, manifest/binding hashes, actual version/source/image and contract;
all declared sources are authenticated before captured helper execution. Selected
helpers execute source bytes rather than unchecked sibling bytecode.

`selected` supplies the actual runtime/binding for Doctor, queries and fresh
update searches. A new chat resolves it again only when the same files and
default/custom locator are available there, instead of reusing embedded old
pins. If the intended custom locator is unknown, request that path; an absent
default does not prove there is no existing installation elsewhere. `invalid`/`incompatible` is a stop condition, not permission to ignore the
record. `absent` in a fresh Cloud session means perform the verified published
release bootstrap after necessary consent. Do not assume files persist from a
previous Cloud task. Authenticate actual target metadata/pins before executing
helpers, use the trusted acquirer with `--workflow-contract 1`, and test new
runtime/image/cache/binding paths through Doctor and real GPR/source queries.
No published compatible target means report the blocker, not invent one.

After those checks and user approval, activate the pair explicitly:

```sh
python3 -I /absolute/entry/scripts/acquire.py selection activate \
  --file /absolute/private/selection.json --runtime /absolute/new-runtime \
  --manifest-sha256 TRUSTED_NEW_MANIFEST_SHA256 --binding /absolute/new-binding.json \
  --workflow-contract 1
```

Use the hash/contract from the verified target release. The first write refuses
an existing record. Replacement also requires `--expected-sha256` from the
current `selection show` and a **new** absolute `--backup` path. This preserves
the old record before an atomic record switch. Unexpected state, occupied backup
or adjacent `.lock` means stop; never delete a lock automatically. Existing
runtime, binding, image and cache are retained. A failed replacement leaves the
old selection active; a backup may remain for inspection. Rollback validates
the old pair and activates it using the current expected record hash plus
another new backup. Confirm selected version and real queries after each switch.

For compatible runtime releases, keep the full/local skill and private Cloud
plugin unchanged. Update the entry only when its own instructions, permissions
or compatibility need to change, preserving its identity/audience and private
overlays. Selection does not change a running native client's config; explicit
supported merge/reconnect and real verification still apply. If state cannot
persist or reconnect/provider capability is unavailable, report session-only,
staged and activated results accurately with the necessary user action.

## What the notice does

A notifier-capable host launcher checks public GitHub release metadata at
startup, normally at most once per day per channel. A stable installation
follows stable releases; a prerelease installation also sees newer prereleases.
SemVer precedence decides which release is newer, not publication order.
The host sends one anonymous request to GitHub's fixed HTTPS release-list API;
it sends no project paths, source, scenarios or account credentials. It follows
no redirects and reads at most 1 MiB and 100 entries. Release descriptions,
commands and download assets are ignored. This is an availability advisory,
not a new source of trusted executable hashes.

Cold or expired cache checks can add up to a two-second fetch delay. The child
is killed and reaped at its deadline. Only metadata returned by a completed
worker is accepted. A timeout reports an offline/unknown check; recovery of
partial worker output or newly observed headers is not guaranteed. Previously
persisted active provider deadlines still apply. Cache/network failures leave MCP usable.
The private application cache defaults to `~/.cache/ada-mcp` (directory 0700,
files 0600), with a nonblocking endpoint lock for concurrent sessions. Automatic
checks cache successes and failures for a day. An explicit fresh check bypasses
that local cooldown; actual provider Retry-After/rate-reset deadlines apply
across stable/prerelease channels in the configured cache and are still honored.
Last-good notices are retained for at most seven days,
marked stale when the latest check failed or expired. A bounded/incomplete feed
without a newer candidate reports unknown rather than falsely claiming currency.

An available-version snapshot appears in MCP initialization instructions and
the existing `ada_project_info` result's additive `update_notice` field. Its
fixed message names the installed and available versions, canonical release
URL and freshness. The bundled query client preserves these fields; the skill
relays one available-version notice per chat, checks the actual target release
and asks whether to update. On approval it executes the workflow below.
Native clients receive standard
MCP data rather than depending on stderr. Actual UI rendering remains specific
to each frontend and has not been accepted for untested clients. Existing
instructions and project results are preserved. The server never checks the
network: container networking, mounts and immutable image pins stay unchanged.
Long-running clients get automatic checks on their next start/reconnect; an
explicit fresh search is available immediately without reconnecting.

## Check status or change the policy

These commands apply to tooling that includes this feature, not published RC1.
`status` only reads cached metadata. `check` requests fresh metadata now,
bypassing the ordinary daily success/offline cache. It makes at most one bounded
request per invocation and never installs anything. An explicit upstream retry
deadline returns `blocked` with `blocked_until`; a concurrent request returns
unknown/check-in-progress. Neither is reported as a fresh current result.
`check_performed` distinguishes an attempted request from a blocked/pending one.
Other outcomes are `available`, `up_to_date`, `unknown`, `offline`, `rate_limited`
and `disabled`. An advisory failure is not an Ada semantic error.

```sh
python3 /absolute/notifier-runtime/scripts/ada_mcp_setup.py updates status \
  --channel auto --cache /absolute/private-update-cache
python3 /absolute/notifier-runtime/scripts/ada_mcp_setup.py updates check \
  --channel auto --cache /absolute/private-update-cache
```

The channel choices are `auto`, `stable`, `prerelease` and `off`. `auto` follows
the installed version's stable/prerelease status. `stable` excludes all
prereleases; `prerelease` permits newer stable releases too. `off` performs no
cache or network work. An explicit `check` defaults to one-shot `auto` even
when automatic checks are opted out; `--channel off` still disables it. It never
changes the environment or persistent automatic policy. Asking the skill to
"search/check updates now" runs this fresh check without installation consent.
Every comparison uses the locked runtime's canonical
version, and the server rejects a notice for another installed version.

For one query, supply `--update-channel` and `--update-cache` before its request:

```sh
python3 /absolute/notifier-runtime/scripts/ada_mcp_setup.py query \
  --binding /absolute/binding.json --update-channel off \
  --update-cache /absolute/private-update-cache \
  batch /absolute/requests.json
```

`native-config` accepts the same options and records them in the fragment's
launcher arguments. Explicitly review/merge that new fragment and reconnect:

```sh
python3 /absolute/notifier-runtime/scripts/ada_mcp_setup.py native-config \
  --binding /absolute/binding.json --update-channel stable \
  --update-cache /absolute/private-update-cache --output /absolute/new-client.toml
```

The launcher also accepts these flags directly. If flags are omitted,
`ADA_MCP_UPDATE_CHANNEL` and `ADA_MCP_UPDATE_CACHE` select the channel and an
absolute cache directory in that host process's environment. Explicit flags
take precedence; GUI clients may have a different PATH/environment. Python
must be available to the host launcher for checks; missing Python suppresses
only the advisory. Doctor and `--check` do no update networking. No setting
edits global client/Docker configuration or the immutable binding schema.

## Ask once, then execute the approved update

The full and lightweight skills share this consent workflow. An available
notice is not installation consent, and a request to search is not a request
to install. Before asking, inspect the actual active runtime/binding, selected
GPR/scenarios, discovery link, native Ada entry or intended private Cloud
identity/audience. Read the actual target's compatibility and migration notes
as data; do not execute commands from release prose. Show installed/target
versions, freshness, the concrete installation/configuration scope and its
restart/reconnect impact. Check the available command/provider/reconnect
capabilities and identify any necessary user action before offering the update.
Then ask once, **"Update now?"**. An existing explicit
request to perform this identified update already supplies consent.

On no/defer, keep using the unchanged old installation and suppress the same
proposal until the user reopens it. On yes, perform the
scoped downloads, setup, skill/configuration activation and verification below;
do not ask again for every routine step. Consent does not authorize repository
source edits, commits, pushes, public releases/plugin listings or changes to
shared services. A missing capability or a different material scope is a real
blocker, not a reason to silently broaden that consent.

### Establish the target's trusted pins

Use the actual target release metadata from GitHub's fixed repository API,
`https://api.github.com/repos/abuild-project/ada-mcp-server/releases/tags/vTARGET`,
where TARGET comes from the identified release. Require the intended published
non-draft tag/channel, then use its asset metadata, not the notice's version
text alone. This is a procedure for real published releases; no TARGET asset
or future version is claimed to exist here.
Perform this read-only provenance/compatibility inspection before asking, or
before proceeding when the user has already approved the identified update.

1. Obtain the `release-manifest.json` asset's GitHub `digest` (`sha256:` plus
   64 hexadecimal digits), `size` and canonical version-specific download URL.
   Download its bounded bytes and verify size/digest before trusting its fields.
   If authoritative digests are absent or inconsistent, stop and obtain the
   maintainer's trusted release metadata; do not guess or reuse embedded hashes.
2. Resolve the release tag through GitHub's Git reference/tag objects to the
   exact commit, including annotated tags. Require `manifest.version == TARGET`
   and `manifest.source_sha` equal to that commit. A mutable branch name or
   `target_commitish` label alone does not establish this correspondence.
3. Take NEW values from that verified manifest: `tooling.filename`,
   `tooling.download_url`, `tooling.bytes`, `tooling.sha256` and
   `tooling.runtime_manifest_sha256` and, for selection-aware entries,
   `tooling.workflow_contract`; also `plugin.filename`/`plugin.sha256`,
   `artifacts_sha256` and the image records. Cross-check the exact asset names,
   sizes, canonical `github.com/abuild-project/ada-mcp-server/releases/download/`
   target-tag URLs and all available API asset digests. The notice and the
   installed skill's old embedded hashes are never NEW executable metadata.
4. Retain the release ID, tag/commit and asset identities used for consent.
   Before installing, reject a moved tag, changed digest, source mismatch or
   different target. Do not silently choose a newer release than was approved.

### Acquire, verify and activate after yes

1. Reuse the already trusted `acquire.py` with the NEW tooling and runtime-manifest
   hashes into a **new private runtime**. Read that verified runtime's guide;
   preserve its licenses and notices. Retain the old runtime, binding, skill
   storage, native configuration and image/cache for operational rollback.
2. Use the new runtime's Bootstrap to create a **new binding** with the approved
   physical roots and a **new explicit image cache**. Its verified manifest pins
   the matching image; cross-check its image metadata with the target release.
   Do not apply an old binding to a new runtime lock. Run Doctor and representative
   real GPR/scenario/source-bound queries, as in the
   [first-install guide](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/first-install.md).
   Compare results and cleanup before switching. On a failure, keep the old pair
   active and report the staged files and concrete blocker.
3. Activate the route actually approved, using the guarded local/native/Cloud
   steps below. A selection-aware compatible entry stays installed unchanged;
   activate its NEW pinned runtime/binding selection. Only changed entry
   instructions, permissions or compatibility require updating the skill/plugin.
   Legacy RC2 entries retain their version-pinned skill replacement procedure.
   Switch the explicit runtime/binding selection through the host's supported
   flow; do not overwrite the old immutable binding or unrelated client entries.
4. Verify entry compatibility and selected runtime pins, actual MCP
   server version against the new verified runtime metadata, selected binding
   and representative real queries **after** activation/reconnect. Verify that
   later sessions can access both the new pair and its selection locator. If
   only current-session access is established, report that limit and the path
   the user must supply next time. Your Ada project's compiler/tests remain
   separate. Download, staging and fragment generation alone are not completion.

If a provider update, persistent binding selection, tool or host reconnect is
unavailable, report exactly what is staged versus activated and the one needed
user action, such as reconnecting with the new fragment or selecting the updated
private plugin/new binding in a new session. Do not claim an update completed
until the active route has actually been checked. This is an agent-executed
update after consent, not an unattended updater executable.

For direct command-line use, activation means deliberately changing the helper
path and `--binding` in your commands to the verified new pair. Operational
rollback means using the retained old helper and its matching old binding.
Keep both images available; restoring a missing old image uses its recorded
immutable source. Do not delete old caches/images during the trial.

## Switch a local skill without losing its old target

Use this only for a needed entry update or the legacy version-pinned route.
A compatible selection-aware runtime update keeps the discovered skill intact.

Stop sessions using the affected discovery entry and avoid concurrent changes.
The installer deliberately refuses replacement. First use the **new verified
runtime's** `install-skill` with a new staging path outside all discovery roots,
for example `/absolute/private-staging/ada-development`. Choose a staging
parent and grandparent owned and writable by you, and retain the successful
installation report.

The following explicit switch, which the agent can run after approval,
preserves an absolute backup of the old target,
because an old relative symlink can break if simply moved elsewhere. Replace
all paths; the backup must be new and outside discovery. It refuses a real
directory, an occupied backup and replacement of an unexpected entry. It
never removes either skill's storage tree.

```sh
python3 -I - <<'PY'
import os
from pathlib import Path

current = Path("/absolute/project/.agents/skills/ada-development")
staged = Path("/absolute/private-staging/ada-development")
backup = Path("/absolute/private-rollback/old-ada-development")
if not current.is_symlink() or not staged.is_symlink():
    raise RuntimeError("inspect the existing and staged skill links first")
old_stat = current.lstat()
old_target = current.resolve(strict=True)
new_target = staged.resolve(strict=True)
if not backup.parent.is_dir():
    raise RuntimeError("create a private backup parent outside discovery first")
os.symlink(str(old_target), backup, target_is_directory=True)
current_stat = current.lstat()
if (current_stat.st_dev, current_stat.st_ino) != (old_stat.st_dev, old_stat.st_ino):
    raise RuntimeError("discovery entry changed; backup retained, nothing switched")
current.unlink()
try:
    os.symlink(str(new_target), current, target_is_directory=True)
except BaseException:
    if not os.path.lexists(current):
        os.symlink(str(old_target), current, target_is_directory=True)
    raise
PY
```

Start a new project session and confirm the actual discovered path, runtime
version and binding. To roll back, use the same guarded switch with `staged`
pointing to the retained absolute old backup link and `backup` pointing to
another **new** path. Confirm the current entry is still the link you activated
before switching. An occupied path is a stop condition, not permission to
delete it. Keep the old binding selection when using the restored skill.

## Switch native clients or a private Cloud copy

For native stdio use, generate a **new** fragment with the verified new runtime
and new binding. Back up the client's current configuration to a new path using
its supported no-clobber/export mechanism. Explicitly replace only the intended
Ada entry through that client's supported configuration, then reconnect and
test real queries and disconnect cleanup. Retain the previous entry/fragment;
rollback restores it explicitly and reconnects to its old runtime/binding.
Do not treat the generated Codex-style TOML as Claude/OpenCode configuration.
Native/Mac acceptance still requires evidence from the actual client/host.

When the entry itself needs updating, use Plugin Creator's guarded update
workflow on the intended reader-owned private Cloud identity. Preserve its audience/workspace,
notices, private metadata/compatibility overlays and NEW trusted source pins.
Do not raw-overwrite private metadata with the public archive. Inspect the
backend result and activate through
the supported host flow. Do not create a duplicate or repeat an uncertain
update. A provider can reject lower package versions: keeping the old archive
does **not** guarantee that re-uploading it restores the old plugin. Operational
rollback uses the retained verified runtime/binding explicitly. Package-level
rollback needs a provider-supported restore or a deliberately forward-versioned
corrective package with reviewed source pins; it is not an invented upstream
release or a lowered manifest. Cross-account import remains unverified.

# First installation

Choose a published pilot release to evaluate the pinned Ada MCP workflow. It runs Ada Language Server in a Linux/AMD64 Debian Trixie container;
read the [support limits](support.md) before choosing a host or client.
You need no private publisher plugin ID, public plugin-directory listing or
self-operated service. GitHub Releases supplies the artifacts.

Choose one entry path:

- **Direct MCP:** [install the current release](#install-or-upgrade-to-rc4),
  [create a shared binding and query your project](#shared-docker-binding-and-first-queries),
  or [prepare a stdio client connection](#connect-a-stdio-mcp-client). No skill,
  private plugin or Plugin Creator is required.
- **Optional Managed Cloud skill:** use the copyable prompt below with an available Plugin
  Creator to save your own private copy of the skill plugin, then acquire and
  run its pinned tooling in a suitable environment.
- **Local Codex:** use the same current-release flow, then install the skill
  once at `~/.agents/skills/ada-development` and optionally register native MCP
  in `~/.codex/config.toml`. This user-wide setup serves multiple repositories
  and worktrees. Repository-local discovery remains an explicit alternative.
  This path does not need Plugin Creator.

See the [tested Mac/Codex scope](#native-clients-and-host-boundaries) below.
A skill installation does not register native MCP tools. Users of Ada
MCP need no build or CI run of this repository; their own Ada project's normal
compiler/test workflow remains separate.

## Install or upgrade to RC4

Use RC4 for a new installation. It includes explicit project refresh,
imported-source view retention and the
[bounded fixes in its release notes](releases/0.2.0-rc.4.md). RC3-or-later
[selection-aware entries](updating.md#keep-the-entry-and-runtime-independent)
can keep using compatible exact runtimes without a skill/plugin replacement.
The supplied [Mac acceptance](assessments/macos-codex-rc4.md) used the published
RC4 runtime at source `7864cda95a5dfc264926a5110416196279ff957c`.
Still check the actual non-draft release and authoritative asset digests before
each acquisition; a source version alone does not establish publication.
RC1/RC2 below remain immutable public baselines. Their existing entries need
one initial entry update to gain selection; direct MCP use needs no plugin.

Copy this prompt to an agent with HTTPS and local command tools. It defaults
to one persistent installation for your local Codex user. Choose your physical
workspace and worktree roots with the agent before Bootstrap. Your approval of
a parent grants read-only access to all descendants, including future checkouts;
choose narrower roots if that scope is unsuitable. An existing explicit setup
request supplies consent within its identified scope.

```text
Install or upgrade Ada MCP 0.2.0-rc.4 once for my local Codex user, shared across
Ada repositories and Git worktrees. Default skill discovery is
~/.agents/skills/ada-development; default native config is ~/.codex/config.toml.
Inspect my actual Codex settings and intended existing skill/runtime/binding,
native entries and selection. Preserve them and unrelated configuration; use
NEW absolute runtime/binding/fragment/evidence paths and backups for rollback.
Use repository-local scope only if I explicitly choose it.

Before Bootstrap, agree once on physical development workspace parent roots
and actual client-managed worktree roots. Use pwd -P and git worktree list
--porcelain for the intended repositories, plus the running client's actual
worktree location/settings. Codex commonly uses ~/.codex/worktrees, but check
the actual configured home/location and any custom root; never reassign HOME
or CODEX_HOME. A worktree outside the workspace needs its own approved parent.
Approval of a parent covers all descendants read-only, so do not enumerate each
repository below it. Do not scan for or mount arbitrary extra roots. Add an
external dependency root only when it lies outside all approved parents.
Read actual publication and compatibility metadata as data:
https://api.github.com/repos/abuild-project/ada-mcp-server/releases/tags/v0.2.0-rc.4
Require this exact repository/tag, non-draft prerelease and canonical assets.
Stop if unpublished, incompatible or authoritative digests are unavailable.

Follow the provenance procedure in doc/updating.md: authenticate the final
release-manifest.json against its GitHub asset digest/size before reading fields;
resolve the release tag to the exact commit and require manifest source/version
agreement. Cross-check NEW tooling/runtime-manifest/plugin/image pins and URLs.
Require integer workflow_contract 1 in both authenticated tooling metadata and
runtime manifest; never reuse older hashes as RC4 pins or trust release prose
as code. Reject a changed target before execution.

Acquire the NEW tooling using my already trusted acquirer and NEW hashes.
If none exists, use the pinned RC1 source-acquirer procedure in this guide's
"First acquisition without an installed acquirer" section; that obtains only
trusted acquisition code, not an RC1 runtime installation.
An RC1/RC2 CLI has no workflow-contract flag; inspect the authenticated new
manifest's contract before invoking target helpers. A compatible later acquirer
can enforce --workflow-contract 1. Read the NEW verified guide, then Bootstrap
a NEW matching binding/image/cache with the approved roots. Keep
RC4's GHCR default: do not pass --transport archive or --archive unless I
explicitly choose archive-only setup or an explicit source is required.
The helper falls back to its verified archive on pull failure/timeout; a
successful pull with an identity failure must stop. Run Doctor and real queries.
For direct CLI use, explicitly choose that helper/binding. For a full/local skill,
run install-skill at the user-wide destination, or the guarded entry upgrade
if needed, then activate the pinned selection. Keep the runtime and selection
outside repositories; future compatible runtime updates can retain the entry.

Use the persistent default ~/.config/ada-mcp/selection.json unless I explicitly
choose a custom locator. It is rediscoverable only where its files persist.
Custom --file paths must be supplied again or explicitly retained through a
supported host setting; activation does not save a pointer.
If unavailable, report session-only use and the one necessary next-session step.
For native Codex generate a NEW matching fragment. Back up the existing config
and explicitly merge only the agreed Ada entry through supported configuration,
preserving other entries; never replace the whole config with the fragment.
Do not remove old repository-local entries or links without scoped consent.
Use the client's supported reconnect flow; for Desktop fully quit and reopen
the app, then verify a new chat and a resumed chat. Confirm user-wide skill
discovery, actual MCP server version and source-bound queries in a regular
checkout and an actual Codex-managed worktree after activation.
Select each connection's actual GPR, ordered dependency paths and scenarios;
never put one globally pinned GPR/project into the shared installation.
Do not claim completion from downloads, staging or generated configuration.

Keep my private Cloud plugin unchanged unless I explicitly choose an initial
entry update in that account. Such a change needs available Plugin Creator,
intended identity/audience and preserved private metadata/overlays. Public release
publication does not update my account. No source edits/commits/push/publication
or shared-service changes are authorized by this setup request.
```

Resolve RC4 pins from actual published metadata rather than copying another
release's pins. GitHub asset digests anchor the final manifest and NEW hashes.
Use the verified runtime guide after acquisition. If RC4 is unavailable,
deliberately choose an actually published older release using its verified guide.
The [RC3 guide](https://github.com/abuild-project/ada-mcp-server/blob/v0.2.0-rc.3/doc/first-install.md#install-or-upgrade-to-rc3)
retains its selection-aware setup. The explicit RC2/RC1 legacy procedures
below remain available; never invent a compatible target. The maintained source
guide supplies these clarified instructions; immutable RC4 archives and installed
skills do not acquire them automatically. Use this guide alongside the verified
runtime's guide, without editing its authenticated files.

### First acquisition without an installed acquirer

On a clean machine, obtain the known RC1 acquisition code from the public source
and check its immutable commit **before executing it**:

```sh
git clone --branch v0.2.0-rc.1 --depth 1 \
  https://github.com/abuild-project/ada-mcp-server \
  /absolute/new-acquirer-source &&
test "$(git -C /absolute/new-acquirer-source rev-parse HEAD)" = \
  9fd401023eb990574b1806f0083799be0cb39d7f
```

Stop on a failed clone/commit check. Authenticate RC4's release manifest and
derive its **new** tooling URL, archive hash and runtime-manifest hash by the
[provenance procedure](updating.md#establish-the-targets-trusted-pins). Require
workflow contract 1 in the authenticated release metadata, then invoke the
checked source helper with those actual values:

```sh
python3 -I /absolute/new-acquirer-source/tooling/acquire.py \
  --url VERIFIED_RC4_TOOLING_URL --sha256 VERIFIED_RC4_TOOLING_SHA256 \
  --manifest-sha256 VERIFIED_RC4_RUNTIME_MANIFEST_SHA256 \
  --destination /absolute/new-private-ada-runtime
```

These uppercase values are placeholders, not executable pins. The legacy
acquirer has no `--workflow-contract` option; inspect the acquired authenticated
runtime manifest for integer contract 1 before executing its helpers. Then use
the RC4 runtime for the [shared binding](#shared-docker-binding-and-first-queries),
[skill discovery](#optional-local-codex-skill-discovery), selection activation
in [the update guide](updating.md#keep-the-entry-and-runtime-independent) and
[native connection](#connect-a-stdio-mcp-client). No RC1 runtime or image is needed.

## Install or upgrade to RC2

RC2 adds fresh release searches and user-approved updates. Confirm publication
before installing it: the release API below must return the intended non-draft
prerelease and its actual assets. A prepared version or source checkout is not
proof that those downloads exist. If RC2 is unavailable, stop and use the
[verified RC1 fallback](#published-rc1-fallback-artifacts) deliberately; RC1 has
no notice hook. The commands in the remaining sections pin that fallback.

For a first installation, or the initial upgrade from RC1, copy this prompt to
an agent with HTTPS and local command tools. Direct MCP and local skills do
not require Plugin Creator. An optional private Cloud copy also needs that
provider's available tools. Replace the paths and select your intended route
before execution; an explicit request to install this identified target supplies
consent for that scope.

```text
Install Ada MCP 0.2.0-rc.2 for my Ada project, or upgrade my intended existing
installation to that version. Use my actual GPR/scenarios and physical roots;
confirm the intended CLI/local skill/native entry or my private Cloud identity
and audience. Choose NEW absolute private runtime, binding, image-cache and
evidence paths; retain the old runtime/image/binding/skill/config for rollback.
No build of Ada MCP or changes to my project's source are requested.

First inspect the actual published release and compatibility notes as data:
https://api.github.com/repos/abuild-project/ada-mcp-server/releases/tags/v0.2.0-rc.2
Require this repository, exact tag, non-draft prerelease and expected assets.
If it is unpublished, incompatible or lacks authoritative digests, stop rather
than guessing hashes or silently selecting another release.

Verify the bounded release-manifest.json download against its GitHub asset
sha256 digest and size BEFORE using its fields. Require canonical target-tag
asset URLs under https://github.com/abuild-project/ada-mcp-server/releases/download/.
Resolve v0.2.0-rc.2 through Git reference/tag objects to its exact commit;
require manifest.version 0.2.0-rc.2 and manifest.source_sha equal to that commit.
Cross-check NEW tooling filename/download_url/bytes/sha256/runtime_manifest_sha256,
plugin filename/sha256, artifacts_sha256 and image records with actual asset
names, sizes, URLs and API digests. Never use RC1's old hashes for RC2 or treat
an advisory/release body as executable metadata. Retain these identities and
reject a moved tag or changed target before acquisition.

Use the already trusted RC1 acquire.py from the pinned fallback source below
(or my existing verified runtime) with those NEW tooling and manifest hashes
into the NEW runtime. Do not run a downloaded helper before authentication.
Read its verified references/setup.md and references/updating.md. Use its
Bootstrap with my actual roots to create a NEW matching image/cache/binding;
run Doctor and representative real GPR/scenario/source-bound query batches.
Stop activation on verification or query failure and keep the old pair active.

Activate only my selected route: switch CLI helper and binding explicitly;
stage/switch a local skill with no-clobber backup; or generate a NEW matching
native fragment, back up the old entry and apply through the client's supported
configuration, then reconnect. If I selected a private Cloud copy, use available
Plugin Creator on my intended existing identity, preserving audience and private
metadata/overlays; create only when no intended installation exists. Update
the installed skill itself so later chats acquire RC2 pins. Preserve licenses
and attribution. Do not add native MCP registration to the skill-only plugin.

Verify actual active server/skill versions, pins and selected binding after
activation/reconnect, then run real project queries again. Report staged and
activated states separately. If a tool/provider/reconnect is unavailable, report
the exact blocker and one necessary user action; do not claim completion.
Keep rollback state: local/native switches can restore the old pair; reuploading
a lower Cloud package version is not guaranteed provider rollback.

This consent covers those scoped downloads/setup/configuration changes, not
repository edits/commits/pushes, public releases/plugins or shared-service
changes. Do not repeatedly request consent for routine steps of this target.
```

The source commit and artifact hashes cannot be embedded here before RC2's
accepted release commit is built and published. GitHub's immutable asset digest
anchors the final manifest, which supplies the new tooling pins; the existing
acquirer verifies them before materialization. The
[update provenance procedure](updating.md#establish-the-targets-trusted-pins)
gives the same checks for later published versions. After acquisition, use the
new verified guide and its actual metadata rather than the RC1 commands below.

## Published RC1 fallback artifacts

The [published release](https://github.com/abuild-project/ada-mcp-server/releases/tag/v0.2.0-rc.1)
uses source commit `9fd401023eb990574b1806f0083799be0cb39d7f`.
Public asset downloads and their hashes have been verified. This establishes
artifact availability, not acceptance of your account, host or native client.

| Artifact | Trusted SHA256 |
| --- | --- |
| [Skill plugin tar.gz](https://github.com/abuild-project/ada-mcp-server/releases/download/v0.2.0-rc.1/ada-development-0.2.0-rc.1.tar.gz) | `d4b967efdbe6e806106de869564360789604d67cf9b7bfa141b0284046d78ce6` |
| [Complete tooling tar.gz](https://github.com/abuild-project/ada-mcp-server/releases/download/v0.2.0-rc.1/ada-mcp-tooling-0.2.0-rc.1.tar.gz) | `b3c65145f608981235829455a7cb3451f94c0ad5161a35367bb80f92d817230c` |
| Runtime manifest inside the tooling, `scripts/runtime-manifest.json` | `499cea68013df5e29d58157bb04fa4bf771f61364612b8f202ef9119b3ab93e7` |

The small plugin contains `plugin.json`, `skills/ada-development/SKILL.md` and
`LICENSE`. Its skill embeds the existing verified acquisition code and pins the
complete tooling. It has no `mcp.json`, native MCP server registration or private
compatibility overlay. Preserve its version, license and attribution when
importing it. The tooling manifest also pins the image archive's URL, byte size
and SHA256. Bootstrap can download that archive into an explicit cache; the
compressed image is 302,305,010 bytes and Docker also needs unpacking space.

## Managed Cloud: create your private copy

Plugin Creator must be available in the reader's account/session. Its private
package workflow downloads the public archive locally, verifies it, and saves
that local file to the authenticated account's active workspace when present,
otherwise the personal account. Do not assume that every result has personal
`USER` scope. Inspect the returned identity and audience before activation.

**Import into a separate third-party account is UNVERIFIED.** A publisher-owned
copy or successful public download does not prove that import. The prompt is
an explicit onboarding procedure to perform and check in your own account.
If Plugin Creator is unavailable, use the local route below; no public listing
or import button is assumed.

Copy this prompt into a session with Plugin Creator available:

```text
Use Plugin Creator's skills-only private package workflow to install my own
ada-development 0.2.0-rc.1 copy. First check for my intended existing installation;
do not create a duplicate. Preserve its identity and audience on updates, and
resolve ambiguous matches before writing.

Download this exact public archive to a new local file:
https://github.com/abuild-project/ada-mcp-server/releases/download/v0.2.0-rc.1/ada-development-0.2.0-rc.1.tar.gz
Verify its SHA256 before reading or executing its skill instructions:
d4b967efdbe6e806106de869564360789604d67cf9b7bfa141b0284046d78ce6

Inspect the archive: it contains only plugin.json,
skills/ada-development/SKILL.md and LICENSE as regular files. Preserve the
released bytes, version, license and author notices. This is a skill-only
package; do not add a server, mcp.json, private compatibility overlay or public
listing, and do not substitute a publisher-owned private plugin reference.

If no intended installation exists, use create_plugin with the verified
archive's absolute local path, not its URL or bytes. It saves a PRIVATE plugin
to my active workspace or personal account. Inspect and report the returned
identity, audience and plugin_url. If saving is unavailable or uncertain, report
that state without claiming success or repeating an uncertain creation.
Activate the returned plugin through the host's supported flow. If a new
session is required for skill discovery, use my returned plugin reference there.
Do not claim that activation registers native Ada MCP tools.

Read the installed ada-development skill and my repository's AGENTS.md and
development guides. Preserve its workflow, roles and correction counters.
Acquire its pinned complete tooling into a new explicit private runtime path.
Use these trusted values, refusing mismatches:
tooling SHA256 b3c65145f608981235829455a7cb3451f94c0ad5161a35367bb80f92d817230c
runtime-manifest SHA256 499cea68013df5e29d58157bb04fa4bf771f61364612b8f202ef9119b3ab93e7

Before Docker setup, obtain my actual physical source/dependency roots, new
binding/cache/evidence paths and Docker host/context. Use the existing Bootstrap,
Doctor and query batch workflow with my real GPR files and scenarios. Inspect
source-bound results and confirmed cleanup; report missing Docker or resources
as concrete blockers. Keep compiler, tests, coverage and documentation checks
separate. Report import, discovery, acquisition, runtime and semantic-query
results separately, including anything unverified in my account or session.
```

This workflow saves a private package; it does not deploy a hosted MCP service.
The skill uses the environment's command tools to run the shared Docker helper.
The environment still needs the prerequisites below, source access and enough
storage. A native Ada MCP catalog in the current chat is a separate integration.
A supplied 15-call managed Cloud Arca batch has independently reviewed
source-bound requests and results; its [evidence limits](support.md) do not
establish another account's import or native Cloud registration.

## Acquire the tooling for direct MCP or local Codex

This section is the explicitly chosen **RC1 fallback runtime**, not the normal
RC4 installation. For a clean current-release setup use
[first acquisition](#first-acquisition-without-an-installed-acquirer) above.

Prerequisites are Git, Python 3.11+, Bash 3.2+ and a working Docker daemon able
to run Linux/AMD64 containers. Run host commands as a nonroot user with Docker
access. The [Mac assessment](assessments/macos-codex-rc4.md) bounds the tested RC4
host/client combination. Choose physical
absolute paths with `pwd -P`; replace every `/absolute/...` example below with
your own paths. Paths marked `new` must not already exist.

Clone the public release source into a new directory only to obtain the
existing acquisition helper; no MCP build or development setup is needed.
The commit check must succeed before that helper runs; the `&&` chain enforces
that order.
The helper verifies the complete tooling archive, its runtime manifest and all
declared files before materialization. No host Python packages are installed.

```sh
git clone --branch v0.2.0-rc.1 --depth 1 \
  https://github.com/abuild-project/ada-mcp-server \
  /absolute/new-ada-mcp-source &&
test "$(git -C /absolute/new-ada-mcp-source rev-parse HEAD)" = \
  9fd401023eb990574b1806f0083799be0cb39d7f &&
python3 -I /absolute/new-ada-mcp-source/tooling/acquire.py \
  --url https://github.com/abuild-project/ada-mcp-server/releases/download/v0.2.0-rc.1/ada-mcp-tooling-0.2.0-rc.1.tar.gz \
  --sha256 b3c65145f608981235829455a7cb3451f94c0ad5161a35367bb80f92d817230c \
  --manifest-sha256 499cea68013df5e29d58157bb04fa4bf771f61364612b8f202ef9119b3ab93e7 \
  --destination /absolute/new-private-ada-runtime
```

Read the verified runtime's `references/setup.md` and `references/support.md`,
then continue to the shared binding and query steps below for direct MCP use.

## Optional local Codex skill discovery

For skill-assisted use, also read the verified runtime's `SKILL.md`.
Use its existing helper to publish one new skill link in Codex's user-wide
discovery directory, shared across repositories and worktrees:

```sh
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py install-skill \
  --destination "$HOME/.agents/skills/ada-development"
```

The helper verifies and copies the skill into separate storage, prepares only
the launcher's user execute bit, and creates a no-replace symlink at that
destination. It preserves existing entries. If that destination exists, inspect
it and use the [guarded entry-switch procedure](updating.md#switch-a-local-skill-without-losing-its-old-target)
only when an entry update is needed; do not delete or overwrite it. Start a new
Codex session and confirm discovery of `ada-development` from that path; invoke
`$ada-development` when needed. Follow your Codex version's supported discovery
and session flow. Installing files alone does not prove discovery in a running
session or register native MCP tools.

Repository-local scope is an explicit alternative: use
`/absolute/ada-workspaces/project/.agents/skills/ada-development` as the
destination. Inspect existing local entries when migrating to user scope and
remove or switch them only with consent and a backup to avoid duplicate or
stale discovery. Keep the persistent runtime and selection outside repositories.
Skill installation does not edit native client configuration or change `HOME`,
`CODEX_HOME` or Docker selection.

## Shared Docker binding and first queries

Choose your physical development workspace parent roots once, plus the actual
client-managed worktree parents outside them. Check intended repositories with
`git worktree list --porcelain` and resolve directories with `pwd -P`. Git's list
shows existing worktrees for that repository; also inspect the running client's
actual worktree location/settings for future managed worktrees. Codex's usual
`~/.codex/worktrees` may be outside your development workspace. Resolve its
actual physical path, including a custom `CODEX_HOME` or client worktree root;
do not change those settings to fit an example. If no managed worktree exists,
use the client's supported flow to establish its location before claiming that
route is covered.

User approval of a parent grants access to all its descendants, including
future repositories and worktrees below it. Do not enumerate every descendant
as a separate root, scan unrelated directories or mount an entire home by
default. Add another approved `--root` only for needed sources/dependencies or
worktrees outside the selected parents. The example assumes two distinct
approved parents; replace or omit the second according to your actual layout.
Roots are mounted read-only at the same absolute paths. The image runtime uses
your nonzero numeric identity, private HOME, no network and dropped capabilities.
See [host setup](setup.md) for reserved paths, permissions and timeout details.

```sh
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py bootstrap \
  --binding /absolute/new-ada-binding.json \
  --root /absolute/ada-workspaces \
  --root /absolute/client-worktrees \
  --image-cache /absolute/new-private-image-cache \
  --output /absolute/new-bootstrap-evidence
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py doctor \
  --binding /absolute/new-ada-binding.json \
  --output /absolute/new-doctor-evidence
```

Bootstrap already runs Doctor before publishing the new binding. The second
command shows how to check it in later sessions. Each evidence directory must
be new. RC4 tooling tries GHCR first and uses the hash-locked image
archive only if the pull fails or times out. `--image-cache` sets that fallback
cache; omitting it uses the platform's user cache directory described in the
[host guide](setup.md#create-one-explicit-host-binding). Add `--transport archive`
for archive-only setup, also named in the error for unsupported registry version
formats. This does not extend acquisition or publication version support.
A successful pull with
an identity failure stops rather than falling back. Published RC3 and earlier
tooling keep their original behavior; their explicit `--registry` option
accepts a verified immutable registry digest as described in the host guide.
Bootstrap may download/load the pinned image; it preserves the current
Docker selection unless you explicitly pass `--docker-host` or `--docker-context`.
In a managed environment, use the actual supported daemon endpoint if its
default is unavailable; do not guess or globally change Docker configuration.
Existing bindings are immutable. Restore their recorded image with Bootstrap
and no overrides, or choose a new binding when changing roots or host selection.
For a changed root set, generate a new matching native fragment and explicitly
switch selection/configuration with backups, then reconnect. A shared binding
grants filesystem access; it does not choose a global GPR. Every connection
selects its own GPR, ordered dependency search paths and scenario values.

Create a JSON batch, for example `/absolute/private/first-queries.json`, with
paths from your actual selected view. Keep any required generated GPR inputs
present. Replace the empty search-path/scenario objects when your project
needs them; preserve ordered dependency search paths.

```json
[
  {
    "tool": "ada_project_info",
    "arguments": {
      "gpr_file": "/absolute/ada-workspaces/project/project.gpr",
      "project_paths": [],
      "scenario_variables": {}
    }
  },
  {
    "tool": "ada_document_symbols",
    "arguments": {
      "file": "/absolute/ada-workspaces/project/src/example.ads"
    }
  }
]
```

```sh
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py query \
  --binding /absolute/new-ada-binding.json \
  --log-dir /absolute/new-query-evidence \
  batch /absolute/private/first-queries.json
```

Inspect the selected GPR/search paths/scenarios and returned symbols against
the real source. Check `complete`, `truncated`, scope and source coordinates
where supplied; then try a supported navigation query at a real location in
that view. Doctor/catalog success alone is not semantic acceptance. Empty
cached diagnostics do not establish clean compilation or whole-project health.
Keep evidence private because it can contain source paths and scenario values.
Run your Ada project's required compiler, tests, coverage and documentation chain.

## Connect a stdio MCP client

After Bootstrap has verified the image and created your binding, use the
existing helper to generate a separate client fragment:

```sh
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py native-config \
  --binding /absolute/new-ada-binding.json --output /absolute/new-ada-mcp.toml
```

The fragment contains the stdio launcher command and arguments derived from
that binding, plus a read-tool policy. It uses Codex-style `[mcp_servers.ada]`
TOML. For user scope, review and explicitly merge the Ada entry into the actual
Codex user configuration (normally `~/.codex/config.toml`) through your version's
supported configuration flow. Back up the existing file first, retain unrelated
settings and resolve any existing Ada entry explicitly. Do not copy the fragment
over the entire configuration. Repository-local configuration is an explicit
alternative. The helper creates only a new fragment; it does not activate tools.

Use the client's supported reconnect flow after activation. For Codex Desktop,
fully quit and reopen the app, then check a new chat and a resumed chat; do not
assume a particular Restart menu exists. In both, confirm skill discovery from
the chosen user scope and the actual native server version (`0.2.0rc4` for RC4).
Run project selection, a known symbol search and source-bound navigation in a
regular checkout and an actual managed worktree. Worktree queries must use that
worktree's GPR/source paths and its dependency/scenario context. A result pointing
at the main checkout is not worktree acceptance. Check lifecycle/cleanup through
the available client evidence and Doctor; report what remains unverified.

For another client, follow its own supported local stdio configuration using
the reviewed launcher command/arguments. This TOML is not Claude or OpenCode
configuration. Other native clients remain in development;
verify actual discovery, GPR-bound queries and disconnect/EOF cleanup in each
client. The query helper above is available independently of native integration.

## Native clients and host boundaries

| Client or host | First-install guidance | Acceptance boundary |
| --- | --- | --- |
| Local Codex skill | Install once in `~/.agents/skills/ada-development`; verify discovery after reopening. Repository scope is optional. | Supplied RC4 records retain user-wide installation and report discovery with Spawn; a fresh-session skill inventory is not bundled. Discovery alone does not register native tools. |
| Codex native MCP | Generate a new fragment, back up and explicitly merge into the user config, then fully quit/reopen Desktop and check new/resumed chats. | Bounded RC4 evidence on Desktop 26.1111.21308 build 27194 covers Spawn main and a managed worktree with external Anet. Other versions/CLI need their own checks. |
| macOS host | Check Python/Bash, Linux/AMD64 emulation, Docker sharing of every physical root, permissions and GUI PATH. | Supplied macOS 26.5.1 (25F80) arm64 evidence covers Docker Desktop's tested setup, two read-only parents and GHCR default acquisition. Other Mac/Docker setups need checks. |
| Claude native MCP | Follow that Claude client's own supported local stdio registration/configuration. Use the reviewed binding's launcher command/arguments only where that client supports them; the generated TOML is not a Claude configuration. | Development only; no Claude registration command or native lifecycle acceptance is provided. |
| OpenCode native MCP | Follow the installed OpenCode version's supported MCP configuration and process lifecycle. Adapt the reviewed launcher command/arguments to that format explicitly; the generated TOML is not an OpenCode configuration. | Development only; no OpenCode registration command or native lifecycle acceptance is provided. |

For every native client, enumerate its actual tools, select the real GPR view,
run source-bound queries and verify disconnect/EOF cleanup in that client.
The public plugin cannot add native server configuration that it does not
contain. The server's 19 advertised tools do not promise support for every tool;
the distribution's 16-tool native read policy and [support matrix](support.md)
still apply. The [assessment](assessments/macos-codex-rc4.md) distinguishes the
project-local Arca run from user-wide Spawn runs and records the evidence limits.
It establishes neither all-tool functionality nor concurrent different-branch
queries. Native-host ALS and fresh Cloud registration remain in development.

RC1 installations remain pinned to these bytes; there is no automatic updater.
Evaluate a future release deliberately with its own trusted hashes and new
runtime/binding paths. This guide does not modify the immutable RC1 artifacts.
The [update guide](updating.md) describes RC2-or-later notices, fresh searches
and user-approved agent execution with rollback. RC1 has no notice hook; use
the [initial upgrade prompt](#install-or-upgrade-to-rc2) only after the target
release is actually published.

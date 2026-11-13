# First installation

Use the published **0.2.0-rc.1 pilot prerelease** to evaluate the pinned Ada MCP
workflow. It runs Ada Language Server in a Linux/AMD64 Debian Trixie container;
read the [support limits](support.md) before choosing a host or client.
You need no private publisher plugin ID, public plugin-directory listing or
self-operated service. GitHub Releases supplies the artifacts.

Choose one entry path:

- **Direct MCP:** [acquire the released tooling](#acquire-the-tooling-for-direct-mcp-or-local-codex),
  [create a shared binding and query your project](#shared-docker-binding-and-first-queries),
  or [prepare a stdio client connection](#connect-a-stdio-mcp-client). No skill,
  private plugin or Plugin Creator is required.
- **Optional Managed Cloud skill:** use the copyable prompt below with an available Plugin
  Creator to save your own private copy of the skill plugin, then acquire and
  run its pinned tooling in a suitable environment.
- **Optional local Codex skill:** after acquiring the same tooling, install its
  skill in an explicit project scope. This path does not need Plugin Creator.

Native MCP integrations retain the client-specific development boundaries
below. A skill installation does not register native MCP tools. Users of Ada
MCP need no build or CI run of this repository; their own Ada project's normal
compiler/test workflow remains separate.

## Published RC1 artifacts

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

Prerequisites are Git, Python 3.11+, Bash 3.2+ and a working Docker daemon able
to run Linux/AMD64 containers. Run host commands as a nonroot user with Docker
access. Actual macOS host acceptance remains in development. Choose physical
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
Use its existing helper to publish a new skill link
in the actual Codex project's supported `.agents/skills` discovery directory:

```sh
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py install-skill \
  --destination /absolute/ada-workspaces/project/.agents/skills/ada-development
```

The helper verifies and copies the skill into separate storage, prepares only
the launcher's user execute bit, and creates a no-replace symlink at that
destination. It preserves existing entries. Start a new Codex session in that
project and confirm discovery of `ada-development` from that path; invoke
`$ada-development` when needed. Follow your Codex version's supported discovery
and session flow. Installing files alone does not prove discovery in a running
session or register native MCP tools.

The runtime and host binding below can serve several repositories. To expose
the skill in another project, choose that project's own new discovery path.
This procedure does not edit global client configuration or change `HOME`,
`CODEX_HOME` or the Docker daemon/context configuration.

## Shared Docker binding and first queries

Select a physical parent that contains your actual projects, dependency roots
and future worktrees. Add another `--root` for dependencies outside that parent.
Roots are mounted read-only at the same absolute paths. The image runtime uses
your nonzero numeric identity, private HOME, no network and dropped capabilities.
See [host setup](setup.md) for reserved paths, permissions and timeout details.

```sh
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py bootstrap \
  --binding /absolute/new-ada-binding.json \
  --root /absolute/ada-workspaces \
  --image-cache /absolute/new-private-image-cache \
  --output /absolute/new-bootstrap-evidence
python3 /absolute/new-private-ada-runtime/scripts/ada_mcp_setup.py doctor \
  --binding /absolute/new-ada-binding.json \
  --output /absolute/new-doctor-evidence
```

Bootstrap already runs Doctor before publishing the new binding. The second
command shows how to check it in later sessions. Each evidence directory must
be new. Bootstrap may download/load the pinned image; it preserves the current
Docker selection unless you explicitly pass `--docker-host` or `--docker-context`.
In a managed environment, use the actual supported daemon endpoint if its
default is unavailable; do not guess or globally change Docker configuration.
Existing bindings are immutable. Restore their recorded image with Bootstrap
and no overrides, or choose a new binding when changing roots or host selection.

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
TOML. Review the fields supported by your installed Codex version, explicitly
merge them through its supported configuration and reconnect. The helper
creates only a new fragment; it does not install or activate native tools.

For another client, follow its own supported local stdio configuration using
the reviewed launcher command/arguments. This TOML is not Claude or OpenCode
configuration. Native registration and runtime behavior remain in development;
verify actual discovery, GPR-bound queries and disconnect/EOF cleanup in each
client. The query helper above is available independently of native integration.

## Native clients and host boundaries

| Client or host | First-install guidance | Acceptance boundary |
| --- | --- | --- |
| Local Codex skill | Use project-scoped `install-skill` above and confirm discovery in a new session. The skill invokes the command-line query helper. | Skill discovery does not register native MCP tools. |
| Codex native MCP | `native-config --binding FILE --output NEW.toml` produces a separate Codex-style `[mcp_servers.ada]` TOML fragment. Review fields supported by your installed version, explicitly merge it through the client's supported configuration and reconnect. | Development only; generation is not registration, query or lifecycle proof for CLI/Desktop. |
| macOS host | Check actual Python/Bash availability, Linux/AMD64 emulation, Docker Desktop/Colima sharing of every physical root, numeric permissions and GUI PATH. | Development only; Linux UID/GID `501:20` evidence does not establish Mac behavior. |
| Claude native MCP | Follow that Claude client's own supported local stdio registration/configuration. Use the reviewed binding's launcher command/arguments only where that client supports them; the generated TOML is not a Claude configuration. | Development only; no Claude registration command or native lifecycle acceptance is provided. |
| OpenCode native MCP | Follow the installed OpenCode version's supported MCP configuration and process lifecycle. Adapt the reviewed launcher command/arguments to that format explicitly; the generated TOML is not an OpenCode configuration. | Development only; no OpenCode registration command or native lifecycle acceptance is provided. |

For every native client, enumerate its actual tools, select the real GPR view,
run source-bound queries and verify disconnect/EOF cleanup in that client.
The public plugin cannot add native server configuration that it does not
contain. The server's 19 advertised tools do not promise support for every tool;
the distribution's read-only policy and [support matrix](support.md) still apply.

RC1 installations remain pinned to these bytes; there is no automatic updater.
Evaluate a future release deliberately with its own trusted hashes and new
runtime/binding paths. This guide does not modify the immutable RC1 artifacts.
The [update guide](updating.md) describes the unreleased notice feature, fresh
searches and user-approved agent execution with rollback. RC1 has no notice
hook; enabling it requires an initial approved upgrade after a notifier-capable
release is actually published.

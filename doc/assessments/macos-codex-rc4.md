# RC4 Mac and user-wide Codex acceptance

## Evidence and scope — 2026-11-19

The supplied `ada-mcp-macos-acceptance-20261119` evidence set contains a report,
environment metadata and curated setup, Desktop and GHCR JSON extracts.
Its ZIP SHA256 is
`d68c917c869160e2d283d9fc99f42ec319591503aa0d4f22b97aaceb6f538488`;
all 16 files listed by its checksum manifest were verified. These are supplied
curated arguments/results with original record locators, not independently
rerun Mac tests or a complete set of raw logs. Some batch extracts share record
locators; they do not establish independent raw request/response pairing.
Private paths, transcript identifiers and the raw bundle are not published here.

| Component | Recorded identity |
| --- | --- |
| Host | macOS 26.5.1 (25F80), arm64 |
| Client | Codex Desktop 26.1111.21308, build 27194 |
| Runtime | Ada MCP 0.2.0-rc.4; MCP handshake `0.2.0rc4`, protocol `2025-06-18` |
| Runtime source | `7864cda95a5dfc264926a5110416196279ff957c` |
| Container | Docker Desktop, Linux/AMD64, Debian Trixie; UID:GID 501:20 |
| Arca main | `20564468d00024e6f949e92c1da79850abf59086` |
| Spawn main and detached managed worktree | `4611adb26fbcc8dffac0db74a36e0a76634780e5` in both |

This documentation topic starts at the runtime source above and changes no
runtime code or version. Later maintained instructions do not modify published
RC4 tooling/full-skill archives or already installed authenticated files.

## Installation and native queries

The initial project-local setup did not provide the intended shared scope.
The supplied migration records establish a no-replace user-wide skill link at
`~/.agents/skills/ada-development`, a user-native configuration, persistent
runtime selection and new bindings. An initial per-checkout root list needed
the separate Codex worktree parent added. The final binding consolidates access
to two user-approved physical parents: the development workspace and the actual
client-managed worktree root. Doctor reports both readable, mounted read-only
at identical absolute source/destination paths, with private writable HOME,
read-only root filesystem, no network, dropped capabilities, successful MCP
initialization and confirmed container removal after EOF.

The supplied report describes user-wide skill discovery. The bundle retains
installation/activation metadata, native registration and direct native queries,
but no standalone fresh-session discovered-skill inventory or skill-use
transcript. Discovery is therefore reported rather than independently
inspectable from these extracts; native query results remain directly retained.

The server advertises 19 tools; native configuration permits 16 read tools.
That is a catalog/policy observation, not functional acceptance of all tools.
The retained calls establish these bounded results:

- Arca used **project-local** native registration before user-wide migration.
  `arca.gpr`, no extra search paths and `ARCA_BUILD_MODE=validation` selected
  its view. `Copy_File_To_Stream` returned two complete, nontruncated symbol
  results: `src/arca-binary_io.ads:15:14` and `.adb:46:14`. Definition and
  implementation navigation agreed with the extracted source; references and
  incoming-call replies identified the CPIO/TAR callers. The source declares a
  procedure; the response's `kind=function` is its normalized LSP category.
  The existing `procedure` and `function` filters both accept FUNCTION/METHOD,
  rather than reconstructing an Ada-specific procedure/function distinction.
- Spawn main and the Codex-managed worktree used **user-wide** native
  registration, with reported user-wide skill discovery, and their own
  `spawn_manager.gpr`, external Anet search path,
  `BUILD=prod`, `OS=linux`, `TARGET_ARCH=x86_64`, `VERSION=""`. Searches for
  `Locate_Exec_On_Path` returned four complete, nontruncated results: two GNAT
  runtime locations and the selected checkout's `src/spawn-utils.ads:36:13`
  and `.adb:61:13`. Navigation from `tools/spawn_manager.adb:131:55` reached
  the declaration and implementation in the selected checkout.
- After two-parent consolidation, a resumed native session again selected the
  managed worktree and returned those four symbols with worktree coordinates.
  Handshake extracts cover new and resumed Desktop chats. Repeated exact-view
  project info observed indexing become ready without requesting refresh.

## Default GHCR acquisition and recovery

Before the test Bootstrap, the pinned image, inventoried RC4 references and
test image-cache entries were absent. Bootstrap used no explicit transport
override, selected `ghcr.io/abuild-project/ada-mcp-server:v0.2.0-rc.4` and
reported registry transport without archive fallback. Three runtime layers
were downloaded; one was already present, so the entire Docker layer cache
was not cold.

Identity validation distinguished OCI index/executable target
`sha256:f0a2568632320bb06774bf342ebf46c0f15ec83aa469abe9c91733d5ffac7106`
from canonical config
`sha256:cfc9a5f2bec4ce97f5236e339894d252c8db927b0b89af2be0e49fefdc2595f6`.
Bootstrap/Doctor passed and confirmed cleanup. Recovery records authenticate
an archive before a warm load, restore the original image references and show
unchanged active config/selection/binding/runtime/skill fingerprints. The test
binding stayed inactive; a final Doctor passed with the original active binding.
This is not an injected registry-failure/archive-fallback test.

## Limits

The bundle establishes neither compiler CI nor a full native-tool matrix.
Spawn's two checkouts share one commit, so different-branch concurrency is
unproven. Anet is an external dependency of those views, but its revision/source
hashes are absent; the bundle does not pin a fully reproducible dependency
snapshot. Other host/client versions, Colima, native-host ALS, Claude/OpenCode
and fresh managed Cloud registration need their own acceptance. Existing
[support limits](../support.md) remain in force beyond the results above.

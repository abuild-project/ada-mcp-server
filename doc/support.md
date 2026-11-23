# Support and evidence matrix

Version: pilot prerelease `0.2.0-rc.6` (Python `0.2.0rc6`). The table defines
its acceptance scope; new artifacts still require the documented checks at
their exact immutable revision. The
[published RC1 release](https://github.com/abuild-project/ada-mcp-server/releases/tag/v0.2.0-rc.1)
has verified public asset downloads and hashes; see the maintained
[first-install guide](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/first-install.md).
A version in source or CI alone does not establish public availability or
acceptance of an untested client.
It does not reuse the old pilot image as evidence for this server revision.
Python 3.11 is the minimum syntax/runtime requirement, not a claim that every
Python version/platform combination was accepted. The complete server chain
uses the container's Python 3.13; host setup records its actual Python version.

| Candidate contract | Required repeatable evidence | Limits |
| --- | --- | --- |
| Linux/AMD64 Trixie, GNAT 14, pinned GPRbuild/ALS | docker/build, docker/check, runtime package/license index | No host-compiler substitute; other architectures in development |
| Exact GPR/search-path/scenario view selection | inherited pool tests, real ALS probe and host acceptance | Prerequisites/generated GPR inputs must exist |
| Selected ancestor GPR retained below nested projects | tests/test_als_pool.py and real parent-view probe | Explicit alternate selection changes the view |
| Anchored project/symbol/definition/hover queries | real ALS/MCP and Arca plus Spawn/Anet acceptance | Check complete/nontruncated results against source locations |
| Complete file diagnostics | required real error/repair/error control with source locations and stable MCP/ALS IDs, plus host acceptance | Per-file ALS publications; not complete compiler/project validation |
| Immutable acquisition, archive/image identity and host provisioning | tests/host plus generated-artifact host acceptance | Warm cache identified; registry transport independently gated |
| Numeric users 1000:1000 and 501:20, readonly isolated runtime | host acceptance with fresh readable source copies | Linux identity evidence does not prove Mac sharing/emulation |
| EOF/exit/container removal | exact-name inspect receipts in host acceptance | Unknown state fails; no broad cleanup |
| Versioned package/skill/image correspondence | scripts/artifacts.py and metadata/version tests; published RC1 public asset/hash verification | Later releases need their own publication and consumer checks |

## Project readiness and tool support

### Tool reference

The query helper from your installed runtime shows the full server catalog
and each tool's argument schema. Run it with the matching binding.

```sh
python3 /path/to/runtime/scripts/ada_mcp_setup.py query \
  --binding /path/to/ada-binding.json tools
```

The JSON `tools` array contains the server's `tools/list` results, including
each tool's `inputSchema`. The repository declares the catalog in
[`list_tools` in `src/ada_mcp/server.py`](https://github.com/abuild-project/ada-mcp-server/blob/main/src/ada_mcp/server.py#L457).

- **Codex Desktop** can call the 16 tools listed in the generated native
  entry's `enabled_tools` setting.
- **Managed Cloud and direct Docker** use the Docker query helper. The Cloud
  skill runs it for you. The helper lists all 19 server tools and limits
  calls to the 16 names in `client_read_tools` plus rename proposals with
  explicit `preview=true`.

The supported workflow covers project selection, symbol queries, definition
and hover lookups, and per-file diagnostics. Catalog entries for references,
implementations, call hierarchy, dependency graphs, completions, signatures,
code actions and spec selection remain in development beyond their individual
test coverage. Applying renames, formatting, builds and Alire integration are
outside the supported workflow.

### Project readiness

For `ada_project_info`, `complete=true` means that the requested GPR metadata
and source membership were evaluated successfully. The separate Boolean
`indexing_complete` confirms observed, quiescent indexing; false means pending
or not yet confirmed. Pending indexing does not invalidate a valid selected
client. Optional Boolean `refresh` defaults to false: repeated exact-view
requests observe readiness without reloading. True reevaluates changed GPR/source
membership on a reused client; a new exact client is already fresh. Use the
advertised guarded `ada_workspace_symbols` path with a known actual source/symbol,
honor `complete`/`truncated` and bound retries without reselecting or refreshing.
Other tools do not all wait or provide completeness fields. Project selection
no longer waits on the former 25-second indexing gate; the 30-second per-ALS-RPC
timeout and 25-second guarded semantic wait remain. The supplied
[post-publication Mac acceptance](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/macos-codex-rc4.md) is separate
from the optional [larger-project timing assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/project-selection-timing.md).

The [additional-tool regression assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/additional-tool-capabilities.md)
adds bounded internal evidence without expanding this support matrix. Three
positional active-parameter results from the pinned ALS remain incorrect and
explicitly unaccepted; named-argument checks do not hide them. See the
[upstream report](https://github.com/AdaCore/ada_language_server/issues/1310).
Native rename
application is unsupported: `preview=false` returns an explicit failure with
no changes and `applied=false` before rename synchronization or native rename
requests. The shared server connection may already be initialized. The shipped
client continues to require explicit rename preview and deny build/formatting
calls. Owned compiler, formatting
and manifest probes do not establish a consumer editing or Alire workflow.

## Earlier client observations

A supplied managed Cloud batch of 15 concrete requests and results was
independently checked against Arca source commit
`20564468d00024e6f949e92c1da79850abf59086`. The selected GPR/scenario,
symbol/navigation coordinates and both reference sets agreed with that source;
four explicit file-diagnostic replies reported `complete=true`, `scope=file`
and no diagnostics. This is bounded evidence for that reported skill/query-client
workflow, not independent ALS replay or compiler success. The execution text
is a summary; full raw process, protocol, Bootstrap, Doctor and command logs
were not supplied. It adds no new process/isolation/cleanup certification to
the separately retained published CI/runtime evidence and does not expand
tool-wide support from individual results.

The RC2-or-later host update checker supplies advisory initialization/project
metadata and a [user-approved update/rollback path](updating.md). Published RC1 has
no notifier and needs an initial approved upgrade to a published RC2 or later. The notice mechanism does not move pins, download executables
or give the server network access. Protocol delivery does not establish how an
untested native frontend renders or relays a notice to its user.

The RC3-or-later selection-aware entry can reuse an authenticated compatible
runtime without skill/plugin replacement. This workflow contract is separate
from semantic support and requires actual published metadata; RC1/RC2 manifests
remain legacy. See [selection and activation](updating.md#keep-the-entry-and-runtime-independent).

Supplied 2026-11-19 RC4 acceptance covers macOS 26.5.1 (25F80) arm64 with Codex
Desktop 26.1111.21308 build 27194 and Docker Desktop's Linux/AMD64 Trixie runtime,
source `7864cda95a5dfc264926a5110416196279ff957c`. Curated extracts record user-wide
skill installation/native registration, Spawn main and a Codex-managed worktree
with external Anet, two consolidated read-only parent mounts, RC4 handshakes
in new/resumed chats, and default GHCR acquisition with Doctor/cleanup. User-wide
skill discovery is reported; a fresh-session discovery inventory or skill-use
transcript is not bundled. Native query excerpts directly retain their results.
The separate Arca native run used project-local registration before migration.
The native policy permits 16 tools; the server catalog lists 19. Neither count
establishes all-tool functionality. Both Spawn checkouts used the same commit;
different-branch concurrency and compiler CI were not tested by this bundle.
These are supplied curated results, not independently rerun Mac logs. See the
[sanitized assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/macos-codex-rc4.md)
for archive identity, source coordinates, LSP category normalization and limits.
Later supplied RC4-to-RC5 observations cover a scoped PATH correction and
cached notice. See the [host Python guidance](updating.md#host-python-and-native-update-policy).

## RC6 consumer observations

The [RC6 consumer assessment](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/assessments/rc6-consumer.md)
records the supplied offline Mac check, restarted Desktop connection and
fresh Managed Cloud task using a retained runtime. The checks cover the
reported configurations and requests. Fresh Mac chat and visual skill
discovery, Cloud cold acquisition, third-party import and native Cloud
registration remain separate checks.

## Other hosts and clients

Other macOS/client versions, Colima, native-host ALS, Claude, OpenCode and
separate-account private plugin import remain in development until tested
directly. Native Cloud registration and other accounts' runtime
behavior require their own evidence beyond the reported workflow and public
artifact-byte access. The reported Mac registry acquisition covers the tested
RC4 and RC6 configurations. Other releases and hosts need their own evidence.
Local CLI discovery or a temporary app-server proves neither the current Cloud
catalog nor another client's behavior. Configuration examples prepare those
tests rather than promising compatibility.

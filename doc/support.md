# Candidate support and evidence matrix

Version: pilot prerelease candidate `0.2.0-rc.3` (Python `0.2.0rc3`). The table defines
its acceptance scope; the exact immutable revision must pass the documented
checks before approval. The
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

For `ada_project_info`, `complete=true` means that the requested GPR metadata
and source membership were evaluated successfully. The separate Boolean
`indexing_complete` confirms observed, quiescent indexing; false means pending
or not yet confirmed. Pending indexing does not invalidate a valid selected
client. Semantic queries retain their own completeness checks. Larger-project
Mac selection latency remains pending under the
[before-release measurement](assessments/project-selection-timing.md).

The server advertises 19 tools. The read-only client policy permits 16 tools
and explicit rename preview, but the catalog alone does not prove correctness
or support for all those functions. References, implementations, call hierarchy,
dependency graphs, completions, signatures, code actions and spec selection
remain in development beyond their individual unit/probe coverage. Write
rename, formatting, build and Alire integration are not supported by this
read-only distribution workflow. They are never described as safe substitutes
for review or compiler CI.

The [additional-tool regression assessment](assessments/additional-tool-capabilities.md)
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

Actual macOS/Apple Bash/Docker Desktop/Colima, native Mac MCP registration,
Claude, OpenCode and separate-account private plugin import remain in development
until tested directly. Native Cloud registration and other accounts' runtime
behavior require their own evidence beyond the reported workflow and public
artifact-byte access. Registry image execution likewise needs its own evidence.
Local CLI discovery or a temporary app-server proves neither the current Cloud
catalog nor another client's behavior. Configuration examples prepare those
tests rather than promising compatibility.

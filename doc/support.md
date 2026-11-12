# Candidate support and evidence matrix

Version: coordinated candidate `0.2.0-rc.1` (Python `0.2.0rc1`). There is no
public release yet. The table defines the acceptance scope for this candidate;
the exact immutable revision must pass the documented checks before approval.
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
| Versioned package/skill/image correspondence | scripts/artifacts.py and metadata/version tests | Publication and public acquisition are later gates |

The server advertises 19 tools. The read-only client policy permits 16 tools
and explicit rename preview, but the catalog alone does not prove correctness
or support for all those functions. References, implementations, call hierarchy,
dependency graphs, completions, signatures, code actions and spec selection
remain in development beyond their individual unit/probe coverage. Write
rename, formatting, build and Alire integration are not supported by this
read-only distribution workflow. They are never described as safe substitutes
for review or compiler CI.

Actual macOS/Apple Bash/Docker Desktop/Colima, native Mac MCP registration,
Claude, OpenCode, a fresh managed Cloud task using public release artifacts,
registry pulling and anonymous public GHCR access remain in development until
tested directly. Local CLI discovery or a temporary app-server proves neither
the current Cloud catalog nor another client's behavior. Configuration examples
prepare those tests rather than promising compatibility.

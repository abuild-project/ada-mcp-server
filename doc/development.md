# Development and validation

Read AGENTS.md and the active plan before editing. Use topic branches and the
coordinator/developer/tester/independent-reviewer workflow described there.
The developer makes modest targeted checks; the tester runs the complete chain
from a fresh detached worktree of the immutable candidate. Review includes all
changes since imported revision `961f532bcc633189e8618852732be289752cbcd7`,
including the independent import README on main.

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

For fast development only, a local venv may run a targeted check:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements/development.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pytest tests/test_als_pool.py -q
```

These host checks are labeled as development evidence; they do not replace the
container chain. Update input requirements and regenerate the hash lock
deliberately. Python package notices and exact Debian/ALS versions are retained
in the image's component index; see licensing.md.

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

## Release and hosted review

Prepare coherent unpublished commits before the first submission. The change
record supplies the final PR description. Hosted CI must test the same head;
read all Copilot feedback and preserve the separate PR correction counter.
Stop at the checked PR until merge/release permission is supplied.

Release promotion uses the already tested CI artifacts and source/image hashes;
it must not rebuild an untested replacement. GitHub Releases/GHCR publication
is prepared separately and is not performed by ordinary CI. GHCR packages may
start private even for a public repository. A later release needs an explicit
visibility decision and an anonymous manifest/pull proof before public
availability is claimed. Authenticated pulls do not prove anonymous access.
The account plugin and future fresh-Cloud deployment follow only after actual
public artifacts exist. See release.md for the manual promotion gates.

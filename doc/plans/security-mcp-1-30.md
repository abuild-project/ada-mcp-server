# Patched MCP 1.x dependency baseline

Base revision: `253612372be43ead2aa28edfddad4663821902db`.

## 2026-11-13: Scope and maintainer decision

The maintainer approved a separate SDK 1.30.0 maintenance topic before the
first pilot release, conditional on the complete existing checks passing.
Require `mcp>=1.30.0,<2` in the public package metadata and pin `mcp==1.30.0`
in the shared runtime input. Regenerate the single development hash lock,
preserving other accepted versions and hash sets unless the SDK's actual
dependency constraints require a documented change.

Retain coordinated project version `0.2.0-rc.1` and Python `0.2.0rc1`;
no release or tag has been published. This topic does not adopt SDK 2,
change server implementation or add supported HTTP/native-client paths.
The already accepted dependency topics and their immutable evidence remain
separate from this new dependency-floor decision.

## 2026-11-13: Advisory and reachability boundaries

The four upstream advisories cover
[HTTP session retention](https://github.com/advisories/GHSA-84m7-p3x7-pcfv),
[token audience validation](https://github.com/advisories/GHSA-w4fh-qvv9-3v23),
[external schema references](https://github.com/advisories/GHSA-rwrf-2pqf-9j8j)
and [cross-origin HTTP redirects](https://github.com/advisories/GHSA-5h93-6whr-6q8j).
They name 1.30.0 as the patched 1.x baseline. The previous 1.28.1 dependency
is within the affected package-version ranges.

The accepted server uses stdio and the bundled command client uses its own
JSON-RPC process pipes. It does not expose the affected SDK HTTP session/auth
or HTTP client routes, nor the SDK client's external-output-schema validation.
Do not describe the package update as a repair of a demonstrated product
exploit or as proof that unsupported HTTP wrappers are safe. If HTTP bearer
authentication is introduced later, resource/audience validation still needs
its explicit configuration; updating the SDK alone does not enable it.
Do not dismiss owner-visible alerts or claim their closure without evidence.

## 2026-11-13: Preparation and acceptance

Use the existing uv 0.13.5 resolver with CPython 3.13.5, targeting Linux/AMD64,
and prefer current output pins except for MCP. This generates metadata/hashes;
it does not install or test the server and is not a substitute Ada environment.

```sh
uv pip compile requirements/development.in --generate-hashes \
  --python python3.13 --python-platform x86_64-unknown-linux-gnu \
  --no-python-downloads --only-binary=:all: \
  --upgrade-package mcp --output-file requirements/development.lock
```

Prepare a coherent immutable candidate, change record and sorted index entry.
The integrator-facing changelog identifies the new minimum SDK version.
Preserve the canonical version, builtin Python-version provider, strict
distribution/image receipts, support boundaries and existing tests.

The tester must validate the new exact source in the unchanged Hosted AMD64
Trixie docker/build and docker/check chain, including actual installed MCP
1.30.0, tests, coverage, style/typing, packages, documentation, real ALS/MCP
controls and both numeric identities. Independent review and current-head
Copilot assessment precede normal merge. Earlier 1.28.1 receipts and green
tests are not acceptance evidence for 1.30.0.

After acceptance, select the new resulting main's successful push CI and
artifacts, repeat the promotion plans and regenerate consumer/plugin pins.
Retain the previous release/plugin packets as historical evidence; never
relabel them as outputs of the new source or rebuild a replacement during
publication. Local Docker/cache/global changes and weaker Ada environments
are outside this preparation.

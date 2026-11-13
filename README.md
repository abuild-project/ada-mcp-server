# Ada MCP Server

The independent [abuild-project](https://github.com/abuild-project) continuation
of [MDBrothers/ada-mcp-server](https://github.com/MDBrothers/ada-mcp-server)
connects Ada Language Server to the Model Context Protocol. It retains the
selected personal fork's history, authorship and MIT notices, with its own
maintenance, release and support decisions.

Coordinated version **0.2.0-rc.1** (Python **0.2.0rc1**) is a **pilot prerelease**,
with the scope and limits in its [release notes](doc/releases/0.2.0-rc.1.md).
The `main` branch contains development sources. Check
[GitHub Releases](https://github.com/abuild-project/ada-mcp-server/releases)
for actually published tags and their verified artifacts; source preparation
and CI artifacts alone do not constitute a public release. GitHub Releases
and GHCR are the distribution channels; PyPI publication is outside this scope.
The imported source is `961f532bcc633189e8618852732be289752cbcd7`; its explicitly
selected ancestor-GPR behavior is retained and tested again here.

The candidate workflow selects actual GPR files, dependency paths and scenarios,
then performs anchored project/symbol/navigation queries and synchronized file
diagnostics in a pinned Linux/AMD64 Trixie container. Diagnostics are ALS file
publications, not a replacement for compiler/test/coverage CI. The 19 advertised
tools do not imply support for every tool; see the explicit
[support and evidence matrix](doc/support.md).

## Development setup

From the checked source revision, with Docker already available:

```sh
docker/build --tag ada-mcp-server:candidate
docker/check ada-mcp-server:candidate
```

This standalone build uses an official immutable Trixie base, GNAT 14,
GPRbuild, pinned ALS and hash-locked Python dependencies. It needs no private
Abuild checkout or old pilot image. [Development instructions](doc/development.md)
cover Cloud CA trust, the complete CI chain, artifact generation and the two
numeric-identity host checks.

The generated distribution separates the complete, hash-verified tooling and
image archives from a lightweight skill plugin. The skill carries an ordinary
HTTPS acquisition path pinned to concrete artifact hashes; it does not require
owner-only Plugin Creator access or unsupported remote script-resource reads.
Those public URLs become usable only after an approved release actually exists.
For current locally generated artifacts, use the [explicit host setup](doc/setup.md).

Host configuration is shared across repositories while project views remain
in their existing GPR files. The launcher preserves same-path read-only roots,
nonroot identity, no runtime network, dropped capabilities and private HOME.
It never silently overwrites existing bindings or global client/Docker config.

Actual macOS, Claude/OpenCode/native-client behavior, registry/public access and
fresh managed Cloud acquisition remain in development until directly verified.
Generating a configuration or discovering a local skill is not a proof of
another frontend's native registration.

## Maintenance and provenance

- [Agent/contributor rules](AGENTS.md)
- [Licensing and immutable origins](doc/licensing.md)
- [Prepared release promotion](doc/release.md)
- [Public repository and release assessment](doc/assessments/public-release.md)
- [Changelog](CHANGELOG.md) and [roadmap](ROADMAP.md)
- [Change records](doc/change-records/README.md)
- [Historical import records](doc/history/README.md)

Own code uses [MIT](LICENSE). Container components retain their own license
terms, notices and source obligations. The source/version/component index is
included in the image and generated artifacts. Publishing, merging or updating
the existing account plugin requires a separate maintainer decision.

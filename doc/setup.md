# Host setup and project views

For first installation or an approved upgrade, start with the maintained
[first-install guide](https://github.com/abuild-project/ada-mcp-server/blob/main/doc/first-install.md).
It covers a reader-owned private Cloud skill-plugin copy and local Codex setup
using the existing released helpers. This page supplies detailed host-binding
rules and locally generated artifact setup. The RC1 archives retain their
original documentation; the maintained guide does not replace release bytes.
See [release checks, approved updates and rollback](updating.md) for the
RC2-or-later notifier and the initial approved upgrade needed by RC1 installations.

The candidate requires Python 3.11+, Bash 3.2+ and an existing Docker daemon.
Its validated container target is Linux/AMD64 Debian Trixie with GNAT 14,
GPRbuild and the pinned Ada Language Server. macOS, native client registration
and other client applications remain in development until their own tests pass.

The [published RC1 release](https://github.com/abuild-project/ada-mcp-server/releases/tag/v0.2.0-rc.1)
provides verified public assets and version-specific artifact metadata.
During development, use
the artifacts generated from the checked source revision by scripts/artifacts.py.
Future GitHub Releases/GHCR paths in generated candidate metadata remain
distribution targets until their publication and access are verified.

## Select a compatible runtime

The RC3-or-later selection-aware entry requires an actually published release.
Public RC1/RC2 archives have no workflow contract or selection command. A
compatible entry first resolves its private pinned selection and uses that runtime/binding
for setup, queries and update checks. Later sessions need the same retained
files and default/custom locator; a custom --file does not persist a pointer.
Entry package version is not server version.
See [entry/runtime selection](updating.md)
for the exact compatibility check, trusted embedded-acquirer invocation, fresh
Cloud bootstrap and guarded activation/rollback. Unknown contracts require an
entry update; do not silently fall back to old pins. Native client activation
remains a separate explicit supported configuration/reconnect.

## Acquire the complete tooling

The lightweight skill includes an acquisition script and the concrete version,
URL, archive SHA256 and runtime-manifest SHA256 generated with the tested
artifact. It downloads the full tooling without Plugin Creator owner access
or remote Python/JSON resource reads. It never pipes unchecked content to a
shell. The complete archive is checked before reading its manifest, and every
declared file is checked before materialization or execution. Links, special
members, duplicate names, path aliases and undeclared files are refused.

For locally generated artifacts, the same source acquisition command is:

```sh
python3 tooling/acquire.py --archive /absolute/release/tooling.tar.gz \
  --sha256 TRUSTED_ARCHIVE_SHA256 --manifest-sha256 TRUSTED_MANIFEST_SHA256 \
  --destination /absolute/new-private-runtime
```

Replace the illustrative filenames/hashes using the actual generated manifest.
The destination must be new. All files start mode 0644 inside private directories;
after complete verification only `scripts/ada-mcp-launch` gains user execute.
The Python helpers run via Python. A successful Doctor through Bash alone does
not prove that Query's direct launcher execution has the correct permission.

## Create one explicit host binding

```sh
python3 /absolute/runtime/scripts/ada_mcp_setup.py bootstrap \
  --binding /absolute/new-binding.json --root /absolute/ada-workspaces \
  --image-cache /absolute/private-image-cache --output /absolute/new-setup-log
```

The generated runtime manifest supplies the immutable config digest and the image
archive's exact versioned URL, byte size and SHA256. Unreleased tooling defaults
to pulling `ghcr.io/abuild-project/ada-mcp-server:v<project-version>` when the
locked local target is absent. The version tag only locates the bytes: before
execution, setup verifies their canonical config digest, platform, source and
version against the authenticated runtime lock. A successful pull followed by
an inspection/export/identity failure stops setup without an archive fallback.

If the pull fails or times out, setup uses the locked archive in `--image-cache`,
downloading it only when needed. Without that option, macOS uses
`~/Library/Caches/ada-mcp/images`; Linux uses `$XDG_CACHE_HOME/ada-mcp/images`
when `XDG_CACHE_HOME` is absolute, otherwise `~/.cache/ada-mcp/images`.
Empty or relative XDG values are ignored. The resolved absolute cache path
is retained in the binding. Existing bindings retain their paths and sources;
the defaults do not create directories until the cache is needed. A cached
archive is accepted only if its hash and size match; HTTPS downloads refuse
downgrade redirects and replacement. `--transport archive` explicitly selects
archive-only setup. The report retains the attempted commands and actual
transport/fallback. Warm default setup can reuse the already pinned target.
Existing bindings keep their recorded sources; no automatic migration occurs.
Previously published tooling retains its original transport behavior.

The automatic GHCR locator accepts the coordinated release forms `X.Y.Z` and
`X.Y.Z-rc.N`. Other version strings produce an actionable error suggesting
`--transport archive`. That override bypasses only the registry locator's
version check; archive integrity and acquisition/publication rules are unchanged.

Bootstrap also creates the local alias `ada-mcp-server:v<project-version>`
after Doctor succeeds, including when the image or binding already exists.
SemVer build metadata's `+` becomes `_` in this Docker tag. An alias already
pointing to that same target is reused. A different target is reported as
`image_tag.status: "conflict"` and left unchanged; unavailable or failed tag
operations are reported as `"error"`. These optional naming outcomes do not
block the verified installation or binding publication. The report records
the alias and its immutable target. Bindings and launchers continue using the
verified digest, and Doctor/query do not create tags. This applies to new tooling;
previously published release archives remain unchanged.

An explicit local `--archive FILE --archive-sha256 HASH` or full
`--registry registry.example.org/team/ada-mcp@sha256:DIGEST` is also supported.
These explicit source overrides do not use the automatic fallback. The example
registry string is not an existing service. A manifest/index digest differs
from the config digest. Runtime execution remains pinned to the verified target
even when the default registry locator is a version tag.
Archive import checks SHA256 and actual single-image Docker-save metadata before
load, including config-byte identity, Linux/AMD64 and layer references. The same
file descriptor is used for hash/metadata/load. Limits are 10,000 members,
1 MiB per manifest/index, 4 MiB total descriptor metadata, 64 metadata nodes,
eight graph edges in depth and 4 MiB config; no files are extracted to the filesystem.
A warm daemon cache is not proof that an unrelated archive contains the image.
Layer-content hashes are left to Docker; this is not an independent layer audit.

Config identity and the locally executable target are separate. A classic
store can execute the config ID; an OCI store can expose a manifest or index
ID instead. The version-2 host binding retains the canonical config lock and
a bounded SHA256/size-verified descriptor proof for the selected local target.
An optional OCI layout wrapper does not override the inspected native target:
hybrid exports can keep a config execution ID and carry a supplementary OCI
root, whose complete runtime graph is still validated. Config descriptor sizes
must match the actual canonical config byte count, retained in the proof and
bound to the trusted runtime metadata when a host binding is read.
After load/pull, Bootstrap exports that local target as data and verifies its
actual config and descriptor graph before running it. This additional check
handles store conversions without assuming that a config ID is executable.
Doctor, Query and generated native configuration use that same verified target.
Unsupported/missing/ambiguous graphs fail; platform/labels alone are no substitute.
Existing bindings are never migrated or overwritten. If a different store
requires another target, choose a new explicit binding.

Roots are physical absolute directories, mounted read-only at the same paths.
The launcher resolves each root with physical-directory semantics before any
Docker use and rejects aliases, including symlinked ancestor components and
symlinks to the filesystem root. Select the physical path reported by `pwd -P`.
Shared roots cannot equal, contain or sit below a reserved runtime path. The
required installation prefix is `/opt/ada-mcp`. A conservative system policy
also reserves `/bin`, `/sbin`, `/lib`, `/lib64`, `/usr/bin`, `/usr/sbin`,
`/usr/lib`, `/usr/lib64`, `/usr/libexec`, `/usr/local/bin`, `/usr/local/sbin`,
`/usr/local/lib`, `/usr/local/lib64`, `/usr/local/libexec` and `/etc` for executable,
library, loader and Python startup state. This is an explicit mount-placement
policy, not an inventory of currently active files. Broad ancestors such as
`/opt` and `/usr` overlap these prefixes and are refused. Component-disjoint
physical directories such as `/opt/my-project`, `/usr/local/src` and
`/opt/ada-mcp-extra` remain eligible; ordinary project paths are not globally
excluded merely for being below `/opt` or `/usr`.
Include dependency roots and parents for future worktrees. Additional roots
outside those parents need a new binding/server restart. Paths with spaces and
Unicode are supported; comma, double quote, newline and path aliases are refused.
UID/GID default to the caller and must be nonzero. Private HOME follows the
selected identity. `--uid 501 --gid 20` is a Linux numeric-identity test, not a
macOS proof. Test readable new copies instead of changing original permissions.

Docker's current host/context is retained unless `--docker-host ENDPOINT` or
`--docker-context NAME` is supplied. Explicit selectors clear conflicting
inherited host/context/TLS selection for that command only. The managed Cloud
host may require `--docker-host unix:///var/run/docker.sock`. Mac normally uses
its existing Docker Desktop/Colima context and must separately verify AMD64
emulation, filesystem sharing and GUI PATH.

The installed server uses isolated Python imports, so project-local Python
packages, user-site startup files and PYTHONPATH/PYTHONHOME cannot replace its
server or standard-library imports. The project remains the process cwd and
explicit GPR/search/scenario selection still controls Ada analysis. Isolated
imports and reserved mount placement work together: a shared directory must not
replace the interpreter, installed server, ALS or their startup libraries.
Verified host helper scripts retain their sibling-module imports; no host Python
installation or global configuration is changed.

## Doctor and actual queries

Binding reads use explicit `--binding`, otherwise `ADA_MCP_BINDING`, otherwise
the normal `~/.config/ada-mcp/binding.json`. Writes always require an explicit
new path. Existing bindings/configuration fragments are not overwritten.
`bootstrap --binding EXISTING` without overrides can restore its recorded image
source. No HOME/CODEX_HOME, Docker daemon/context or global client config changes
are made.

```sh
python3 /absolute/runtime/scripts/ada_mcp_setup.py doctor \
  --binding /absolute/binding.json --output /absolute/new-doctor-log
python3 /absolute/runtime/scripts/ada_mcp_setup.py query \
  --binding /absolute/binding.json --log-dir /absolute/new-query-log \
  batch /absolute/requests.json
```

The batch is an array of `{"tool":"ada_project_info","arguments":{...}}` objects.
Select the actual `gpr_file`, ordered `project_paths` and `scenario_variables`
before related file queries in the same batch. Existing GPR files remain the
project contract; host bindings are not a new repository configuration format.
Anchor workspace queries to an absolute `file` from the selected view. Inspect
`complete`, `truncated`, scope and source-bound coordinates. Unscoped cached
diagnostics are not a clean compilation or complete project check.

File queries first retain the deepest explicitly selected lexical ancestor
view. For an imported file outside all selected roots, they use its canonical
evaluated source membership, including equivalent absolute paths with `..` or
file symlinks. If several selected views include that file, the
most recently explicitly selected matching view wins. Reselect its GPR to
refresh that choice and the evaluated source list. After project or source
membership changes, repeat `ada_project_info` to refresh this snapshot. Files
outside those lists continue through normal project discovery. Successful
reselection reevaluates source membership in the existing ALS process.

`ada_project_info.complete=true` confirms the requested evaluated project
metadata and membership. Its separate Boolean `indexing_complete` is a
conservative readiness snapshot: false means indexing is pending or has not
yet been confirmed. The valid selection and ALS process remain available.
Semantic queries still apply their own completeness checks; a successful
project selection alone does not establish complete semantic results.

Doctor checks the actual locked image, numeric identity, read-only mounts,
private HOME, network/capability isolation, MCP catalog and confirmed EOF
cleanup. Direct host Docker calls have `--command-timeout`; MCP requests and
initialization use `--timeout`. Unknown inspect/timeout states fail and never
authorize explicit removal. Doctor excludes Config.Env from inspect requests.
Keep argv/protocol/stderr logs private; they contain caller paths and Docker's
own diagnostics. Direct command timeouts retain available stdout/stderr before
failure propagates. The legacy Mac smoke retains full private inspect records.
New Session log and Mac-smoke evidence directories, including newly created
parents, are owner-only before any records are opened or written. Existing
directories are refused rather than chmodded or reused. Logs can contain source
and scenario values; Mac full-inspect evidence can contain Config.Env. Permission
unit controls on Linux do not establish actual macOS runtime acceptance.

## Native clients and discovery

`native-config --binding FILE --output NEW.toml` creates a separate UTF-8 TOML
fragment. Review and merge it explicitly using the native client's supported
configuration, then reconnect. Generation is not registration or lifecycle
proof. The fragment exposes read tools; write rename/format/build are excluded.
The command client allows rename only as explicit preview. Availability is not
a support promise for every tool; see [support.md](support.md), included and
hash-verified beside this setup guide in the standalone bundle.

`install-skill --destination NEW_ABSOLUTE_DIRECTORY` copies verified resources
and atomically publishes a no-replace symlink in a supported local discovery
root. Storage stays outside that root to avoid duplicate discovery. Existing
entries are preserved. This proves only the actually tested local scope.
Installing a skill does not register native tools in the current managed Cloud
catalog. A reader's account/session still needs its own plugin-import,
discovery, acquisition and runtime checks; public bytes alone do not prove them.

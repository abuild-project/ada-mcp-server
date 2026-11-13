# Host setup and project views

The candidate requires Python 3.11+, Bash 3.2+ and an existing Docker daemon.
Its validated container target is Linux/AMD64 Debian Trixie with GNAT 14,
GPRbuild and the pinned Ada Language Server. macOS, native client registration
and other client applications remain in development until their own tests pass.

Check the GitHub Releases index
(<https://github.com/abuild-project/ada-mcp-server/releases>) for published
versions and their artifact metadata. During development, use
the artifacts generated from the checked source revision by scripts/artifacts.py.
Version-specific GitHub Releases/GHCR paths in generated candidate metadata
are distribution targets until publication and anonymous access are verified.

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
archive's exact versioned URL, byte size and SHA256. The explicit cache path
avoids global installation. A cached archive is accepted only if its hash and
size match; downloads use HTTPS and refuse downgrade redirects and replacement.
An existing local image can be used without a source, but a later cache miss
then requires explicit source configuration.

An explicit local `--archive FILE --archive-sha256 HASH` or full
`--registry registry.example.org/team/ada-mcp@sha256:DIGEST` is also supported.
The registry string is an example, not an existing service. Registry transport
needs separate evidence; a manifest/index digest differs from the config digest.
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
catalog. A new managed Cloud runtime's public artifact acquisition remains an
acceptance gate after a release is genuinely available.

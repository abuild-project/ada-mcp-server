# Ada MCP Server

Ada MCP lets an MCP client inspect your Ada projects through Ada Language
Server. Select your existing GPR project and use source-aware results to
understand code without leaving your assistant workflow.

You can:

- Explore a project's structure and symbols in its selected GPR view.
- Navigate to definitions and inspect hover information at real source locations.
- Request diagnostics for specific Ada files.

File diagnostics complement your project's compiler and tests. See the
[support matrix](doc/support.md) for the supported queries and current limits.

## Install, connect and use

You need Git, Python 3.11+, Bash 3.2+ and Docker able to run Linux/AMD64
containers. Use a nonroot account with Docker access and readable project
sources. You do not need to build Ada MCP or run this repository's CI.

1. [Choose and acquire a published release](doc/first-install.md#install-or-upgrade-to-rc3)
   and [create a shared Docker binding](doc/first-install.md#shared-docker-binding-and-first-queries)
   for your projects and dependencies. The guide verifies published downloads
   before setup and retains a pinned RC1 fallback.
2. [Use the bundled MCP query client](doc/first-install.md#shared-docker-binding-and-first-queries),
   or [prepare your client's stdio connection](doc/first-install.md#connect-a-stdio-mcp-client).
   Native client integration is experimental and needs checks in that client.
3. Select your actual GPR file, dependency search paths and scenarios. Ask
   questions such as “Which symbols does this file define?”, “Where is this
   symbol defined?” or “What diagnostics were published for this file?”.
   Compare returned locations and scope with your source.

This direct MCP workflow is independent of Plugin Creator and any private
publisher account. Optional conveniences are
[local Codex skill discovery](doc/first-install.md#optional-local-codex-skill-discovery)
and [your own private Cloud skill-plugin copy](doc/first-install.md#managed-cloud-create-your-private-copy).
The plugin supplies instructions; it does not register native MCP tools.

This is a pilot for the documented Linux/AMD64 Docker workflow. macOS,
native Codex/Claude/OpenCode integration and importing the Cloud plugin into
a separate account remain in development. See the
[first-install guide](doc/first-install.md) for host details and
[GitHub Releases](https://github.com/abuild-project/ada-mcp-server/releases)
for versions that are actually published.

RC2 adds [release checks and approved updates](doc/updating.md): search for a
new release and let the skill verify and execute an update after your approval.
Existing RC1 installations need an initial approved upgrade to a published
RC2 or later; their immutable packages have no update-notice hook.
RC3 adds [runtime reuse without replacing the skill/plugin](doc/updating.md#keep-the-entry-and-runtime-independent).
Use it only after publication; existing RC2 entries need one initial entry
upgrade, and later sessions need the same retained files and selection path.

## Contributing

To change, build, test or release Ada MCP itself, read the
[contributor development guide](doc/development.md).

This is the independently maintained
[abuild-project](https://github.com/abuild-project) continuation of
[MDBrothers/ada-mcp-server](https://github.com/MDBrothers/ada-mcp-server).
Original history, authorship and MIT notices are preserved.
See [LICENSE](LICENSE) and [component licensing](doc/licensing.md).

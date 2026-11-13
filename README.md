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

1. [Acquire the published tooling](doc/first-install.md#acquire-the-tooling-for-direct-mcp-or-local-codex)
   and [create a shared Docker binding](doc/first-install.md#shared-docker-binding-and-first-queries)
   for your projects and dependencies. The guide uses the existing public RC1
   release and verifies downloads before setup.
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

The current release is the **0.2.0-rc.1 pilot prerelease** for the documented
Linux/AMD64 Docker workflow. macOS, native Codex/Claude/OpenCode integration and
importing the Cloud plugin into a separate account remain in development.
Start with the [first-install guide](doc/first-install.md) for host-specific
details and the [published release](https://github.com/abuild-project/ada-mcp-server/releases/tag/v0.2.0-rc.1)
for artifacts.

Read [release checks and approved updates](doc/updating.md) for fresh searches,
the skill's ask-and-update workflow and rollback. Existing RC1 installations
need an initial approved upgrade after a notifier-capable release is published.

## Contributing

To change, build, test or release Ada MCP itself, read the
[contributor development guide](doc/development.md).

This is the independently maintained
[abuild-project](https://github.com/abuild-project) continuation of
[MDBrothers/ada-mcp-server](https://github.com/MDBrothers/ada-mcp-server).
Original history, authorship and MIT notices are preserved.
See [LICENSE](LICENSE) and [component licensing](doc/licensing.md).

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

1. [Install the current RC4 release](doc/first-install.md#install-or-upgrade-to-rc4).
   The guide verifies published downloads and creates one shared Docker binding
   for your approved workspace and client worktree roots. RC4 uses GHCR by
   default, with a verified image archive as fallback.
2. [Use the bundled MCP query client](doc/first-install.md#shared-docker-binding-and-first-queries),
   or [prepare your client's stdio connection](doc/first-install.md#connect-a-stdio-mcp-client).
   For Codex, install the skill once in `~/.agents/skills/ada-development` and
   explicitly merge a generated native fragment into `~/.codex/config.toml`.
   Both can serve multiple repositories and worktrees.
3. Select your actual GPR file, dependency search paths and scenarios. Ask
   questions such as “Which symbols does this file define?”, “Where is this
   symbol defined?” or “What diagnostics were published for this file?”.
   Compare returned locations and scope with your source.

This direct MCP workflow is independent of Plugin Creator and any private
publisher account. Optional conveniences are
[local Codex skill discovery](doc/first-install.md#optional-local-codex-skill-discovery)
and [your own private Cloud skill-plugin copy](doc/first-install.md#managed-cloud-create-your-private-copy).
The plugin supplies instructions; it does not register native MCP tools.

This is a pilot for the documented Linux/AMD64 Docker workflow. Supplied RC4
acceptance covers bounded queries on macOS 26.5.1 arm64 with Codex Desktop
26.1111.21308, including user-wide setup and a Codex-managed worktree. See the
[support matrix](doc/support.md) for the tested scope; other clients, native-host
ALS and separate-account Cloud plugin import remain in development. See
[GitHub Releases](https://github.com/abuild-project/ada-mcp-server/releases)
for published artifacts.

RC2 adds [release checks and approved updates](doc/updating.md): search for a
new release and let the skill verify and execute an update after your approval.
Existing RC1 installations need an initial approved upgrade to a published
RC2 or later; their immutable packages have no update-notice hook.
RC3 adds [runtime reuse without replacing the skill/plugin](doc/updating.md#keep-the-entry-and-runtime-independent).
Use it only after publication; existing RC2 entries need one initial entry
upgrade, and later sessions need the same retained files and selection path.
RC4 adds explicit project refresh, imported-source view retention and
[further bounded fixes](doc/releases/0.2.0-rc.4.md). The maintained installation
guide includes the later [Mac acceptance assessment](doc/assessments/macos-codex-rc4.md);
published archives and already installed skills retain their original instructions.

## Contributing

To change, build, test or release Ada MCP itself, read the
[contributor development guide](doc/development.md).

This is the independently maintained
[abuild-project](https://github.com/abuild-project) continuation of
[MDBrothers/ada-mcp-server](https://github.com/MDBrothers/ada-mcp-server).
Original history, authorship and MIT notices are preserved.
See [LICENSE](LICENSE) and [component licensing](doc/licensing.md).

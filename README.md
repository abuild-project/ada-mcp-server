# Ada MCP Server

Ada MCP lets your assistant inspect Ada code through Ada Language Server.
Select your existing GPR project to list symbols, jump to definitions,
inspect types and view diagnostics for a file. The documented workflow
reads your sources through Docker. Use your usual compiler and tests to
check the project.

## Get started

- [Mac with Codex Desktop](doc/user/first-install.md#mac-with-codex-desktop) — install the Ada skill and connect the Desktop tools.
- [Codex in Managed Cloud](doc/user/first-install.md#codex-in-managed-cloud) — activate a private skill that uses the Docker query helper.
- [Direct Docker](doc/user/first-install.md#direct-docker) — use the query helper from your terminal.

Once connected, ask Codex to select your `.gpr` file and list the symbols in
an Ada source file you know. Ask for their file names and line numbers so you
can check the answer against your checkout.

[Run a first query](doc/user/setup.md) · [Update or roll back](doc/user/updating.md)
· [Get help](doc/user/support.md)

See the [user documentation home](doc/user/index.md).

## Contributing

See the [development guide](doc/development.md) and [license](LICENSE).
This is the independently maintained
[abuild-project](https://github.com/abuild-project) continuation of
[MDBrothers/ada-mcp-server](https://github.com/MDBrothers/ada-mcp-server).

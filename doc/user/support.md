# Help with Ada MCP

## The Ada tools or skill are missing

- **Mac:** Check that Docker Desktop is running. Make sure the Ada entry was
  merged into the Codex settings, then fully quit and reopen Desktop.
- **Managed Cloud:** Check that the intended private plugin is active.
  Open a fresh chat if the skill is missing. The skill uses a Docker helper
  and appears as a skill in Codex.
- **Docker:** Check that your account has Docker access and the binding
  lists the project folders you need.
  [Run Doctor](../setup.md#doctor-and-actual-queries) for a setup check.

## The answer is empty or incomplete

Ask which project file and source path were used. Check that they're in the
right checkout and that you supplied any dependency paths and scenario values.
If indexing is still in progress, give it time and retry in the same project
view. If a result says it's incomplete or truncated, treat it as partial.

## What can I use it for?

Use Ada MCP for read-only inspection: listing symbols, finding definitions,
checking hover information and reading per-file diagnostics. Run your usual
compiler and tests to check whether the project builds and behaves correctly.
The documented setup covers the Docker helper, Mac Codex Desktop and the
Managed Cloud skill workflow. Other clients and setups need their own checks.

## Report a problem

Include your setup route, the installed version, the query and what you
expected. Remove private paths, source and secrets from any logs before
sharing them.
[Open a GitHub issue](https://github.com/abuild-project/ada-mcp-server/issues)
or follow the [security reporting process](../../SECURITY.md) for a vulnerability.

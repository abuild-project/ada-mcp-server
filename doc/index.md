# Ada MCP Server documentation

Ada MCP connects your assistant to Ada Language Server in a read-only Docker
workflow. Select an existing GPR project to explore symbols, navigate to
definitions and inspect file diagnostics.

## Choose your setup

| Setup | Start here |
| --- | --- |
| Mac with Codex Desktop | [Install or upgrade the verified runtime and local skill](first-install.md#install-or-upgrade-to-rc6). Then [generate and merge the native Ada entry](first-install.md#connect-a-stdio-mcp-client), fully quit and reopen Desktop, and check the connected server. |
| Codex in Managed Cloud | [Create or upgrade your private skill plugin](first-install.md#managed-cloud-create-your-private-copy), activate it and start a fresh chat if required. The skill uses the Docker query helper in your execution environment. |
| Direct Docker | [Acquire the verified RC6 runtime](first-install.md#first-acquisition-without-an-installed-acquirer), then [create a shared binding and use the query helper](first-install.md#shared-docker-binding-and-first-queries). You can also [connect a local stdio MCP client](first-install.md#connect-a-stdio-mcp-client). |

Check the [published releases](https://github.com/abuild-project/ada-mcp-server/releases)
and verify the selected release's metadata before downloading. See host
[prerequisites, Docker roots and permissions](setup.md) when preparing local
or managed execution.

## Run your first Ada query

With the connection or query helper ready, select your actual GPR file,
ordered dependency search paths and scenario values. Then ask a source-bound
question, for example:

> Select my project's GPR and scenario. List the symbols defined in
> `src/example.ads` and show their source locations.

Use a file that exists in your selected view. Check the returned GPR, file
and coordinates against your source, and look at `complete` and `truncated` where
available. If indexing is pending, follow the
[project readiness guidance](support.md#project-readiness-and-tool-support).
The [direct query example](first-install.md#shared-docker-binding-and-first-queries)
shows the equivalent JSON batch.

## Update, roll back or get help

- [Check for a release](updating.md#check-status-or-change-the-policy)
  and [approve an update](updating.md#ask-once-then-execute-the-approved-update).
- [Restore a compatible skill's or Cloud plugin's previous runtime selection](updating.md#restore-a-compatible-runtime-selection)
  or [return to the retained runtime and binding for direct Docker](updating.md#restore-the-direct-docker-runtime-and-binding).
- [Roll back a native client or private Cloud copy](updating.md#switch-native-clients-or-a-private-cloud-copy).
  If you replaced the local skill itself, [restore the retained skill](updating.md#switch-a-local-skill-without-losing-its-old-target).
- [Check supported tools, tested setups and limits](support.md).
- [Report a problem](https://github.com/abuild-project/ada-mcp-server/issues)
  with the client, runtime version and sanitized view and results.
  Use the [security reporting process](../SECURITY.md) for vulnerabilities.

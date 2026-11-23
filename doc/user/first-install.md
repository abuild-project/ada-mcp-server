# Install Ada MCP

Choose the project, dependency and worktree folders you want Ada MCP to read.
An approved folder includes all its subfolders, including future checkouts.

## Mac with Codex Desktop

1. Start Docker Desktop with Linux/AMD64 container support. Have Git,
   Python 3.11+ and Bash 3.2+ available to your user account.
2. Open your Ada checkout in Codex and copy this request:

   ```text
   Set up Ada MCP for this Mac. Follow the local Codex instructions in:
   https://github.com/abuild-project/ada-mcp-server/blob/main/doc/first-install.md#install-or-upgrade-to-rc6
   Verify the published downloads. Ask which project and worktree folders
   to share read-only. Install the Ada skill once for my user account and
   back up my Codex settings before merging the Ada tool entry.
   ```

3. Fully quit and reopen Codex Desktop after setup. In your checkout, ask
   Codex to confirm the Ada connection and [run a first query](setup.md#run-your-first-query).

The local skill guides Codex through Ada work. The separate Ada tool entry
connects Desktop directly to the server. For manual setup, see the
[local installation reference](../first-install.md#install-or-upgrade-to-rc6).

## Codex in Managed Cloud

1. Open your Ada checkout in an execution environment with command access,
   Git, Python 3.11+, Bash 3.2+ and Docker that can run Linux/AMD64
   containers. Creating or updating a private skill plugin requires
   Plugin Creator.
2. Copy this request into Codex:

   ```text
   Set up the private Ada development skill for my Codex account using the
   Managed Cloud instructions in:
   https://github.com/abuild-project/ada-mcp-server/blob/main/doc/first-install.md#managed-cloud-create-your-private-copy
   Keep my existing plugin identity and reuse its verified runtime if
   compatible. Check Docker access in this environment.
   ```

3. Activate the intended plugin through Codex and start a fresh chat if
   needed. Ask the skill to [run a first query](setup.md#run-your-first-query).

The Cloud skill runs the Docker query helper inside the execution
environment. Your Mac setup is separate. In a new environment, the skill
checks which files are available before reusing an installation. See the
[private plugin instructions](../first-install.md#managed-cloud-create-your-private-copy)
for activation and reuse.

If you need Plugin Creator and it is unavailable, use
[Direct Docker](#direct-docker) in an environment with Docker access. If
Docker is unavailable in Cloud, try [Codex Desktop on a Mac](#mac-with-codex-desktop).

## Direct Docker

1. Have Git, Python 3.11+, Bash 3.2+ and access to Docker that can run
   Linux/AMD64 containers. Use a regular user account with readable Ada sources.
2. [Download and verify the published tooling](../first-install.md#first-acquisition-without-an-installed-acquirer).
3. [Create a binding and run Doctor](../first-install.md#shared-docker-binding-and-first-queries)
   to give the helper read-only access to the folders you approve. A binding
   records the Docker setup and the folders it can read.
4. [Run the first query from your terminal](setup.md#direct-docker-query).

You can use the helper on its own. To connect a local client, follow the
[stdio setup instructions](../first-install.md#connect-a-stdio-mcp-client).

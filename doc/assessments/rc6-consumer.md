# RC6 Mac and Managed Cloud consumer assessment

The maintainer supplied these observations for the
[published RC6 pilot](https://github.com/abuild-project/ada-mcp-server/releases/tag/v0.2.0-rc.6).
They cover the specific configurations and requests below.

- **Mac offline check:** The RC6 launcher `--check` ran under Bash 3.2 on
  macOS 26.5.1 arm64, inspecting the retained RC5 image without starting a
  container. It accepted Python 3.13.14, rejected the system Python 3.9.6
  when advisories were enabled, and reported Python disabled with policy `off`.
- **Mac RC6 runtime and native connection:** The subsequent RC6 GHCR download
  and Doctor check used an installed fixed Python 3.13.14 interpreter,
  `auto` update policy and two read-only mounts. After fully restarting
  Codex Desktop, a resumed Arca chat reported the direct MCP handshake
  `0.2.0rc6` and that the skill was available. The selected `arca.gpr` view
  used the release scenario. The workspace-symbol search for `CPIO_Make_Symlink`
  was complete and untruncated. Definition and implementation queries matched
  the specification at line 72, column 14 and the body at line 368, column 14.
  A fresh RC6 chat and visual skill discovery remain separate checks.
- **Managed Cloud runtime reuse:** A fresh task in another configured
  execution environment reused the retained selection and verified runtime.
  It reported handshake `0.2.0rc6`, complete `arca.gpr` validation, and a
  complete, untruncated workspace symbol result for `Arca` at line 3,
  column 9. A fresh prerelease check returned `up_to_date`. The task used
  the skill and Docker query helper with retained files. Cold acquisition,
  third-party account import and native Cloud registration remain separate
  checks.

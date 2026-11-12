---
name: ada-development
description: Use for Ada/GPR development and pinned shared Ada MCP setup across repositories. Read project rules, verify the host binding, select real GPR/scenario views and assess complete source-bound results. Compiler CI remains separate.
---

# Ada development

Read the repository's AGENTS.md and development guides before work. Preserve
the active topic, role assignments and correction counters. Runtime helpers
are in this installed skill's scripts directory. See references/setup.md for
explicit host setup, artifact hashes and client limits.

Run scripts/ada_mcp_setup.py through Python: doctor first, bootstrap with the
existing binding if its pinned image is missing, or create a new explicit
binding/approved roots and image cache. Binding reads use --binding, then
ADA_MCP_BINDING, then the normal user configuration path. Never overwrite
bindings or global client/Docker configuration or repurpose HOME/CODEX_HOME.

Use query batch with actual ada_project_info arguments: exact gpr_file,
ordered project_paths and scenario_variables. Existing GPR files remain the
project contract. Anchor later symbol/navigation calls to an absolute Ada
file in that view. Check complete/truncated/scope and source coordinates;
an empty unscoped diagnostic cache is not a successful compilation.

Use only documented candidate support. A catalog tool name is not a support
promise. The query client forbids write rename/format/build; rename preview
requires explicit preview=true. Run the project's prescribed compiler, tests,
coverage and documentation separately. MCP does not replace CI.

Native Mac, Claude, OpenCode, registry transport and fresh managed Cloud
deployment remain in development until directly tested. Native configuration
generation or local skill discovery does not register tools in the running
managed Cloud chat. Report missing resources/image access as concrete blockers.

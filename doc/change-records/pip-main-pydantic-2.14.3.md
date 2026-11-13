# Pydantic input and installed version alignment

The dependency update changes the Pydantic input but leaves development.lock
unchanged. Docker installs that hash lock, so a green run would continue
testing 2.13.4 rather than the requested 2.14.3.

Regenerate the single hash lock for Pydantic 2.14.3 and its required
pydantic-core 2.50.4. Keep every other package version and hash set
unchanged. The public dependency ranges, MCP 1.28.1 pin and documented
support scope remain unchanged.

The original input-only revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388399084),
but its build log installed Pydantic 2.13.4. That result does not validate
the requested upgrade. Local preparation verifies input/lock agreement and
hash structure; the corrected merged revision requires complete Trixie CI
with the requested installed version, packaging, semantic and identity
checks and independent review.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

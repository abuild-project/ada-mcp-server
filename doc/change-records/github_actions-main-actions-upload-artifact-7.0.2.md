# Pinned artifact upload maintenance

The workflow uses an older pinned artifact-upload action. Update both upload
steps to the reviewed 7.0.2 commit while retaining the existing artifact
names, ZIP behavior, retention and read-only CI permissions.

The selected action remains on Node.js 24 and includes upstream retry
handling for HTTP429 responses. The original update completed the full
Hosted Trixie chain and both artifact uploads. This changes CI
infrastructure rather than the server's supported tools or public API.

The original dependency revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388341426),
including 399 unit tests, the later ALS/MCP controls and generated-artifact
host checks. These results belong to that original revision. The merged
preparation requires its own complete Hosted CI and independent review; no
manual release promotion was exercised by that CI run.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

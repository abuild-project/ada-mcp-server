# Pinned checkout maintenance

Update all three checkout sites from the older 4.x pin to the reviewed 7.0.1
commit, preserving exact-source selection and persist-credentials:false in
normal CI and both promotion jobs.

The action uses Node.js 24, whose minimum runner 2.327.1 is below the
observed Hosted runner 2.338.2. The v7 unsafe-fork guard does not require an
override because the workflows use neither pull_request_target nor
workflow_run. Do not enable credential persistence or broader permissions
for this update.

The original dependency revision passed [Hosted
validation](https://github.com/abuild-project/ada-mcp-server/actions/runs/43388353044),
including 399 unit tests and the later complete Trixie and
generated-artifact checks. This run did not execute the manual promotion
jobs. The merged preparation requires its own complete Hosted CI and
independent review, including inspection of those promotion call sites.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

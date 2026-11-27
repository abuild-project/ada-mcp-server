# Pages publishing action updates

Update the Pages publisher to setup-python 7.1.0, upload-pages-artifact
5.0.0 and deploy-pages 5.0.1. The proposed pins match the published Git
tags resolved through remote refs and the GitHub API. Their pinned
manifests preserve Python 3.13 and the handoff of one tar file in the
`github-pages` ZIP. The deploy action still finds that artifact through
the runner's Actions Results service before calling the Pages REST API.
The [plan](../plans/pages-actions-v5.md) records the verified releases,
manifests and runner requirements.

The successful main run at `dc0b1e2b091f8178b590e97d58fac87d58af0c08`
used runner 2.338.2, above the Node.js 24 minimum. A local build of that
revision produced seven visible files. Both upload versions' default
archive settings yielded the same tar. The main workflow will exercise
the new actions together after an approved merge.
[Main Pages run](https://github.com/abuild-project/ada-mcp-server/actions/runs/45988404392)

Co-Authored-By: GPT-6 <noreply@openai.com>

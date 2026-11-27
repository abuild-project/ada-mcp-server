# Pages publishing action updates

## 2026-11-27 — scope

Use main `dc0b1e2b091f8178b590e97d58fac87d58af0c08` as the base.
Update the three Pages workflow pins together so the Python setup, artifact
upload and deployment path can be reviewed as one change. Keep the current
main push and manual dispatch behavior, build and deploy jobs, permissions,
concurrency and GitHub Pages environment. Keep the user guides, generator,
Python 3.13 and hash-locked installation in the existing workflow.

Compare the Dependabot diffs with the published release notes, then resolve
each tag through Git's remote refs and the GitHub API's tag objects. The
three proposals match these published release commits. Read each action
manifest at its verified commit.

| Action | Verified commit | Published release |
| --- | --- | --- |
| `actions/upload-pages-artifact` | `fc324d3547104276b827a68afc52ff2a11cc49c9` | [v5.0.0](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0) |
| `actions/setup-python` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` | [v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0) |
| `actions/deploy-pages` | `368f82528645a54fb793d4d04e342629a3f51346` | [v5.0.1](https://github.com/actions/deploy-pages/releases/tag/v5.0.1) |

## 2026-11-27 — runner and deployment compatibility

The v7 setup action retains `python-version`. The workflow installs the
hash lock in its own shell step, so the v7.0.0 removal of `pip-install`
and the v7.1.0 addition of optional mirror inputs require no input changes.
Setup Python, the nested uploader and deploy Pages use Node.js 24. The
last successful main Pages run used `ubuntu-latest`, Ubuntu 26.04.1,
runner 2.338.2 and CPython 3.13.18. The runner exceeds the documented
v2.327.1 minimum for Node.js 24 actions.
[Setup Python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0) ·
[Runner v2.327.1](https://github.com/actions/runner/releases/tag/v2.327.1) ·
[Main Pages run](https://github.com/abuild-project/ada-mcp-server/actions/runs/45988404392)

The Pages uploader pins `actions/upload-artifact` v7.0.0 at
`bbbca2ddaa5d8feaa63e36b76fdaad77386f024f`. At review time the `v7`
alias resolved to v7.0.2 at `cf430e030ddbb5b0abf93d22962f4752f3646cd9`.
The composite passes one `artifact.tar` with
the name `github-pages` and the nested action's default `archive: true`
wraps that file in a ZIP. The prior main run uploaded the same artifact
name and one tar file. The v5 composite keeps its default hidden-file
exclusion and always excludes `.git` and `.github`. At the main base,
the site builder produced seven visible regular files. Both default tar
commands produced identical archives of those files. A scratch copy
with dotfiles exercised the default and explicit opt-in behavior.
[Pages upload manifest](https://github.com/actions/upload-pages-artifact/blob/fc324d3547104276b827a68afc52ff2a11cc49c9/action.yml) ·
[Nested upload manifest](https://github.com/actions/upload-artifact/blob/bbbca2ddaa5d8feaa63e36b76fdaad77386f024f/action.yml)

Deploy Pages defaults to `github-pages`. Its API client matches the
previous pin byte for byte and its shipped bundle calls the runner's
Actions Results service to find exactly one artifact by that name. It
then submits that artifact ID to the Pages REST API with the Pages GitHub
token and an OIDC token. The existing `pages: write` and `id-token: write`
permissions cover the deployment. v5.0.1 adds backoff and jitter to
status polling.
[Deploy action manifest](https://github.com/actions/deploy-pages/blob/368f82528645a54fb793d4d04e342629a3f51346/action.yml) ·
[Deploy API client](https://github.com/actions/deploy-pages/blob/368f82528645a54fb793d4d04e342629a3f51346/src/internal/api-client.js) ·
[Deploy execution bundle](https://github.com/actions/deploy-pages/blob/368f82528645a54fb793d4d04e342629a3f51346/dist/index.js)

## 2026-11-27 — acceptance and rollback

Check the maintained guides and the site archive locally. The tester
runs the full AMD64 Trixie chain on the immutable candidate. Independent
review covers that revision and the pin and compatibility evidence.
Start both correction phases at zero, with up to three rounds each.
Ordinary PR CI validates the site preview. After separate merge
approval, the main push triggers the first Pages deployment with the
new pins. Confirm the build and deploy jobs and the published guide
URLs at that revision.

If the new deployment fails, seek approval to revert its merge commit
with main as parent one. Validate the revert and merge it through the
ordinary workflow. Verify that the prior pins return and the resulting
main run publishes the site successfully.

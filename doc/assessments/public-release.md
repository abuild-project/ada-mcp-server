# Public repository and release assessment

## Observations on 2026-11-13

This assessment compares the effective settings exposed by GitHub for
`abuild-project/ada-mcp-server`, `abuild-project/arca-ada` and
`abuild-project/spawn-manager`. The inspected Ada MCP base is accepted merge
commit `5253b21204c8da18031f417d0f35ef6732d1e7c5`. Settings can change independently
of source; these observations are dated evidence, not permanent assertions.

| Setting | Ada MCP Server | Arca | Spawn Manager |
| --- | --- | --- | --- |
| Visibility and repository type | Public, independent repository | Public, independent repository | Public, independent repository |
| Primary branch | `main` | `main` | `master` |
| Effective primary-branch protection | `protected: false` | `protected: true` | `protected: true` |
| Allowed merge methods | Merge, squash, rebase | Merge only | Merge, squash, rebase |
| Repository rulesets returned | None | None; primary branch still protected | Primary-branch, release-tag and historical-branch rulesets |
| Private vulnerability reporting | Disabled | Enabled | Enabled |
| Automatically delete merged topic branches | Disabled | Enabled | Disabled |
| Wiki | Enabled | Disabled | Disabled |
| Repository description | Empty | Present | Present |
| Release-promotion environment | Absent; only `copilot` returned | Not used by the source-release procedure | Not used by the inspected source-release procedure |

Arca's recent workflow PR and Spawn Manager's recent release PR have real
two-parent merge commits. Spawn Manager's permissive merge settings are not
evidence that its recent releases used squash or rebase.

The maintainer selected merge commits for every Ada MCP PR and requested that
squash and rebase be disabled. The attempted repository update containing only
those three merge-method flags received HTTP 403, `Resource not accessible by
integration`. No settings were changed. The committed policy is therefore
decided, while remote enforcement remains pending an authorized administrator.

The integration can read ordinary repository, branch, ruleset, private-reporting
and environment metadata. Detailed branch protection, Actions permissions,
default workflow-token permissions, allowed-action policy, fork-contributor
approval policy, immutable-release settings and Dependabot alert enablement
received HTTP 403. Missing `security_and_analysis` fields do not establish
whether secret scanning or push protection is enabled. A repository metadata
response indicating administrator permissions does not prove this integration
has the fine-grained access needed by those endpoints.

## Proposed settings and remaining verification

The following repository-scoped target follows Arca's documented approach while
using this repository's actual `standalone` CI job. Except for the agreed merge
method, these are proposed settings for maintainer review, not claims that they
were applied or additional requirements for an external reviewer product.

- Permit merge commits only. Keep reviewed commits and authorship, with
  unpublished corrections combined before first submission. Do not require
  linear history, which would exclude the agreed merge method.
- Protect `main` with pull requests, strict successful GitHub Actions
  `standalone` checks, resolved conversations and enforcement for administrators;
  disallow force pushes and deletion. The reviewable
  [branch-protection target](../repository-protection.json) requires zero GitHub
  approving reviews, preserving the independent role workflow without inventing
  a second human approver.
- Inspect and protect released version tags against updates/deletion. Verify
  immutable-release settings before publication and retain each tag's exact
  source target. Corrections use a new version instead of replacing artifacts.
- Verify Actions accepts the required GitHub-owned actions at full commit-SHA
  pins and that external fork contributions require approval. Ordinary workflow
  tokens should be read-only; publication receives narrowly scoped writes only
  in its explicitly invoked job.
- Enable private vulnerability reporting and verify Dependabot alerts, secret
  scanning and push protection where supported. The existing SECURITY.md
  reporting guidance does not establish that GitHub's private reporting channel
  is enabled.
- Configure and inspect the actual `release-promotion` environment and intended
  branch/approval restrictions before relying on them. Its declaration in YAML,
  or automatic creation when a workflow first runs, does not establish any
  protection. Keep this distinct from the maintainer's release authorization.

Arca's tracked protection policy and dated publication documentation provide
useful targets, but inaccessible current settings are not independently
revalidated by copying those files. Do not change Arca or Spawn Manager as part
of this release. A description and removal of an unused wiki are optional
presentation improvements, not demonstrated runtime defects.

## Source, release and consumer evidence

The source contains MIT notices, immutable import provenance, contributor and
security guidance, explicit support limits and a manual release procedure.
Normal CI has `contents: read`, uses pinned checkout/upload actions, builds and
checks the committed AMD64 Trixie image, packages the same immutable target,
exercises both numeric identities and retains CI artifacts without publishing.
The publication job declares `contents: write` and `packages: write` only for
the explicitly selected release path; actual GitHub/GHCR access still needs its
own successful execution. A source declaration does not override organization
or repository policy.

Release preparation does not establish public artifact availability. The
promotion workflow requires a successful `main` push CI run at the exact source
revision and a matching release tag. It reuses that run's artifacts without
rebuilding and requires anonymous digest-pinned GHCR pull/config identity before
creating the GitHub prerelease. A public Git repository does not establish
public package visibility; inspect that package's effective setting after
creation. The [licensing requirements](../licensing.md) for redistributed
components remain applicable to the exact binary artifacts; component names,
license notices and checksums do not themselves fulfill corresponding-source
delivery obligations.

No public download, anonymous GHCR access, account-plugin update or fresh managed
Cloud deployment is certified by this assessment. After actual publication,
check versioned file URLs against the pinned hashes, update the existing plugin
to those verified references, and perform ordinary acquisition and source-bound
queries in a genuinely fresh managed Cloud task. Mac and native Claude/OpenCode
acceptance remain separate subsequent topics. Use the
[release procedure](../release.md) and [versioned notes](../releases/0.2.0-rc.1.md)
for the ordered pilot gates and limits.

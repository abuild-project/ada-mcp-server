# Validation reference retention assessment

## 2026-11-19: Audited source inventory

The audit of `abuild-project/ada-mcp-server` identified thirteen inactive
branches and no open pull requests at main
`67b93c7cc337ef307913e2760562b152a32a74d7`. Independent Git ancestry checks
confirmed that the seven source heads below are already reachable from that
revision, with no branch-only commits. Their temporary branches are redundant
if their heads and activity remain unchanged.

| Original branch | Exact source SHA |
| --- | --- |
| `codex/validation/additional-tool-round-3` | `9d0286be506fc781f2d6f6956fedfc22eb25b684` |
| `codex/validation/generic-unit-names-local-1` | `8c0997ab1444c51f62b999d12c901f20955912fa` |
| `codex/validation/harness-maintenance-local-0` | `47340df146ad5bc67fcfe426122b01d774d29b41` |
| `codex/validation/permission-tests-local-1` | `b1f40a7ad1e1b6dc7012133018f50627ba71a992` |
| `codex/validation/rename-application-result-local-0` | `5e8fb17810d90a55c0dedae911f147efef5ef151` |
| `codex/validation/retire-exploration-local-0` | `c1c9be5e426dfce454e88ef28bc4cf2638b831b6` |
| `codex/validation/signature-selection-contract-local-0` | `e7c9d9f21b4586a5b264e1f5a6f77e5006f70943` |

The six superseded heads below contain branch-only commits. Their public
remote refs were verified as annotated tag objects with the exact peeled
source targets shown here. These tags preserve the snapshots without
rewriting them.

| Original branch | Exact source SHA | Archive tag | Annotated tag object |
| --- | --- | --- | --- |
| `codex/read-tool-regressions` | `5cdd315acd309b11bed22e77f98d62cb8d9b396b` | `archive/codex/read-tool-regressions` | `523027a40700176658addc819656bd97127814e1` |
| `codex/validation/additional-tool-observation` | `0950488ebbdc9710d59c5a5ed28b288d4ba00deb` | `archive/codex/validation/additional-tool-observation` | `8e7e8f7e4cfbf6a85e8a5db1ac887e6196073488` |
| `codex/validation/additional-tool-round-1` | `452a32f546704b72bbb2477ec504cc5433c13587` | `archive/codex/validation/additional-tool-round-1` | `211824920634ebfdbf037141ff3ea31a16ca90f9` |
| `codex/validation/additional-tool-round-2` | `8b68936bd580a8ba2ab2ce80e582c4bb0d34b806` | `archive/codex/validation/additional-tool-round-2` | `5510886bf743f66dc5f3628f89a46baa4959c9a3` |
| `codex/validation/generic-unit-names-local-0` | `076cfee91dcb055519db01990beacc2f447215da` | `archive/codex/validation/generic-unit-names-local-0` | `78cc981cc3bcfdcd352031bb7c1e9d38a2182860` |
| `codex/validation/permission-tests-local-0` | `17baeec6f598467a7cf27697148c12b31de0f440` | `archive/codex/validation/permission-tests-local-0` | `81fdc288d01dced1bf3dd62cc6411e47e67639f5` |

All six objects name tagger Matthias Weidle at `2026-11-19T22:56:34Z`.
Each annotation records the original branch, exact source SHA and the reason:
preserve the superseded validation or topic snapshot before deleting its
obsolete branch after replacement work merged. It also states the separate
CI-retention boundary.

## Conditional deletion and archive protection

The maintainer authorized these archival substitutions and branch deletions.
Deletion requires an unchanged source head and no active work or open pull
request. A superseded branch additionally requires verification of the remote
annotated object, peeled source and effective archive-namespace protection
against updates/deletion. Protection must cover both direct and nested archive
names (`refs/tags/archive/*` and `refs/tags/archive/**/*`), allowing new archive
creation while prohibiting replacement or deletion. Tags must never move or
overwrite earlier snapshots. These preservation facts do not certify branch
deletion or continuing server-side enforcement.

## Separately retained CI evidence

The evidence capture at `2026-11-19T22:55:02Z` covers the thirteen exact source
heads above. Exact-head Actions queries returned twenty-five successful CI
runs and no failed CI runs. The collection contains twenty-five job logs as
UTF-8 serializations of connector-decoded provider text and twenty-five original
`validation-evidence` ZIPs. The ZIP bytes were checked against provider SHA256
digests; run/source metadata and member indices are retained with them.
Verification checked all 115 handoff files without extracting or executing
downloaded code. Its inner manifest SHA256 is
`39f991558ad707cf2d4854b127f65da4a655ff16875726572ba76e5b700f6ff9`.

| Handoff part | Bytes | SHA256 |
| --- | --- | --- |
| 1 of 2 | 15115583 | `e8898b3949ff0626665d63063437a31d57fdbeb9f87d2b72457cccfac1663928` |
| 2 of 2 | 13459445 | `d050fd456c74afaf37ee67d4fc8c9ff10d97f5110ee37641775a98eb712b090e` |

The [public evidence archive](https://github.com/abuild-project/ada-mcp-server/tree/70d082155b88b9a9b2a372bfc7ff80e04c47eee7)
is pinned by annotated tag `archive/ci-evidence/2026-11-19` to commit
`70d082155b88b9a9b2a372bfc7ff80e04c47eee7`, with tag object
`5a1bf350c91b70206d387cdf7a4ee71c0c4088cb`. Publication readback at
`2026-11-20T05:33:04Z` verified anonymous access, matching published bytes and
active archive-namespace protection against updates/deletion. This is a dated
observation; server-side protection can change independently of source.

Raw archives and logs are stored in that separate archive commit, outside main;
private host paths are omitted here. Release image archives were outside this
bounded collection, as were failures at ancestor revisions or in local attempts.
Original negative controls and native-blocker data remain inside the retained
validation ZIPs; preservation does not change acceptance.

The CI workflow's `validation-evidence` and `release-candidate` artifacts have
fourteen-day retention. Creating a source archive tag does not extend that
period or automatically preserve Actions logs; the separate evidence archive
explicitly stores the selected bytes.

## 2026-11-20: Storage decision before another evidence archive

The six small source-snapshot tags in the inventory remain required to preserve
superseded source heads. The separate binary CI-evidence tag
`archive/ci-evidence/2026-11-19` is a one-off storage exception. A fresh default
clone was verified to fetch its binary archive blobs even though those files
are outside main's working tree, adding to ordinary clone storage.

Prefer release assets outside Git object history for future CI evidence.
Before the next CI-evidence archive, obtain an explicit maintainer decision
on storage method and destination. No destination is selected here; the
decision must respect immutable product releases and update-feed behavior.
Keep the existing protected tag and archive unchanged.

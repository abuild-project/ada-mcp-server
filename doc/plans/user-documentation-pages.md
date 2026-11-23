# User documentation on GitHub Pages

## 2026-11-23 — initial scope

Use main `876602d264dd4e468b294847360a0ea201128008` as the base. Add an English
start page that guides readers through Mac/Codex, managed Cloud/Codex or direct
Docker setup, their first Ada query, updates, rollback and support. Publish the
start page and four existing user guides from their Markdown sources. Keep
contributor guidance, assessments, plans, change records and release notes on
GitHub and preserve links to those sources. Do not change released assets,
runtime, client configuration, update contracts or support commitments.

Use the already hash-locked development Markdown parser. Verify navigation and
in-page links at the project Pages subpath, and retain a hosted preview of the
exact candidate. Prepare a main-only manual Pages workflow with job-scoped
publication permissions where the official actions can be pinned. Repository
settings and deployment require separate authorization.

Replace stale pending RC6 consumer language in the maintained guides with the
maintainer-supplied Mac and managed Cloud observations and their evidence limits.
The Mac offline check reused the RC5 image; acquired RC6 and restarted Desktop
provide separate observations. The fresh Cloud task reused a configured entry
and retained RC6 runtime. Preserve the historical RC4 assessment and released
RC6 notes.

The developer will run targeted render, link and quality checks. The tester
will exercise the immutable candidate and complete AMD64 Trixie chain and the
independent reviewer will examine the same source and evidence. Local and PR
correction counters begin at zero, with up to three rounds in each phase.

## 2026-11-23 — site and release metadata decisions

The five site pages use relative HTML URLs for project-subpath hosting.
Links to guides on the main branch use the corresponding rendered pages.
Other repository files stay linked to GitHub, along with tagged documentation
and release assets. The complete container chain builds the preview and
hosted CI uploads it. Manual publication uses a separate workflow on main.

The release API confirmed an immutable, non-draft RC6 prerelease at the
accepted main revision. Maintained guides can direct readers to the published
pilot while still requiring digest and provenance verification at acquisition.

## 2026-11-23 — direct Docker and distribution

The direct Docker route starts with RC6 acquisition and points to the retained
runtime/binding pair for rollback. A compatible skill or Cloud entry can restore
its runtime selection through the existing guarded activation procedure. The
site carries an unchanged copy of the project's MIT license.

## 2026-11-23 — Pages link regression checks

An owned Markdown fixture exercises the actual site builder independently of
the maintained guides. Check that relative and GitHub main guide links resolve
at the project subpath, that a tagged guide retains its immutable GitHub URL,
and that missing pages and fragments fail the build. Keep these checks in the
ordinary host test suite.

## 2026-11-23 — task-oriented user guides

Render the short English guides from `doc/user/` at the existing Pages
filenames. The README leads with setup. The site takes readers from a choice
of Mac, Managed Cloud or direct Docker to a real query, then covers routine
use, approved updates, rollback and help. Link to advanced setup and recovery
at the steps that need them.

Keep the advanced reference paths and inbound anchors used by the distributed
skill, published release links and developer guidance. Move the detailed RC6
observations and their evidence limits to a maintainer assessment. Preserve
the support scope and the manual install/update procedures. No runtime,
release or archive-generation code changes are needed.

## 2026-11-23 — tool reference and first-query guidance

Add one optional link from everyday use to technical support on GitHub and
preserve the section anchor. Explain how to inspect the installed catalog
and argument schemas and how the Desktop and Docker helper call policies
differ. Give readers a source check for their first query and an alternate
setup route when Managed Cloud plugin creation is unavailable. Keep the
README and landing page unchanged.

## 2026-11-23 — maintainer-authorized link validation

The maintainer authorized this limited exception with local corrections at
1/3 and PR corrections at 3/3. The counters remain unchanged. The permitted
edits cover `scripts/build_pages.py` and `tests/host/test_build_pages.py` for
heading checks on linked repository Markdown, `doc/support.md` for the
server catalog source link, and this plan and its change record.

Validate headings in the candidate source for both relative links and
canonical GitHub main links. Keep advanced references on GitHub and retain
the existing treatment of tagged links, external links and fragments for
other file types. Link to the named server catalog declaration without a
line number on main.

## 2026-11-23 — maintainer-authorized Pages trigger

The maintainer directed Pages to publish on pushes to `main`, as in Arca
and Spawn. This supersedes the manual-only trigger and retains manual
dispatch from `main`. The pull request preview continues to run in CI.

This separate adjustment applies only to `.github/workflows/pages.yml`,
`doc/development.md`, this plan and its change record. Local corrections
remain at 1/3 and PR corrections at 3/3. Repository configuration and live
deployment are separate actions.

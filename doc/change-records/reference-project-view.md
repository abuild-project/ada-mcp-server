# Imported-source project views

File queries anchored to an imported library could lose an explicitly selected
CLI project when the library sources were outside the CLI directory. The call
anchor then returned three references, while the declaration returned only the
library specification and body. The installed baseline
`a3f16279c08dffbe87c6f09ea77e88ed9d6df04b` reproduced this difference using
two ALS instances; querying the declaration through the CLI instance returned
all three references and located the cause in wrapper routing.

Explicit project selection reloads ALS's project tree and waits for fresh
indexing before retaining exact source files from the root and imported
projects. File queries preserve the deepest explicitly selected lexical
ancestor, including nested overrides. Outside
those roots, the most recently successfully selected view containing the exact
file wins. Explicit reselection refreshes both membership and order; ordinary
file use and pool eviction preserve them. Runtime sources and files absent
from those evaluated lists remain outside this fallback. Recreated clients
retain the selected GPR, ordered project paths and scenario values.

Focused controls cover evaluated membership, unlisted and runtime sources,
overlapping imports, reselection, lexical priority, rejected views and eviction
with exact context. The additional-tool trace requires the ordered reload,
project-view and mains exchanges while retaining action-execution rejection.
The required STDIO regression compiles an owned library
and importer, requires three references from both initial anchors, adds and
compiles one imported caller, then requires four references from the new call
and original declaration after reselection. It observes stable MCP/ALS births
and checks a nonmember's separate project with positive and negative symbol
queries. It retains raw
protocol, compiler output and known fixture-input hashes.

Development checks through topic revision
`e5ceadee68024fe8433aae336f0631370c3279ff` passed Ruff, formatting, strict
typing, targeted unit tests and documentation validation in the verified
baseline Trixie runtime. The source-mounted native control passed the initial
three-reference and refreshed four-reference queries with unchanged original
inputs and a separately hashed addition. It rejects both the original
anchor-dependent scope defect and the published topic's stale-reselection
behavior. Development checks supplement the complete committed-source Trixie
build/check, artifact and numeric-identity controls required for acceptance.
Immutable-head results and source/image provenance belong in the PR validation
comments. See `doc/setup.md` and `doc/plans/reference-project-view.md` for
the approved policy.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

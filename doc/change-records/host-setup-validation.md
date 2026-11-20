# Host Python and explicit update policy

Native configuration previously left advisory Python selection to the GUI's
PATH. Supplied Mac RC4-to-RC5 observations exposed Python 3.9.6 failing the
checker while a Python 3.13.14 CLI worked, with stderr discarded and MCP still
usable. A separate native `off` policy also correctly suppressed notices.
The reported PATH correction and `auto` restored an existing cached notice and
native RC5 handshake; they do not establish a fresh automatic fetch, visible
banner or acceptance of this source fix.

New native fragments pin the supported setup interpreter's absolute
`sys.executable` through an optional launcher `--python` argument. Existing
fragments retain their PATH fallback. Generation freezes the effective channel
from explicit flag, environment or default `auto`, retains an inherited cache
path and reports the selected policy/source and interpreter. Deliberate `off`
remains valid; existing user configuration is never rewritten automatically.
Missing/unsupported advisory Python, checker process failure and oversized
output receive bounded stderr diagnostics while normal MCP startup preserves
protocol stdout, stdin and its fail-open behavior. Ordinary offline or empty
snapshot outcomes retain their existing best-effort semantics.
The version probe has an independent two-second host deadline, kills/reaps a
timed-out selected process and removes its private output without a surviving
timer. This covers that probe only, preserving the existing checker network
budget and making no general process-tree guarantee. Invalid inherited channels
warn once and disable advisories during normal launcher/query use; generation,
Doctor and `--check` remain strict.

Offline launcher `--check` and Doctor validate the intended interpreter for an
enabled advisory. Probe acceptance requires both exit zero and a bounded numeric
`X.Y.Z` response meeting Python 3.11; empty, malformed or older replies fail.
Doctor reports its intended launch check separately from its
forced-off MCP probe; deliberate `off` needs no advisory interpreter. No network
request is introduced by these checks. Python 3.11 remains the minimum; binding
schema, SDK/dependencies, workflow contract 1 and public tool behavior stay
unchanged.

README, installation, setup, update and full-skill guidance separate Mac
user-wide skill/native configuration from account-owned Cloud plugin activation,
fresh-chat discovery, verified runtime selection/bootstrap and Docker helper
queries. Current Cloud onboarding authenticates published RC5 metadata instead
of defaulting to RC1. Legacy entries need one selection-aware entry upgrade;
compatible runtime updates retain that entry. No Mac/Cloud synchronization or
Cloud task persistence is assumed. Published RC5 retains its scoped PATH
correction route and cannot accept the unreleased `--python` option.

The topic is based on `d723cd23261e0973a8e8e9d41383a3744f7fcf85`.
Focused development tests cover GUI PATH, pinned/failing interpreters,
protocol preservation, offline validation and generated policy; the added
counterexamples reject that unchanged baseline. Probe/channel controls also
reject `52018a9d636104266869c3b3dbe142245e94f1bd`; version-response controls
reject `769b8c1548430e4826994598a7bfb3062bb5bfc9`. Ruff, strict typing and
maintained documentation checks pass. Exact-head canonical hosted validation
and independent acceptance are recorded separately in the PR evidence.
Published RC4/RC5 bytes, release notes and historical Mac assessments remain
unchanged. No new Mac consumer, third-party Cloud import or native Cloud
registration acceptance is claimed.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

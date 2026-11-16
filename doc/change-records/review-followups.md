# Review follow-up evidence

The generic-owner regression previously measured only three module-level
regex APIs, silently allowing compiled-pattern work and an empty
measurement. Its existing 128-formal input and four-times-source budget
now include masking substitutions, require a measurement and explicitly
reject unmeasured callable APIs. One helper attempts repeated prefix
searches through a compiled pattern before returning the real handler
result; the shared guard rejects that measurement bypass. This is a
deterministic instrumentation check, without a timing SLA or general
complexity claim.

A launcher mock now omits identity overrides and uses an owned id stub
returning UID 1234 and GID 5678. It checks the exact Docker user and home
tmpfs arguments. A signature-parameter comment explains null's current
contract and the future LSP 3.18 capability decision. The generic-owner
changelog loses only its implementation detail. A separate build commit
ignores Dependabot MCP major updates while leaving minor/patch updates
eligible and current requirements and locks unchanged.

At `77d1b0455c51bd0b6141aaac9bcfe51138454f8a`, 159 focused tests,
Ruff/format, strict source Mypy and documentation checks passed. The
byte-verified snapshot ran in the existing project image as development
evidence. A baseline counterexample confirmed the old guard accepted the
compiled-prefix bypass. Product behavior remains unchanged; the identity
stub establishes Docker argument construction only.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

# Security reports

Do not include credentials, private source paths or unpublished vulnerability
details in public issues, logs or pull requests. Use the repository's private
security-reporting contact if available; otherwise contact a maintainer before
sharing sensitive details publicly. General setup failures can be reported
with redacted versions, hashes and the exact failing command.

Release consumers must verify the selected immutable artifact hash before
extracting or executing tooling. A successful hash check establishes artifact
identity relative to trusted metadata, not that arbitrary server tools are safe.
Use the documented read-only, nonroot, network-isolated container boundary.

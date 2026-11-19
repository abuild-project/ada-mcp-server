# Historical CI evidence archive

This isolated Git snapshot retains the CI evidence collected for the
2026-11-19 validation-branch cleanup in abuild-project/ada-mcp-server.
It covers 25 successful GitHub Actions runs at 13 exact source heads.

- [Part 1 of 2](ci-evidence-part-1.zip)
- [Part 2 of 2](ci-evidence-part-2.zip)
- [Part checksums](handoff-manifest.json)
- [Run, source, provider and file inventory](ci-evidence-manifest.json)

Both ZIP parts form one archive. Their paths share a common evidence root;
the two parts and handoff manifest must be retained together. The original
25 job-log serializations and 25 validation-evidence ZIPs are copied unchanged,
with provider metadata, member indices and source/image provenance. Logs are
UTF-8 serializations of connector-decoded provider text; validation ZIPs are
the original provider bytes. A total of
115 handoff files was verified. The inventory identifies the exact hashes
and collection boundary. No downloaded archive code was executed.

The source snapshots remain under their original protected archive tags,
with redundant source heads reachable from main. This root commit contains
evidence only and has no parent in the product history. It is not a product
release and supplies no replacement runtime image. Artifact preservation
does not turn expected negative controls or native ALS blockers into
accepted behavior. This archive does not change GitHub Actions retention.

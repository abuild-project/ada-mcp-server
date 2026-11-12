# Independent bootstrap and distribution

The inherited fork depended on external container preparation and did not
provide a standalone, versioned way to acquire the shared Ada tooling. The
independent abuild-project continuation preserves source/authorship history
while preparing one coordinated `0.2.0-rc.1` server/container/tooling candidate.

The standalone AMD64 Trixie recipe pins the Ada toolchain, ALS and Python
dependencies. Generic host tools preserve explicit GPR views, nonroot numeric
identity, read-only sources, isolated networking and private temporary HOME.
Bindings/configuration fragments are created only at explicit new paths.
Build inputs come from the exact committed Git tree, so ignored local files
cannot enter a source-labeled image. CI uses private executable scratch for
test fixtures while production temporary files remain nonexecutable.

Versioned tooling and image archives carry source/image/hash metadata. The
small skill obtains the complete archive through a pinned HTTPS URL/hash with
safe materialization, rather than requiring Plugin Creator owner access or
unsupported remote resource reads. Source and imported own tooling use MIT;
dependency notices and exact component/source metadata remain available.

The documented check chain covers unit/style/strict typing/coverage/packaging,
maintained links/examples and actual ALS/MCP integration. Host acceptance uses
generated artifacts and real project sources with both numeric identities.
The inherited ancestor-GPR selection fix is retained and directly exercised.
The required real diagnostic control observes malformed, repaired and malformed
text in the same MCP/ALS processes; an always-clean result is rejected.
Command receipts survive timeouts and process-start failures with their
available partial streams.

This candidate prepares release promotion; it does not publish artifacts.
Actual Mac/native-other-client behavior, registry transport/public access,
a cold image cache and fresh managed Cloud public acquisition require their
own later evidence. MCP file diagnostics and catalog presence do not replace
compiler CI or imply support for every advertised function.

Co-Authored-By: Codex (GPT-6) <codex@openai.com>

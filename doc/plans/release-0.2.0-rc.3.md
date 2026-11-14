# RC3 release and public notification acceptance

Base revision: `7b8c12c108deb14902e2cb8e2a758d688d612619`.

## 2026-11-14: Coordinated release and bounded consumer case

The maintainer authorized the separate reviewed RC3 release package after the
accepted entry/runtime separation feature, then publication and a real update
notification test. Coordinate canonical `0.2.0-rc.3` and Python/MCP `0.2.0rc3`;
preserve historical version fixtures and immutable public RC1/RC2 packages.
Keep the SDK, licensing, supported Linux/AMD64 Docker workflow and explicit
Mac/native/third-party Cloud limits unchanged. Runtime workflow contract remains 1.

Source-bound notes and public installation/update guidance must stay truthful
before publication. Use actual published GitHub asset digests, final release
manifest, exact tag/source and new pins; no future hashes are invented. Existing
RC2 entries need one initial entry update for selection, while compatible later
runtime updates may retain the entry. Files and their locator must actually
persist or be supplied in later sessions; do not promise Cloud persistence.

Add one manual read-only-permission hosted consumer workflow, with exact approved
RC3 source input and fixed installed RC2/expected RC3. Authenticate bounded public
API/asset metadata and tag/source correspondence before executing acquired RC2
helpers. Use its legacy acquisition interface without assuming a workflow field.
A new empty Docker client config supplies an anonymous digest-pinned public RC2
image. Use pinned Arca source and its real validation GPR view for Doctor/query.
Require actual RC2 initialization and both initialization/project RC3 notices,
then an actually performed fresh check inside the daily cache and an off control.

Preserve raw protocol, JSON, argv/streams, exact cleanup and provider/cache state
on failure; upload only small evidence. Respect actual provider waits and report
missing publication/feed propagation/offline failures without cache bypasses or
automatic retries. The probe never installs RC3, updates a private plugin or
claims native/fresh-Cloud/Mac acceptance. It does not rerun source/compiler CI.

Validate provenance/notice/HTTP guard logic with controlled fixtures and an
isolated no-network invalid-source startup. Keep the script in normal strict
Mypy/Ruff/unit checks. Full exact-source Trixie CI and independent review precede
the release PR merge; promote only that resulting main push CI's tested bytes
without rebuilding. Run the actual consumer workflow only after verified RC3
publication, and retain its real result separately from fixture evidence.

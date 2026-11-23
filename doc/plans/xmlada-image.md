# XML/Ada image dependencies

Base revision: `31c9f97e3ea7bd627b74145da391deb2ac397838`.

## 2026-11-23: Authorized standalone dependency

Install `libxmlada-schema-dev=25.0.0-4` in the existing pinned AMD64 Debian
Trixie image. Its dependencies provide the DOM, SAX, Input and Unicode
development packages, including the GPR projects and Ada sources needed by
projects importing XML/Ada. The corresponding runtime libraries in RC6 do
not supply these development exports. Existing Debian component and notice
inventories retain the package provenance.

Add one repository-owned fixture importing the same `xmlada` aggregate as
Abuild and all five package families. Reuse the existing real integration
runner to compile it and retain compiler output, input hashes and its ALI
artifact hash. The canonical tests must not require an external Abuild checkout.

The separate tester runs the complete immutable-candidate Docker check chain,
then a prepared Abuild pilot selecting `abuild.gpr` with `BUILD_TYPE=tests`,
`ABUILD_ANALYSIS=enabled` and `project_paths=[]`. Compare the candidate's package
identity, XML/Ada exports and source-bound navigation with the published RC6
missing-export control. Prepare Abuild's own project dependencies normally.

The coordinator assigns developer, tester and independent reviewer. This new
topic starts at local 0/3 and later PR 0/3. The developer performs modest host
checks and freezes the initial candidate. The tester handles Docker work given
the managed environment's VFS storage and limited free space.

Keep core server behavior, SDK, workflows, version and Trixie unchanged.
A project-build-derived image is a later release recommendation outside this
implementation. The coordinator handles hosted delivery.

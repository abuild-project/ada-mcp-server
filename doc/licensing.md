# Licensing and provenance

The server and this project's own distribution/tooling code use MIT. The
original [LICENSE](../LICENSE) notice is retained. This project is an
independent continuation of [MDBrothers/ada-mcp-server](https://github.com/MDBrothers/ada-mcp-server).
Its complete selected personal-fork history is retained at imported revision
`961f532bcc633189e8618852732be289752cbcd7`, including the ancestor-GPR fix.

The four host helpers originated in the separately tested generic integration:

| Imported helper | Original SHA256 before relicensing |
| --- | --- |
| ada-mcp-launch | 13f45411ec877a6395b605b4763ebc533a5c696dca4ae8e971e5816aaba9367a |
| ada_mcp_setup.py | 15279d11009cc38d09c88b85d6b8f32b286158a99aef024675e77b4428fa852c |
| mac_smoke.py | 26357de663e921a3bf78d8e9598f29ec56a62004dd7b67a3da5d030bd8b2d930 |
| mcp_client.py | 7b39bb31776a52c7ed43924f3f335c210b922f1abc043a0411791036407dc2fe |

The maintainer explicitly confirmed ownership/authority and MIT relicensing
for these four previously GPL-marked own files. Their copies here are adapted
under MIT. The prior pilot packages, images and evidence are not relicensed or
edited. No additional GPL implementation is copied from the private build
project. Version pins and generated dependency metadata are recorded facts;
the standalone Docker recipe and new workflow guides are written here.

The container is not wholly MIT. Debian packages, Python dependencies, GNAT,
GPRbuild and Ada Language Server retain their own terms. Debian copyright
metadata remains under `/usr/share/doc`, Python distribution notices remain in
the venv, and the exact ALS license is retained under
`/usr/share/licenses/ada-language-server`. The container build records pinned
versions, upstream URLs and checksums. Preserve these notices and comply with
the corresponding-source obligations of redistributed components. This project's
MIT grant does not replace them.

The lightweight skill and full tooling archives include this project's MIT
license. Generated metadata references the exact source revision and image;
an upstream PyPI package is not an abuild-project distribution channel.

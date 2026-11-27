# Pydantic 2.14.4 hash lock update

Dependabot bumped the runtime input to Pydantic 2.14.4. At merge
`2b5c5448740d094ee8a6d47078be9e77235b2c73`, the pin checker found
Pydantic 2.14.3 in the hash lock that Docker installs. Update the lock
to Pydantic 2.14.4 and its required pydantic-core 2.50.5.

The Pydantic wheel and the CPython 3.13 Linux AMD64 core wheel matched
their published SHA256 digests. Their wheel metadata confirmed the core
pin and the remaining dependency requirements. The locked hashes match
PyPI metadata for every wheel and source archive in both releases.
[Pydantic metadata](https://pypi.org/pypi/pydantic/2.14.4/json) ·
[pydantic-core metadata](https://pypi.org/pypi/pydantic-core/2.50.5/json)

Co-Authored-By: GPT-6 <noreply@openai.com>

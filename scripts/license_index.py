#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Record installed component versions, original notices and source locations."""

import argparse
import importlib.metadata
import json
import subprocess
from pathlib import Path


def component_index() -> dict[str, object]:
    """Read package metadata without changing any dependency or license text."""
    installed = subprocess.check_output(
        [
            "dpkg-query",
            "-W",
            "-f=${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\n",
        ],
        text=True,
    )
    debian = []
    for line in installed.splitlines():
        binary, version, source, source_version = line.split("\t")
        debian.append(
            {
                "package": binary,
                "version": version,
                "source_package": source,
                "source_version": source_version,
                "source_url": f"https://sources.debian.org/src/{source}/{source_version}/",
                "copyright": f"/usr/share/doc/{binary.split(':')[0]}/copyright",
                "source_acquisition": f"apt-get source {source}={source_version}",
            }
        )
    python = [
        {
            "name": package.metadata["Name"],
            "version": package.version,
            "license": package.metadata.json.get(
                "license_expression", package.metadata.json.get("license")
            ),
            "metadata": str(package.locate_file("")),
            "source_url": f"https://pypi.org/project/{package.metadata['Name']}/{package.version}/#files",
        }
        for package in importlib.metadata.distributions()
    ]
    return {
        "own_source_license": "MIT",
        "scope": "Dependencies retain their own license and corresponding-source requirements",
        "debian": debian,
        "python": python,
        "als": {
            "version": "2026.3.202607051",
            "license": "/usr/share/licenses/ada-language-server/LICENSE",
            "source_url": "https://github.com/AdaCore/ada_language_server/tree/2026.3.202607051",
        },
    }


def main() -> None:
    """Write the index inside the container after its dependencies are installed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    options.output.write_text(json.dumps(component_index(), indent=2) + "\n")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: MIT
"""Bind Docker's executable targets to one immutable Linux/AMD64 config."""

import base64
import hashlib
import json
import re
import tarfile
from pathlib import PurePosixPath
from typing import Any, BinaryIO

JSON = dict[str, Any]
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
INDEX = {
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
}
MANIFEST = {
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
}
CONFIG = {
    "application/vnd.oci.image.config.v1+json",
    "application/vnd.docker.container.image.v1+json",
}
LIMIT = 1024 * 1024


def require(condition: object, message: str) -> None:
    """Keep identity checks active under Python optimization."""
    if not condition:
        raise RuntimeError(message)


def descriptor(value: Any) -> JSON:
    """Accept only a bounded SHA256 descriptor, without fetching its URLs."""
    require(isinstance(value, dict), "image descriptor must be an object")
    assert isinstance(value, dict)
    require(
        isinstance(value.get("digest"), str) and DIGEST.fullmatch(value["digest"]),
        "invalid image descriptor digest",
    )
    require(type(value.get("size")) is int and value["size"] > 0, "invalid descriptor size")
    require(isinstance(value.get("mediaType"), str), "missing descriptor media type")
    return value


def validate_identity(identity: JSON, expected_config: str) -> str:
    """Verify a portable metadata proof; return its executable immutable target."""
    require(
        identity.get("version") == 1
        and identity.get("image_id") == expected_config
        and isinstance(expected_config, str)
        and DIGEST.fullmatch(expected_config)
        and identity.get("platform") == "linux/amd64",
        "image identity differs from the config/platform lock",
    )
    target = descriptor(identity.get("target"))
    config_size = identity.get("config_size")
    require(
        type(config_size) is int and 0 < config_size <= 4 * LIMIT,
        "invalid canonical config byte count",
    )
    nodes = identity.get("metadata")
    require(isinstance(nodes, dict) and len(nodes) <= 64, "invalid image metadata proof")
    assert isinstance(nodes, dict)
    graph_root = identity.get("oci_root")
    if target["digest"] == expected_config:
        require(
            target["mediaType"] in CONFIG and target["size"] == config_size,
            "invalid classic config target size/type",
        )
        if graph_root is None:
            require(not nodes, "unreachable metadata for classic config target")
            return str(target["digest"])
        graph_root = descriptor(graph_root)
    else:
        require(
            graph_root is None or graph_root == target, "OCI root differs from execution target"
        )
        graph_root = target
    seen: set[str] = set()
    runtime_count = 0
    metadata_bytes = 0

    def walk(item: JSON, depth: int = 0) -> None:
        nonlocal runtime_count, metadata_bytes
        item = descriptor(item)
        platform = item.get("platform", {})
        require(
            not platform
            or platform.get("os") == "linux"
            and platform.get("architecture") == "amd64",
            "image descriptor platform differs from Linux/AMD64",
        )
        digest = item["digest"]
        require(depth <= 8 and digest not in seen, "cyclic/duplicate image descriptor path")
        seen.add(digest)
        require(item["mediaType"] in INDEX | MANIFEST, "unsupported image metadata type")
        require(digest in nodes and item["size"] <= LIMIT, "missing/oversized image metadata")
        require(
            isinstance(nodes[digest], str) and len(nodes[digest]) <= 2 * LIMIT,
            "encoded metadata exceeds limit",
        )
        try:
            data = base64.b64decode(nodes[digest], validate=True)
        except (ValueError, TypeError) as error:
            raise RuntimeError("invalid image metadata encoding") from error
        metadata_bytes += len(data)
        require(metadata_bytes <= 4 * LIMIT, "image metadata proof exceeds size limit")
        require(
            len(data) == item["size"] and "sha256:" + hashlib.sha256(data).hexdigest() == digest,
            "image descriptor digest/size mismatch",
        )
        document = json.loads(data)
        require(
            isinstance(document, dict)
            and document.get("schemaVersion") == 2
            and document.get("mediaType", item["mediaType"]) == item["mediaType"],
            "invalid image metadata document",
        )
        if item["mediaType"] in INDEX:
            children = document.get("manifests")
            require(isinstance(children, list) and 0 < len(children) <= 64, "invalid image index")
            for child in children:
                child = descriptor(child)
                platform = child.get("platform", {})
                annotations = child.get("annotations", {})
                if (
                    platform == {"architecture": "unknown", "os": "unknown"}
                    and annotations.get("vnd.docker.reference.type") == "attestation-manifest"
                ):
                    require(child["mediaType"] in MANIFEST, "invalid attestation descriptor")
                    continue
                require(
                    not platform
                    or platform.get("os") == "linux"
                    and platform.get("architecture") == "amd64",
                    "image index contains a non-AMD64 runtime",
                )
                walk(child, depth + 1)
        else:
            config = descriptor(document.get("config"))
            require(
                config["mediaType"] in CONFIG and config["digest"] == expected_config,
                "image manifest config differs from runtime lock",
            )
            require(
                config["size"] == config_size,
                "image manifest config size differs from canonical config byte count",
            )
            layers = document.get("layers")
            require(isinstance(layers, list) and bool(layers), "image manifest layers missing")
            for layer in layers:
                descriptor(layer)
            runtime_count += 1

    walk(graph_root)
    require(runtime_count == 1, "expected exactly one Linux/AMD64 runtime manifest")
    require(set(nodes) == seen, "unreachable metadata in image identity proof")
    return str(target["digest"])


def archive_identity(
    stream: BinaryIO,
    expected_config: str | None = None,
    expected_target: str | None = None,
    evidence: JSON | None = None,
) -> JSON:
    """Read safe Docker-save metadata, authenticating OCI target/config linkage."""
    result: JSON = {"status": "failed", "expected_image_id": expected_config}
    if evidence is not None:
        evidence["image_validation"] = result

    def name(value: Any) -> str:
        require(isinstance(value, str) and bool(value), "invalid Docker-save member name")
        path = PurePosixPath(value)
        require(
            not path.is_absolute() and ".." not in path.parts and str(path) != ".",
            "unsafe Docker-save member name",
        )
        return str(path)

    stream.seek(0)
    with tarfile.open(fileobj=stream, mode="r:*") as archive:
        members: dict[str, tarfile.TarInfo] = {}
        for count, member in enumerate(archive, 1):
            require(count <= 10000, "Docker-save archive has too many members")
            if member.isdir() and member.name in {".", "./"}:
                continue
            key = name(member.name)
            require(key not in members, "duplicate Docker-save archive member: " + key)
            members[key] = member

        def read(key: str, limit: int = LIMIT) -> bytes:
            require(key in members, "Docker-save metadata is missing: " + key)
            member = members[key]
            require(
                member.isfile() and 0 <= member.size <= limit,
                "Docker-save metadata must be a bounded regular file: " + key,
            )
            payload = archive.extractfile(member)
            assert payload is not None
            with payload:
                data = payload.read(limit + 1)
            require(len(data) == member.size, "Docker-save metadata size mismatch")
            return data

        manifests = json.loads(read("manifest.json"))
        require(isinstance(manifests, list), "Docker-save manifest must be an array")
        result["manifest_image_count"] = len(manifests)
        require(
            len(manifests) == 1 and isinstance(manifests[0], dict),
            "only single-image Docker-save archives are accepted",
        )
        config_name = name(manifests[0]["Config"])
        config_bytes = read(config_name, 4 * LIMIT)
        actual = "sha256:" + hashlib.sha256(config_bytes).hexdigest()
        result.update(config_member=config_name, actual_image_id=actual)
        require(
            expected_config is None or actual == expected_config,
            "Docker-save config image ID differs from the runtime lock; Docker load was not run",
        )
        config = json.loads(config_bytes)
        require(isinstance(config, dict), "Docker-save config must be an object")
        require(
            config.get("os") == "linux" and config.get("architecture") == "amd64",
            "Docker-save config is not linux/amd64",
        )
        labels = config.get("config", {}).get("Labels", {})
        result.update(
            platform="linux/amd64",
            source_revision=labels.get("org.opencontainers.image.revision"),
            project_version=labels.get("org.opencontainers.image.version"),
        )
        layers = manifests[0].get("Layers")
        diff_ids = config.get("rootfs", {}).get("diff_ids")
        require(
            isinstance(layers, list)
            and bool(layers)
            and isinstance(diff_ids, list)
            and len(layers) == len(diff_ids),
            "Docker-save layer/config count mismatch",
        )
        assert isinstance(layers, list)
        for layer in layers:
            key = name(layer)
            require(
                key in members and members[key].isfile(), "Docker-save layer missing/nonregular"
            )
        identity: JSON = {
            "version": 1,
            "image_id": actual,
            "config_size": len(config_bytes),
            "platform": "linux/amd64",
            "target": {
                "digest": actual,
                "size": len(config_bytes),
                "mediaType": "application/vnd.oci.image.config.v1+json",
            },
            "metadata": {},
        }
        result["identity"] = identity
        if "index.json" in members:
            require(
                json.loads(read("oci-layout")) == {"imageLayoutVersion": "1.0.0"},
                "invalid OCI layout",
            )
            index = json.loads(read("index.json"))
            roots = index.get("manifests") if isinstance(index, dict) else None
            require(isinstance(roots, list) and len(roots) == 1, "ambiguous OCI archive targets")
            assert isinstance(roots, list)
            identity["oci_root"] = descriptor(roots[0])
            if expected_target != actual:
                identity["target"] = identity["oci_root"]
            collected_bytes = 0

            def collect(item: JSON, depth: int = 0) -> None:
                nonlocal collected_bytes
                item = descriptor(item)
                require(depth <= 8 and len(identity["metadata"]) < 64, "OCI graph exceeds limit")
                digest = item["digest"]
                require(digest not in identity["metadata"], "cyclic/duplicate OCI graph")
                data = read("blobs/sha256/" + digest.removeprefix("sha256:"))
                collected_bytes += len(data)
                require(collected_bytes <= 4 * LIMIT, "OCI graph exceeds byte limit")
                require(
                    len(data) == item["size"]
                    and "sha256:" + hashlib.sha256(data).hexdigest() == digest,
                    "OCI descriptor digest/size mismatch",
                )
                identity["metadata"][digest] = base64.b64encode(data).decode("ascii")
                document = json.loads(data)
                if item["mediaType"] in INDEX:
                    for child in document.get("manifests", []):
                        if (
                            child.get("platform") == {"architecture": "unknown", "os": "unknown"}
                            and child.get("annotations", {}).get("vnd.docker.reference.type")
                            == "attestation-manifest"
                        ):
                            continue
                        collect(child, depth + 1)

            collect(identity["oci_root"])
        target = validate_identity(identity, actual)
        require(
            expected_target is None or target == expected_target,
            "export target differs from inspected immutable Docker target",
        )
        result.update(status="passed", layer_count=len(layers), verified_before_load=True)
        return identity

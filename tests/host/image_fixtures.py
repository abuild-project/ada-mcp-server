"""Small metadata archives only; no fixture is an executable Ada image."""

import hashlib
import io
import json
import tarfile


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def classic_identity(image_id, size=1):
    return {
        "version": 1,
        "image_id": image_id,
        "config_size": size,
        "platform": "linux/amd64",
        "target": {
            "digest": image_id,
            "size": size,
            "mediaType": "application/vnd.oci.image.config.v1+json",
        },
        "metadata": {},
    }


def metadata_archive(oci=False, mutate=None, *, hybrid=False):
    config = json.dumps(
        {
            "os": "linux",
            "architecture": "amd64",
            "config": {
                "Env": ["TEST_PRIVATE_SENTINEL=do-not-log-config-env"],
                "Labels": {
                    "org.opencontainers.image.revision": "a" * 40,
                    "org.opencontainers.image.version": "0.2.0-rc.1",
                },
            },
            "rootfs": {"diff_ids": [digest(b"fixture layer")]},
        }
    ).encode()
    config_id = digest(config)
    files = {"config.json": config, "layer.tar": b"fixture layer"}
    target = config_id
    if oci or hybrid:
        manifest = json.dumps(
            {
                "schemaVersion": 2,
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "config": {
                    "digest": config_id,
                    "size": len(config),
                    "mediaType": "application/vnd.oci.image.config.v1+json",
                },
                "layers": [
                    {
                        "digest": digest(b"fixture layer"),
                        "size": 13,
                        "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    }
                ],
            }
        ).encode()
        runtime = {
            "digest": digest(manifest),
            "size": len(manifest),
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "platform": {"os": "linux", "architecture": "amd64"},
        }
        attestation = {
            "digest": "sha256:" + "e" * 64,
            "size": 123,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "platform": {"os": "unknown", "architecture": "unknown"},
            "annotations": {"vnd.docker.reference.type": "attestation-manifest"},
        }
        index = json.dumps(
            {
                "schemaVersion": 2,
                "mediaType": "application/vnd.oci.image.index.v1+json",
                "manifests": [runtime, attestation],
            }
        ).encode()
        target = digest(index)
        files["blobs/sha256/" + digest(manifest)[7:]] = manifest
        files["blobs/sha256/" + target[7:]] = index
        root = {
            "digest": target,
            "size": len(index),
            "mediaType": "application/vnd.oci.image.index.v1+json",
        }
        if hybrid:
            root = runtime
            target = config_id
        files["index.json"] = json.dumps(
            {
                "schemaVersion": 2,
                "manifests": [root],
            }
        ).encode()
        files["oci-layout"] = b'{"imageLayoutVersion":"1.0.0"}'
    files["manifest.json"] = json.dumps(
        [{"Config": "config.json", "Layers": ["layer.tar"]}]
    ).encode()
    if mutate is not None:
        mutate(files)
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for name, data in files.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
    stream.seek(0)
    return stream, config_id, target


def corrupt_config_size(files):
    """Rehash enclosing OCI nodes, leaving actual canonical config bytes intact."""
    index = json.loads(files["index.json"])
    root = index["manifests"][0]
    root_key = "blobs/sha256/" + root["digest"][7:]
    document = json.loads(files[root_key])
    runtime = document["manifests"][0] if "manifests" in document else root
    runtime_key = "blobs/sha256/" + runtime["digest"][7:]
    manifest = json.loads(files[runtime_key])
    manifest["config"]["size"] += 1
    data = json.dumps(manifest).encode()
    runtime.update(digest=digest(data), size=len(data))
    files["blobs/sha256/" + runtime["digest"][7:]] = data
    if "manifests" in document:
        data = json.dumps(document).encode()
        root.update(digest=digest(data), size=len(data))
        files["blobs/sha256/" + root["digest"][7:]] = data
    files["index.json"] = json.dumps(index).encode()

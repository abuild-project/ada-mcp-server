#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Provision and diagnose a pinned Ada MCP image without changing product code."""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, BinaryIO

JSON = dict[str, Any]


sys.dont_write_bytecode = True

SCRIPT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_ROOT.parent
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


def require(condition: object, message: str) -> None:
    """Reject invalid inputs before changing state."""
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path | str) -> str:
    """Hash a file incrementally, including large Docker-save archives."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verified_manifest() -> JSON:
    """Check every declared bundle helper before invoking it."""
    manifest: JSON = json.loads((SCRIPT_ROOT / "runtime-manifest.json").read_text())
    require(IMAGE_ID.fullmatch(manifest["image_id"]), "bundle image ID is invalid")
    for name, digest in manifest["files_sha256"].items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts, "invalid bundle manifest path")
        require(
            SHA256.fullmatch(digest) and sha256_file(SKILL_ROOT / path) == digest,
            "bundle helper checksum mismatch: " + name,
        )
    from image_identity import validate_identity

    validate_identity(manifest["image_identity"], manifest["image_id"])
    return manifest


def absolute_path(value: str, label: str) -> Path:
    """Keep installation and binding writes explicit and absolute."""
    path = Path(value)
    require(path.is_absolute(), label + " must be absolute")
    return path


def binding_path(value: str | None) -> Path:
    """Read an explicit binding, then ADA_MCP_BINDING, then the normal user path."""
    return absolute_path(
        value
        or os.environ.get("ADA_MCP_BINDING")
        or str(Path.home() / ".config/ada-mcp/binding.json"),
        "binding path",
    )


def validate_registry(reference: str) -> None:
    """Require an explicit registry/repository and immutable manifest digest."""
    require(
        isinstance(reference, str) and reference.count("@sha256:") == 1,
        "registry source requires a full registry/repository@sha256:digest",
    )
    repository, digest = reference.split("@sha256:")
    require(SHA256.fullmatch(digest), "invalid registry manifest digest")
    parts = repository.split("/")
    require(
        len(parts) >= 2 and ("." in parts[0] or ":" in parts[0] or parts[0] == "localhost"),
        "registry hostname must be explicit",
    )
    require(
        re.fullmatch(r"[a-z0-9][a-z0-9.:-]*", parts[0])
        and all(re.fullmatch(r"[a-z0-9]+(?:[._-]+[a-z0-9]+)*", p) for p in parts[1:]),
        "invalid registry repository or tag; use an untagged repository@digest",
    )


def validate_binding(binding: JSON, manifest: JSON) -> JSON:
    """Validate one host binding; existing GPR files remain the project contract."""
    require(
        isinstance(binding, dict)
        and set(binding)
        == {
            "version",
            "image_id",
            "roots",
            "docker_host",
            "docker_context",
            "uid",
            "gid",
            "image_source",
            "image_identity",
        },
        "invalid binding fields",
    )
    require(binding["version"] == 2, "unsupported binding version")
    require(
        binding["image_id"] == manifest["image_id"],
        "image ID does not match this bundle runtime lock",
    )
    target_id(binding)
    require(
        binding["image_identity"]["config_size"] == manifest["image_identity"]["config_size"],
        "config byte count does not match this bundle runtime lock",
    )
    require(isinstance(binding["roots"], list) and binding["roots"], "select at least one root")
    for root in binding["roots"]:
        require(isinstance(root, str), "root must be a string")
        path = absolute_path(root, "root")
        require(
            path.is_dir() and root != "/" and str(path.resolve()) == root,
            "root must be an existing physical absolute directory: " + root,
        )
        require(
            not any(character in root for character in [",", '"', "\n", "\r"]),
            "unsupported root path character",
        )
    require(len(set(binding["roots"])) == len(binding["roots"]), "duplicate root")
    for key in ["uid", "gid"]:
        require(
            type(binding[key]) is int and 0 < binding[key] <= 4294967294,
            key + " must be a nonzero numeric identity",
        )
    for key in ["docker_host", "docker_context"]:
        require(
            binding[key] is None or isinstance(binding[key], str) and binding[key],
            "invalid Docker selector",
        )
    require(
        not (binding["docker_host"] and binding["docker_context"]),
        "Docker host and context are mutually exclusive",
    )
    source = binding["image_source"]
    require(source is None or isinstance(source, dict), "invalid image source")
    if source is not None:
        if source.get("kind") == "archive":
            require(
                set(source) == {"kind", "path", "sha256"}
                and isinstance(source["sha256"], str)
                and SHA256.fullmatch(source["sha256"]),
                "archive source requires path and SHA256",
            )
            absolute_path(source["path"], "archive path")
        elif source.get("kind") == "download":
            require(
                set(source) == {"kind", "path", "url", "sha256", "bytes"},
                "invalid download source fields",
            )
            absolute_path(source["path"], "image cache path")
            distribution = manifest["available_archive"]
            require(
                source["url"] == distribution["download_url"]
                and source["sha256"] == distribution["sha256"]
                and source["bytes"] == distribution["bytes"],
                "image download source differs from runtime lock",
            )
        elif source.get("kind") == "registry":
            require(set(source) == {"kind", "reference"}, "invalid registry source fields")
            validate_registry(source["reference"])
        else:
            raise RuntimeError("unknown image source kind")
    return binding


def read_binding(path: Path, manifest: JSON) -> JSON:
    """Read host metadata without evaluating shell or TOML code."""
    return validate_binding(json.loads(path.read_text()), manifest)


def docker_binding(binding: JSON) -> tuple[list[str], dict[str, str]]:
    """Preserve default Docker selection, clearing conflicts only for overrides."""
    command = ["docker"]
    environment = dict(os.environ)
    if binding["docker_host"] or binding["docker_context"]:
        for key in [
            "DOCKER_HOST",
            "DOCKER_CONTEXT",
            "DOCKER_TLS",
            "DOCKER_TLS_VERIFY",
            "DOCKER_CERT_PATH",
        ]:
            environment.pop(key, None)
        if binding["docker_host"]:
            command.extend(["--host", binding["docker_host"]])
        else:
            command.extend(["--context", binding["docker_context"]])
    return command, environment


def command_run(
    command: list[str],
    environment: dict[str, str],
    report: JSON,
    timeout: float,
    check: bool = True,
    stdin: BinaryIO | None = None,
) -> subprocess.CompletedProcess[str]:
    """Record bounded command results without including host environment secrets."""
    entry: JSON = {"argv": command, "rc": None, "stdout": "", "stderr": ""}
    report.setdefault("commands", []).append(entry)
    try:
        result = subprocess.run(
            command, env=environment, stdin=stdin, text=True, capture_output=True, timeout=timeout
        )
        entry.update(rc=result.returncode, stdout=result.stdout, stderr=result.stderr)
        require(
            not check or result.returncode == 0,
            "command failed (rc=" + str(result.returncode) + "): " + result.stderr.strip(),
        )
        return result
    except subprocess.TimeoutExpired as error:

        def decoded(value: str | bytes | None) -> str:
            return (
                value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
            )

        entry.update(
            stdout=decoded(error.stdout),
            stderr=decoded(error.stderr),
            timed_out=True,
            timeout_seconds=timeout,
            error=type(error).__name__ + ": " + str(error),
        )
        raise
    except Exception as error:
        entry["error"] = type(error).__name__ + ": " + str(error)
        raise


def inspect_container(
    command: list[str],
    environment: dict[str, str],
    name: str,
    observations: list[JSON],
    timeout: float,
) -> JSON | None:
    """Inspect exactly one name with a deadline and distinguish unknown state."""
    selected = (
        '[{"Id":{{json .Id}},"Name":{{json .Name}},"Image":{{json .Image}},'
        '"Config":{"User":{{json .Config.User}},"Labels":{{json .Config.Labels}}},'
        '"HostConfig":{{json .HostConfig}},"Mounts":{{json .Mounts}}}]'
    )
    argv = command + ["container", "inspect", "--format", selected, name]
    observation: JSON = {
        "argv": argv,
        "name": name,
        "status": "unknown",
        "rc": None,
        "stdout": "",
        "stderr": "",
        "timeout_seconds": timeout,
        "selected_fields": [
            "Id",
            "Name",
            "Image",
            "Config.User",
            "Config.Labels",
            "HostConfig",
            "Mounts",
        ],
        "excluded_fields": ["Config.Env"],
    }
    observations.append(observation)
    try:
        result = subprocess.run(
            argv, env=environment, text=True, capture_output=True, timeout=timeout
        )
        observation.update(rc=result.returncode, stdout=result.stdout, stderr=result.stderr)
        if result.returncode == 0:
            states: list[JSON] = json.loads(result.stdout)
            require(
                isinstance(states, list)
                and len(states) == 1
                and isinstance(states[0], dict)
                and states[0].get("Name") == "/" + name,
                "Docker inspect did not return the exact requested container",
            )
            observation["status"] = "present"
            return states[0]
        missing = {
            prefix + kind + name
            for prefix in ["", "Error: ", "Error response from daemon: "]
            for kind in ["No such container: ", "No such object: "]
        }
        if (
            result.returncode == 1
            and result.stdout.strip() in ["", "[]"]
            and result.stderr.strip() in missing
        ):
            observation["status"] = "absent-confirmed"
            return None
        raise RuntimeError(
            "Docker container state is unknown (inspect rc="
            + str(result.returncode)
            + "): "
            + result.stderr.strip()
        )
    except subprocess.TimeoutExpired as error:

        def decoded(value: bytes | str | None) -> str:
            return (
                value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
            )

        observation.update(
            stdout=decoded(error.stdout),
            stderr=decoded(error.stderr),
            timed_out=True,
            error=type(error).__name__ + ": " + str(error),
        )
        raise
    except Exception as error:
        observation["error"] = type(error).__name__ + ": " + str(error)
        raise


def validate_docker_archive(stream: BinaryIO, expected_image: str, evidence: JSON) -> None:
    """Validate canonical config and safe Classic/OCI metadata before any load."""
    from image_identity import archive_identity

    archive_identity(stream, expected_config=expected_image, evidence=evidence)


def target_id(binding: JSON) -> str:
    """Resolve the verified host target without treating a config as executable."""
    from image_identity import validate_identity

    return validate_identity(binding["image_identity"], binding["image_id"])


def inspect_image(
    docker: list[str], environment: dict[str, str], reference: str, report: JSON, timeout: float
) -> JSON | None:
    """Inspect bounded selected fields; unknown daemon/identity state must fail."""
    selected = (
        '{"Id":{{json .Id}},"Os":{{json .Os}},"Architecture":{{json .Architecture}},'
        '"Labels":{{json .Config.Labels}}}'
    )
    argv = docker + ["image", "inspect", "--format", selected, reference]
    entry: JSON = {
        "argv": argv,
        "rc": None,
        "stdout": "",
        "stderr": "",
        "timeout_seconds": timeout,
        "output_limit_bytes": 1024 * 1024,
        "excluded_fields": ["Config.Env"],
    }
    report.setdefault("commands", []).append(entry)
    failure = None
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            result = subprocess.run(
                argv, env=environment, stdout=stdout, stderr=stderr, timeout=timeout
            )
            entry["rc"] = result.returncode
        except Exception as error:
            failure = error
            entry["error"] = type(error).__name__ + ": " + str(error)
            entry["timed_out"] = isinstance(error, subprocess.TimeoutExpired)
        for label, stream in [("stdout", stdout), ("stderr", stderr)]:
            stream.seek(0)
            data = stream.read(1024 * 1024 + 1)
            entry[label] = data[: 1024 * 1024].decode("utf-8", errors="replace")
            entry[label + "_truncated"] = len(data) > 1024 * 1024
    if failure is not None:
        raise failure
    require(
        not entry["stdout_truncated"] and not entry["stderr_truncated"],
        "image inspect exceeds evidence limit",
    )
    if entry["rc"] == 0:
        state: JSON = json.loads(entry["stdout"])
        require(
            isinstance(state, dict) and IMAGE_ID.fullmatch(state.get("Id", "")),
            "invalid image inspect identity",
        )
        return state
    missing = {
        prefix + "No such image: " + reference
        for prefix in ["", "Error: ", "Error response from daemon: "]
    }
    if (
        entry["rc"] == 1
        and entry["stdout"].strip() in ["", "[]"]
        and entry["stderr"].strip() in missing
    ):
        return None
    raise RuntimeError("image state is unknown; Docker inspect failed: " + entry["stderr"].strip())


def exported_identity(
    docker: list[str],
    environment: dict[str, str],
    target: str,
    expected_config: str,
    report: JSON,
    timeout: float,
) -> JSON:
    """Bind an actual loaded target to the locked config without executing it."""
    from image_identity import archive_identity

    require(IMAGE_ID.fullmatch(target), "export requires an immutable Docker target")
    argv = docker + ["image", "save", target]
    entry: JSON = {"argv": argv, "rc": None, "stderr": "", "timeout_seconds": timeout}
    report.setdefault("commands", []).append(entry)
    with tempfile.TemporaryFile() as stream, tempfile.TemporaryFile() as errors:
        try:
            result = subprocess.run(
                argv, env=environment, stdout=stream, stderr=errors, timeout=timeout
            )
            entry["rc"] = result.returncode
        except Exception as error:
            entry["error"] = type(error).__name__ + ": " + str(error)
            entry["timed_out"] = isinstance(error, subprocess.TimeoutExpired)
            raise
        finally:
            errors.seek(0)
            entry["stderr"] = errors.read(1024 * 1024).decode("utf-8", errors="replace")
            entry["export_bytes"] = stream.tell()
        require(result.returncode == 0, "Docker target export failed")
        evidence = report.setdefault("resolved_image", {})
        return archive_identity(stream, expected_config, target, evidence)


def image_present(binding: JSON, report: JSON, timeout: float) -> bool:
    """Distinguish an absent image from daemon or permission errors."""
    docker, environment = docker_binding(binding)
    target = target_id(binding)
    state = inspect_image(docker, environment, target, report, timeout)
    if state is not None:
        require(
            state["Id"] == target and state["Os"] == "linux" and state["Architecture"] == "amd64",
            "image identity/platform mismatch; expected pinned linux/amd64 image",
        )
        return True
    return False


def resolve_candidates(
    docker: list[str],
    environment: dict[str, str],
    candidates: list[str],
    expected_config: str,
    report: JSON,
    timeout: float,
) -> JSON:
    """Authenticate one locally executable target, including store conversions."""
    for candidate in dict.fromkeys(candidates):
        require(IMAGE_ID.fullmatch(candidate), "candidate target must be an immutable digest")
        state = inspect_image(docker, environment, candidate, report, timeout)
        if state is not None:
            require(state["Id"] == candidate, "Docker target changed during resolution")
            return exported_identity(
                docker, environment, candidate, expected_config, report, timeout
            )
    raise RuntimeError("Docker load/pull did not expose an observable immutable target")


def loaded_candidates(stdout: str, identity: JSON) -> list[str]:
    """Use only immutable IDs from verified metadata or Docker's load receipt."""
    return [
        identity["target"]["digest"],
        identity["image_id"],
        *re.findall(r"^Loaded image ID: (sha256:[0-9a-f]{64})$", stdout, re.MULTILINE),
    ]


def provision_image(
    binding: JSON, report: JSON, timeout: float, manifest: JSON | None = None
) -> None:
    """Import only the selected verified archive or explicitly pinned registry image."""
    source = binding["image_source"]
    require(
        source is not None,
        "pinned image unavailable without a source; supply an archive or registry digest",
    )
    docker, environment = docker_binding(binding)
    if source["kind"] in ["archive", "download"]:
        if source["kind"] == "download":
            from acquire import download_file

            report["download"] = download_file(
                source["url"], Path(source["path"]), source["sha256"], source["bytes"]
            )
        path = Path(source["path"])
        require(path.is_file(), "image archive is unavailable: " + str(path))
        # Retain one file descriptor across verification and import, avoiding
        # substitution of a different path between the hash and Docker load.
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
            report["archive"] = {
                "path": str(path),
                "sha256": digest.hexdigest(),
                "expected_sha256": source["sha256"],
                "bytes": stream.tell(),
                "verified_before_load": digest.hexdigest() == source["sha256"],
            }
            require(
                report["archive"]["verified_before_load"],
                "image archive SHA256 mismatch; Docker load was not run",
            )
            validate_docker_archive(stream, binding["image_id"], report["archive"])
            if manifest is not None:
                metadata = report["archive"]["image_validation"]
                require(
                    metadata["source_revision"] == manifest["source_sha"]
                    and metadata["project_version"] == manifest["project_version"],
                    "archive source/version differs from runtime lock; Docker load was not run",
                )
            stream.seek(0)
            loaded = command_run(
                docker + ["image", "load"], environment, report, timeout, stdin=stream
            )
        candidates = loaded_candidates(loaded.stdout, binding["image_identity"])
    else:
        validate_registry(source["reference"])
        command_run(
            docker + ["image", "pull", "--platform", "linux/amd64", source["reference"]],
            environment,
            report,
            timeout,
        )
        state = inspect_image(docker, environment, source["reference"], report, timeout)
        require(state is not None, "pulled registry digest is unavailable")
        assert state is not None
        candidates = [state["Id"]]
    binding["image_identity"] = resolve_candidates(
        docker, environment, candidates, binding["image_id"], report, timeout
    )
    if manifest is not None:
        metadata = report["resolved_image"]["image_validation"]
        require(
            metadata["source_revision"] == manifest["source_sha"]
            and metadata["project_version"] == manifest["project_version"],
            "loaded image source/version differs from runtime lock",
        )
    require(image_present(binding, report, timeout), "provisioning did not supply the pinned image")


def launcher_arguments(binding: JSON, name: str | None = None) -> list[str]:
    """Produce the unchanged launcher's exact argv without shell evaluation."""
    arguments = [str(SCRIPT_ROOT / "ada-mcp-launch"), "--image", target_id(binding)]
    for root in binding["roots"]:
        arguments.extend(["--root", root])
    for key in ["docker_host", "docker_context", "uid", "gid"]:
        if binding[key] is not None:
            arguments.extend(["--" + key.replace("_", "-"), str(binding[key])])
    if name is not None:
        arguments.extend(["--name", name])
    return arguments


def doctor(
    binding: JSON,
    manifest: JSON,
    report: JSON,
    output: Path | None,
    timeout: float,
    command_timeout: float,
) -> None:
    """Check the real pinned container and STDIO catalog, not project semantics."""
    # The entry point has verified these helper bytes before importing them.
    from mcp_client import Session

    require(
        image_present(binding, report, command_timeout),
        "pinned image missing; run bootstrap with this binding to restore its source",
    )
    docker, environment = docker_binding(binding)
    info = report.setdefault("doctor", {"container_inspections": []})
    observations = info["container_inspections"]
    name = "ada-mcp-doctor-" + uuid.uuid4().hex
    info["container_name"] = name
    require(
        inspect_container(docker, environment, name, observations, command_timeout) is None,
        "generated container name already exists",
    )
    session = None
    errors = []
    try:
        session = Session(
            ["/bin/bash"] + launcher_arguments(binding, name),
            timeout,
            output / "mcp" if output is not None else None,
        )
        info["initialize"] = session.initialize()
        catalog = session.tools()
        names = sorted(tool["name"] for tool in catalog)
        require(
            names == manifest["server_tools"], "server tool catalog differs from the runtime lock"
        )
        info["tools"] = names
        state = inspect_container(docker, environment, name, observations, command_timeout)
        require(
            state is not None and state["Image"] == target_id(binding), "container image mismatch"
        )
        assert state is not None
        require(
            state["Config"].get("Labels", {}).get("ada-mcp-generic") == "1",
            "launcher label missing",
        )
        require(
            state["HostConfig"]["ReadonlyRootfs"] and state["HostConfig"]["NetworkMode"] == "none",
            "container root/network isolation mismatch",
        )
        require(
            "ALL" in state["HostConfig"]["CapDrop"]
            and any(
                option.startswith("no-new-privileges")
                for option in state["HostConfig"]["SecurityOpt"]
            ),
            "container capability/security isolation mismatch",
        )
        for root in binding["roots"]:
            require(
                any(
                    mount["Destination"] == root and mount.get("RW") is False
                    for mount in state["Mounts"]
                ),
                "selected root is not mounted read-only at the same path: " + root,
            )
        probe = (
            "import json,os,platform,sys; print(json.dumps(dict(uid=os.getuid(),gid=os.getgid(),"
            'machine=platform.machine(),os_release=open("/etc/os-release").read(),'
            'home_writable=os.access(os.environ["HOME"],os.W_OK),'
            "roots=[dict(path=p,readable=os.path.isdir(p) and os.access(p,os.R_OK|os.X_OK)) "
            "for p in json.loads(sys.argv[1])])))"
        )
        runtime = json.loads(
            command_run(
                docker + ["exec", state["Id"], "python", "-c", probe, json.dumps(binding["roots"])],
                environment,
                report,
                command_timeout,
            ).stdout
        )
        require(
            runtime["uid"] == binding["uid"] and runtime["gid"] == binding["gid"],
            "runtime identity mismatch",
        )
        require(
            runtime["machine"] == "x86_64" and "VERSION_CODENAME=trixie" in runtime["os_release"],
            "runtime is not AMD64 Trixie",
        )
        require(
            runtime["home_writable"] and all(root["readable"] for root in runtime["roots"]),
            "private HOME or selected roots are inaccessible to the runtime identity",
        )
        info["runtime"] = runtime
        info["container_settings"] = {
            "image": state["Image"],
            "user": state["Config"]["User"],
            "host_config": state["HostConfig"],
            "mounts": state["Mounts"],
        }
    except Exception as error:
        errors.append(type(error).__name__ + ": " + str(error))
    finally:
        if session is not None:
            try:
                info["server_exit"] = session.close()
            except Exception as error:
                errors.append(type(error).__name__ + ": " + str(error))
            try:
                state = inspect_container(docker, environment, name, observations, command_timeout)
                if state is None:
                    info["cleanup"] = "absent-confirmed"
                elif any(item["status"] == "unknown" for item in observations):
                    info["cleanup"] = "unknown-no-removal"
                    errors.append("container state unknown; explicit cleanup refused")
                elif (
                    state["Image"] == target_id(binding)
                    and state["Config"].get("Labels", {}).get("ada-mcp-generic") == "1"
                ):
                    command_run(
                        docker + ["container", "rm", "-f", state["Id"]],
                        environment,
                        report,
                        command_timeout,
                    )
                    info["cleanup"] = "remaining-owned-container-removed"
                    errors.append("STDIN EOF did not remove the container")
                else:
                    info["cleanup"] = "identity-mismatch-no-removal"
                    errors.append("container identity changed; explicit cleanup refused")
            except Exception as error:
                info["cleanup"] = "unknown-no-removal"
                errors.append(type(error).__name__ + ": " + str(error))
    info["errors"] = errors
    require(not errors, "; ".join(errors))
    info["scope"] = "real container and MCP catalog; no project semantic or CI pass claimed"


def write_new(path: Path, content: str) -> None:
    """Atomically publish a new file without replacing an existing entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=path.parent, prefix=".ada-mcp-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink()


def toml_string_array(values: list[str]) -> str:
    """Preserve Unicode scalar values rather than emitting JSON surrogate pairs."""
    for value in values:
        value.encode("utf-8")
    return json.dumps(values, ensure_ascii=False).replace("\x7f", "\\u007f")


def new_binding(options: argparse.Namespace, manifest: JSON) -> JSON:
    """Construct a host binding only from explicit setup parameters."""
    require(options.root, "new bindings require at least one explicit --root")
    require(not options.archive_sha256 or options.archive, "--archive-sha256 requires --archive")
    source = None
    if options.archive:
        require(
            options.archive_sha256 and SHA256.fullmatch(options.archive_sha256),
            "--archive requires its trusted --archive-sha256",
        )
        source = {
            "kind": "archive",
            "path": str(absolute_path(options.archive, "archive path")),
            "sha256": options.archive_sha256,
        }
    elif options.image_cache:
        distribution = manifest["available_archive"]
        filename = distribution["filename"]
        require(
            Path(filename).name == filename and filename not in ["", ".", ".."],
            "invalid image archive name",
        )
        cache = absolute_path(options.image_cache, "image cache directory")
        source = {
            "kind": "download",
            "path": str(cache / filename),
            "url": distribution["download_url"],
            "sha256": distribution["sha256"],
            "bytes": distribution["bytes"],
        }
    elif options.registry:
        validate_registry(options.registry)
        source = {"kind": "registry", "reference": options.registry}
    return validate_binding(
        {
            "version": 2,
            "image_id": options.image_id or manifest["image_id"],
            "image_identity": manifest["image_identity"],
            "roots": [root.rstrip("/") or "/" for root in options.root],
            "docker_host": options.docker_host,
            "docker_context": options.docker_context,
            "uid": options.uid if options.uid is not None else os.getuid(),
            "gid": options.gid if options.gid is not None else os.getgid(),
            "image_source": source,
        },
        manifest,
    )


def install_skill(destination: Path, manifest: JSON, report: JSON) -> None:
    """Publish a complete skill with an atomic, no-replace symlink operation."""
    require(
        not os.path.lexists(destination), "install destination already exists; nothing overwritten"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Keep storage outside the discovery root so the copied tree and its link
    # cannot be discovered twice. A shallow non-discovery destination can use
    # its own parent rather than attempting to write the filesystem root.
    storage_parent = destination.parent.parent
    if storage_parent == Path("/"):
        storage_parent = destination.parent
    stage = Path(tempfile.mkdtemp(prefix=".ada-skill-", dir=storage_parent))
    published = False
    try:
        for name in list(manifest["files_sha256"]) + ["scripts/runtime-manifest.json"]:
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SKILL_ROOT / name, target)
        for name, digest in manifest["files_sha256"].items():
            require(
                sha256_file(stage / name) == digest, "installed skill checksum mismatch: " + name
            )
        launcher = stage / "scripts/ada-mcp-launch"
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
        # Symlinked skill folders are explicitly supported by Codex. Creating
        # the link is atomic and fails even if a competing empty directory exists.
        os.symlink(
            os.path.relpath(stage, destination.parent), destination, target_is_directory=True
        )
        published = True
        report.update(
            destination=str(destination),
            storage_directory=str(stage),
            publication="atomic no-replace symlink",
            skill="ada-development",
            permissions_prepared="launcher user execute bit only, after hash verification",
        )
    finally:
        if not published:
            shutil.rmtree(stage)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    setup = modes.add_parser(
        "bootstrap", help="create a host binding or restore its configured image"
    )
    setup.add_argument("--binding", required=True)
    setup.add_argument("--image-id")
    setup.add_argument("--root", action="append")
    selector = setup.add_mutually_exclusive_group()
    selector.add_argument("--docker-host")
    selector.add_argument("--docker-context")
    setup.add_argument("--uid", type=int)
    setup.add_argument("--gid", type=int)
    sources = setup.add_mutually_exclusive_group()
    sources.add_argument("--archive")
    sources.add_argument("--registry")
    sources.add_argument(
        "--image-cache", help="explicit cache directory for the locked release image archive"
    )
    setup.add_argument("--archive-sha256")
    check = modes.add_parser("doctor", help="check the actual host binding and MCP runtime")
    check.add_argument("--binding")
    for mode in [setup, check]:
        mode.add_argument("--output", help="new evidence directory")
        mode.add_argument("--timeout", type=float, default=60)
        mode.add_argument("--command-timeout", type=float, default=300)
    query = modes.add_parser("query", help="use the real optional MCP client with a host binding")
    query.add_argument("--binding")
    query.add_argument("--log-dir")
    query.add_argument("--name", help="optional exact Docker container name for observation")
    query.add_argument("--timeout", type=float, default=60)
    query.add_argument("request", nargs=argparse.REMAINDER)
    native = modes.add_parser("native-config", help="write a new native Desktop/CLI TOML fragment")
    native.add_argument("--binding")
    native.add_argument("--output", required=True)
    install = modes.add_parser(
        "install-skill", help="install the skill into an explicit new discovery directory"
    )
    install.add_argument("--destination", required=True)
    options = parser.parse_args()
    report: JSON = {"status": "failed", "operation": options.mode}
    output = None
    try:
        manifest = verified_manifest()
        if options.mode in ["bootstrap", "doctor"]:
            require(
                options.timeout > 0 and options.command_timeout > 0, "timeouts must be positive"
            )
            if options.output:
                candidate = absolute_path(options.output, "evidence directory")
                candidate.mkdir(parents=True, exist_ok=False)
                output = candidate
        if options.mode == "install-skill":
            install_skill(
                absolute_path(options.destination, "install destination"), manifest, report
            )
        else:
            path = binding_path(options.binding)
            report["binding"] = str(path)
            if options.mode == "bootstrap":
                exists = os.path.lexists(path)
                if exists:
                    require(
                        not any(
                            getattr(options, key) is not None
                            for key in [
                                "image_id",
                                "root",
                                "docker_host",
                                "docker_context",
                                "uid",
                                "gid",
                                "archive",
                                "archive_sha256",
                                "registry",
                                "image_cache",
                            ]
                        ),
                        "binding immutable; use it without overrides or choose a new file",
                    )
                    binding = read_binding(path, manifest)
                else:
                    binding = new_binding(options, manifest)
                # An explicitly supplied source for a new binding exercises its
                # real import/pull path even when the daemon already caches the ID.
                original_target = target_id(binding)
                if not exists and binding["image_source"] is not None:
                    provision_image(binding, report, options.command_timeout, manifest)
                elif not image_present(binding, report, options.command_timeout):
                    provision_image(binding, report, options.command_timeout, manifest)
                require(
                    not exists or target_id(binding) == original_target,
                    "restored store uses another target; choose a new explicit host binding",
                )
                doctor(binding, manifest, report, output, options.timeout, options.command_timeout)
                if not exists:
                    write_new(path, json.dumps(binding, indent=2) + "\n")
                report["binding_created"] = not exists
            else:
                binding = read_binding(path, manifest)
                if options.mode == "doctor":
                    doctor(
                        binding, manifest, report, output, options.timeout, options.command_timeout
                    )
                elif options.mode == "query":
                    require(
                        options.timeout > 0 and options.request,
                        "provide a positive timeout and tools/call/batch request",
                    )
                    require(
                        image_present(binding, report, 60), "locked image is missing; run bootstrap"
                    )
                    arguments = [
                        sys.executable,
                        str(SCRIPT_ROOT / "mcp_client.py"),
                    ] + launcher_arguments(binding)[1:]
                    arguments.extend(["--timeout", str(options.timeout)])
                    if options.log_dir:
                        arguments.extend(["--log-dir", options.log_dir])
                    arguments.extend(
                        ["--name", options.name or "ada-mcp-query-" + uuid.uuid4().hex]
                    )
                    arguments.extend(options.request)
                    os.execv(sys.executable, arguments)
                elif options.mode == "native-config":
                    from mcp_client import READ_TOOLS

                    require(
                        image_present(binding, report, 60), "locked image is missing; run bootstrap"
                    )
                    target = absolute_path(options.output, "native configuration output")
                    content = (
                        "# Generated native-client fragment; merge explicitly.\n"
                        '[mcp_servers.ada]\ncommand = "/bin/bash"\nargs = '
                        + toml_string_array(launcher_arguments(binding))
                        + "\nstartup_timeout_sec = 60\n"
                        "tool_timeout_sec = 120\nenabled_tools = "
                        + toml_string_array(sorted(READ_TOOLS))
                        + "\n"
                    )
                    write_new(target, content)
                    report["native_config"] = str(target)
                    report["installed_in_native_client"] = False
        report["status"] = "passed"
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    finally:
        if output is not None:
            (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

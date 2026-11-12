"""Acquisition regressions use controlled bytes, not fake Ada semantic evidence."""

import hashlib
import io
import json
import stat
import tarfile
from types import SimpleNamespace
from urllib.request import Request

import acquire
import pytest


def make_archive(extra=None, corrupt=False):
    files = {"LICENSE": b"MIT notice\n", "scripts/ada-mcp-launch": b"#!/bin/bash\nexit 0\n"}
    manifest = json.dumps(
        {"files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}
    ).encode()
    if corrupt:
        files["LICENSE"] = b"changed after declaration\n"
    files["scripts/runtime-manifest.json"] = manifest
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, data in files.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        if extra is not None:
            archive.addfile(extra, io.BytesIO(b""))
    data = output.getvalue()
    return data, hashlib.sha256(data).hexdigest(), hashlib.sha256(manifest).hexdigest()


def test_verified_materialization_and_only_launcher_execute(tmp_path):
    files = acquire.verified_files(*make_archive())
    target = tmp_path / "new runtime 😀"
    hashes = acquire.materialize(files, target)
    assert set(hashes) == set(files)
    assert stat.S_IMODE(target.stat().st_mode) == 0o700
    assert stat.S_IMODE((target / "scripts/ada-mcp-launch").stat().st_mode) == 0o744
    assert stat.S_IMODE((target / "LICENSE").stat().st_mode) == 0o644


@pytest.mark.parametrize("name", ["../escape", "/absolute", "x/../escape", "x\\evil", "./alias"])
def test_path_aliases_are_refused_before_materialization(name):
    with pytest.raises(ValueError, match="archive path"):
        acquire.verified_files(*make_archive(tarfile.TarInfo(name)))


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE])
def test_links_and_special_members_are_refused(kind):
    member = tarfile.TarInfo("special")
    member.type = kind
    member.linkname = "/outside"
    with pytest.raises(ValueError, match="special archive"):
        acquire.verified_files(*make_archive(member))


def test_duplicate_member_is_refused():
    with pytest.raises(ValueError, match="duplicate"):
        acquire.verified_files(*make_archive(tarfile.TarInfo("LICENSE")))


def test_outer_manifest_and_member_hashes_each_fail_for_their_reason():
    data, archive_hash, manifest_hash = make_archive()
    with pytest.raises(ValueError, match="archive SHA256"):
        acquire.verified_files(data, "0" * 64, manifest_hash)
    with pytest.raises(ValueError, match="manifest SHA256"):
        acquire.verified_files(data, archive_hash, "0" * 64)
    with pytest.raises(ValueError, match="file SHA256"):
        acquire.verified_files(*make_archive(corrupt=True))


def test_existing_destination_remains_untouched(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "marker").write_bytes(b"do not replace")
    with pytest.raises(ValueError, match="destination exists"):
        acquire.materialize(acquire.verified_files(*make_archive()), target)
    assert list(target.iterdir()) == [target / "marker"]
    assert (target / "marker").read_bytes() == b"do not replace"


@pytest.mark.parametrize(
    "url",
    [
        "http://example.invalid/file",
        "https://user:secret@example.invalid/file",
        "https://example.invalid/releases/latest/file",
    ],
)
def test_invalid_download_url_never_starts_transport(url, monkeypatch):
    monkeypatch.setattr(
        acquire.urllib.request, "build_opener", lambda *args: pytest.fail("transport started")
    )
    with pytest.raises(ValueError):
        acquire.download(url)


def test_https_redirect_downgrade_is_refused():
    with pytest.raises(ValueError, match="downgrade"):
        acquire.HTTPSRedirects().redirect_request(
            Request("https://example.invalid/a"), None, 302, "", {}, "http://example.invalid/b"
        )


@pytest.mark.parametrize(
    "data,expected_size,expected_hash",
    [
        (b"too long", 2, hashlib.sha256(b"to").hexdigest()),
        (b"short", 7, hashlib.sha256(b"shortxx").hexdigest()),
        (b"wrong", 5, hashlib.sha256(b"right").hexdigest()),
    ],
)
def test_image_stream_mismatch_is_not_published(
    tmp_path, monkeypatch, data, expected_size, expected_hash
):
    opener = SimpleNamespace(open=lambda *args, **kwargs: io.BytesIO(data))
    monkeypatch.setattr(acquire.urllib.request, "build_opener", lambda *args: opener)
    target = tmp_path / "image.tar.gz"
    with pytest.raises(ValueError):
        acquire.download_file("https://example.invalid/image", target, expected_hash, expected_size)
    assert not target.exists()
    assert not list(tmp_path.glob(".ada-image-*"))


def test_verified_image_cache_is_reused_without_transport(tmp_path, monkeypatch):
    data = b"verified archive bytes"
    target = tmp_path / "image.tar.gz"
    target.write_bytes(data)
    monkeypatch.setattr(
        acquire.urllib.request, "build_opener", lambda *args: pytest.fail("network used")
    )
    result = acquire.download_file(
        "https://example.invalid/image", target, hashlib.sha256(data).hexdigest(), len(data)
    )
    assert result["cache_hit"] is True
    target.write_bytes(b"changed")
    with pytest.raises(ValueError, match="nothing overwritten"):
        acquire.download_file(
            "https://example.invalid/image", target, hashlib.sha256(data).hexdigest(), len(data)
        )
    assert target.read_bytes() == b"changed"

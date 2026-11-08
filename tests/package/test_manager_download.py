# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=redefined-outer-name,protected-access,unused-argument

import hashlib
import json
import logging
import os
import threading
import time
from random import random
from typing import Optional

import pytest
import requests

from platformio import app, fs, telemetry
from platformio.package.download import (
    ArtifactVerificationError,
    ResponseValidationError,
    TransferInterruptedError,
)
from platformio.package.lockfile import LockFile
from platformio.package.manager import _download, _registry
from platformio.package.manager._download import DownloadAttempt, TrustedArtifact
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec

from .conftest import Reply, Request, Resource, TestServer, redirect

DATA = os.urandom(150 * 1024)
SHA256 = hashlib.sha256(DATA).hexdigest()
ETAG = '"v1"'
CUT = 50 * 1024
REAL_LOG_EVENT = telemetry.log_event


@pytest.fixture(autouse=True)
def events(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, dict]]:
    """Capture telemetry events; tests never send real ones."""
    logged: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        telemetry,
        "log_event",
        lambda name, params, instant_sending=False: logged.append((name, params)),
    )
    return logged


@pytest.fixture
def isolated_cache(
    func_isolated_pio_core,
    monkeypatch: pytest.MonkeyPatch,  # pylint: disable=unused-argument
) -> None:
    # the cache dir follows PLATFORMIO_CACHE_DIR when it is set
    monkeypatch.setenv(
        "PLATFORMIO_CACHE_DIR", os.path.join(str(func_isolated_pio_core), ".cache")
    )


@pytest.fixture
def pm(isolated_cache) -> ToolPackageManager:  # pylint: disable=unused-argument
    manager = ToolPackageManager()
    manager.set_log_level(logging.ERROR)
    return manager


def artifact(sha256: str = SHA256, size: Optional[int] = len(DATA)) -> TrustedArtifact:
    return TrustedArtifact(sha256, size)


def partial_paths(pm: ToolPackageManager, key: str) -> tuple[str, str]:
    base = os.path.join(pm.get_download_dir(), "partial", key)
    return base + ".part", base + ".json"


def read_state(pm: ToolPackageManager, key: str) -> dict:
    with open(partial_paths(pm, key)[1], encoding="utf8") as fp:
        return json.load(fp)


def test_trusted_artifact_validation() -> None:
    assert TrustedArtifact(SHA256.upper(), None).sha256 == SHA256
    for sha256 in ("", "abc", "g" * 64, hashlib.sha1(b"").hexdigest()):
        with pytest.raises(ValueError):
            TrustedArtifact(sha256, None)
    with pytest.raises(ValueError):
        TrustedArtifact(SHA256, -1)


#
# Trusted registry artifacts
#


def test_trusted_download_is_cached_by_sha256(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, etag=ETAG)
    path = pm.download(http_server.url("/a"), artifact())
    assert path == os.path.join(pm.get_download_dir(), SHA256)
    with open(path, "rb") as fp:
        assert fp.read() == DATA
    assert not os.listdir(os.path.join(pm.get_download_dir(), "partial"))
    # a different approved mirror hits the same cache entry
    assert pm.download(http_server.url("/other"), artifact()) == path
    assert len(http_server.requests) == 1


def test_trusted_resume_same_mirror(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, etag=ETAG, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    part, _ = partial_paths(pm, SHA256)
    assert os.path.getsize(part) == CUT
    state = read_state(pm, SHA256)
    assert state["mode"] == "trusted" and state["total_size"] == len(DATA)

    path = pm.download(http_server.url("/a"), artifact())
    with open(path, "rb") as fp:
        assert fp.read() == DATA
    resumed = http_server.requests[-1]
    assert resumed.headers["Range"] == "bytes=%d-" % CUT
    assert "If-Range" not in resumed.headers


def test_trusted_resume_cross_mirror(
    pm: ToolPackageManager, http_server: TestServer, mirror_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, etag=ETAG, cuts=[CUT])
    # mirror B redirects to its delivery host as part of the same attempt
    mirror_server.routes["/b"] = redirect("/assets/b")
    mirror_server.routes["/assets/b"] = Resource(DATA, etag='"mirror-b"')
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())

    path = pm.download(mirror_server.url("/b"), artifact())
    with open(path, "rb") as fp:
        assert fp.read() == DATA
    for request in mirror_server.requests:
        assert request.headers["Range"] == "bytes=%d-" % CUT
        assert "If-Range" not in request.headers
        assert ETAG not in request.headers.values()


def test_trusted_complete_partial_accepts_416(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    # interrupted after the last byte, before cache promotion
    http_server.routes["/a"] = Resource(DATA)
    part, state = partial_paths(pm, SHA256)
    os.makedirs(os.path.dirname(part), exist_ok=True)
    with open(part, "wb") as fp:
        fp.write(DATA)
    with open(state, "w", encoding="utf8") as fp:
        json.dump(
            {
                "version": 1,
                "mode": "trusted",
                "key": SHA256,
                "url": http_server.url("/a"),
                "effective_url": http_server.url("/a"),
                "sha256": SHA256,
                "expected_size": len(DATA),
                "total_size": len(DATA),
                "segments": [
                    {
                        "start": 0,
                        "url": http_server.url("/a"),
                        "effective_url": http_server.url("/a"),
                    }
                ],
            },
            fp,
        )
    pm.download(http_server.url("/a"), artifact())
    (request,) = http_server.requests
    assert request.headers["Range"] == "bytes=%d-" % len(DATA)


def test_trusted_sha256_mismatch_discards_partial(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    other = bytes(len(DATA))
    http_server.routes["/a"] = Resource(other, etag=ETAG)
    with pytest.raises(ArtifactVerificationError, match="SHA256"):
        pm.download(http_server.url("/a"), artifact())
    assert not any(os.path.exists(p) for p in partial_paths(pm, SHA256))
    assert not os.path.exists(os.path.join(pm.get_download_dir(), SHA256))


def test_trusted_size_mismatch_discards_partial(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    # correct content, but the server sends no length; size is checked
    # independently of SHA256
    http_server.routes["/a"] = Resource(DATA, send_length=False)
    with pytest.raises(ArtifactVerificationError, match="size"):
        pm.download(http_server.url("/a"), artifact(size=len(DATA) + 1))
    assert not any(os.path.exists(p) for p in partial_paths(pm, SHA256))


def test_trusted_size_conflict_keeps_partial(
    pm: ToolPackageManager, http_server: TestServer, mirror_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    # mirror B serves something of another size: rejected before truncation
    mirror_server.routes["/b"] = Resource(DATA + b"x", accept_ranges=False)
    with pytest.raises(ResponseValidationError):
        pm.download(mirror_server.url("/b"), artifact())
    assert os.path.getsize(partial_paths(pm, SHA256)[0]) == CUT


def test_overlong_range_body_discards_partial(
    pm: ToolPackageManager, http_server: TestServer, mirror_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    # a close-delimited 206 that sends more than its Content-Range declares
    mirror_server.routes["/b"] = lambda _: Reply(
        206,
        {"Content-Range": "bytes %d-%d/%d" % (CUT, len(DATA) - 1, len(DATA))},
        DATA[CUT:] + bytes(200 * 1024),
    )
    with pytest.raises(ResponseValidationError):
        pm.download(mirror_server.url("/b"), artifact())
    assert not any(os.path.exists(p) for p in partial_paths(pm, SHA256))


def test_artifact_is_hashed_while_streaming(
    pm: ToolPackageManager,
    http_server: TestServer,
    mirror_server: TestServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def no_read_back(*_):
        raise AssertionError("the downloaded file must not be read back to hash it")

    monkeypatch.setattr(fs, "calculate_file_hashsum", no_read_back)
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    mirror_server.routes["/b"] = Resource(DATA)
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    # resumed: the hash is seeded from the partial, then fed the new bytes
    path = pm.download(mirror_server.url("/b"), artifact())
    assert os.path.basename(path) == SHA256


def test_old_checksum_argument_is_rejected_clearly(pm: ToolPackageManager) -> None:
    with pytest.raises(TypeError, match="TrustedArtifact"):
        pm.download("https://example.com/f.tar.gz", SHA256)


@pytest.mark.parametrize(
    "field,value",
    [
        ("effective_url", 123),
        ("effective_url", None),
        ("segments", [{"start": 0, "url": 1, "effective_url": "x"}]),
        ("segments", [{"start": "0", "url": "x", "effective_url": "x"}]),
        ("encoding", None),
        ("updated", "now"),
    ],
)
def test_malformed_state_fields_restart(
    pm: ToolPackageManager, http_server: TestServer, field: str, value
) -> None:
    url = http_server.url("/ext")
    http_server.routes["/ext"] = Resource(DATA, etag=ETAG, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(url)
    key = os.path.basename(pm.compute_download_path(url, ""))
    state = read_state(pm, key)
    state[field] = value
    with open(partial_paths(pm, key)[1], "w", encoding="utf8") as fp:
        json.dump(state, fp)
    pm.download(url)
    # discarded up front: no wasted Range request before the clean download
    assert len(http_server.requests) == 2
    assert "Range" not in http_server.requests[-1].headers


def test_partial_larger_than_total_restarts(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    part, _ = partial_paths(pm, SHA256)
    with open(part, "ab") as fp:
        fp.write(bytes(len(DATA)))
    pm.download(http_server.url("/a"), artifact())
    assert "Range" not in http_server.requests[-1].headers


def test_corrupt_state_restarts(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    with open(partial_paths(pm, SHA256)[1], "w", encoding="utf8") as fp:
        fp.write("{not json")
    pm.download(http_server.url("/a"), artifact())
    assert "Range" not in http_server.requests[-1].headers


def test_state_records_provenance(
    pm: ToolPackageManager, http_server: TestServer, mirror_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    mirror_server.routes["/b"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    with pytest.raises(TransferInterruptedError):
        pm.download(mirror_server.url("/b"), artifact())
    segments = read_state(pm, SHA256)["segments"]
    assert [(s["start"], s["url"]) for s in segments] == [
        (0, http_server.url("/a")),
        (CUT, mirror_server.url("/b")),
    ]


#
# External URLs
#


def test_external_download_without_checksum(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    url = http_server.url("/ext.tar.gz")
    http_server.routes["/ext.tar.gz"] = Resource(DATA)
    path = pm.download(url)
    assert path == pm.compute_download_path(url, "")
    with open(path, "rb") as fp:
        assert fp.read() == DATA


def test_resume_partial_disabled_starts_clean(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    pm.download(http_server.url("/a"), artifact(), resume_partial=False)
    assert "Range" not in http_server.requests[-1].headers


def test_verification_error_reports_resumed_data(
    pm: ToolPackageManager, http_server: TestServer, mirror_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(bytes(len(DATA)), cuts=[CUT])
    mirror_server.routes["/b"] = Resource(DATA)
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    with pytest.raises(ArtifactVerificationError) as exc_info:
        pm.download(mirror_server.url("/b"), artifact())
    assert exc_info.value.resumed
    # a clean download from the same mirror succeeds
    pm.download(mirror_server.url("/b"), artifact())
    with pytest.raises(ArtifactVerificationError) as exc_info:
        pm.download(http_server.url("/a"), artifact(sha256="0" * 64))
    assert not exc_info.value.resumed


def test_external_without_validator_is_not_kept(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    url = http_server.url("/ext")
    http_server.routes["/ext"] = Resource(DATA, etag='W/"weak"', cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(url)
    assert not os.listdir(os.path.join(pm.get_download_dir(), "partial"))


def test_external_resume_with_strong_etag(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    url = http_server.url("/ext")
    http_server.routes["/ext"] = Resource(DATA, etag=ETAG, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(url)
    path = pm.download(url)
    with open(path, "rb") as fp:
        assert fp.read() == DATA
    resumed = http_server.requests[-1]
    assert resumed.headers["Range"] == "bytes=%d-" % CUT
    assert resumed.headers["If-Range"] == ETAG


def test_external_resume_with_strong_last_modified(
    pm: ToolPackageManager, http_server: TestServer, strong_dates: tuple[str, str]
) -> None:
    lm, date = strong_dates
    url = http_server.url("/ext")
    http_server.routes["/ext"] = Resource(DATA, last_modified=lm, date=date, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(url)
    pm.download(url)
    assert http_server.requests[-1].headers["If-Range"] == lm


def test_external_redirect_target_change_restarts(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    def changing_redirect(request: Request) -> Reply:
        # the first attempt is redirected to /v1, later ones to /v2
        first = len(http_server.requests_for("/ext")) == 1
        return redirect("/v1" if first else "/v2")(request)

    http_server.routes["/ext"] = changing_redirect
    http_server.routes["/v1"] = Resource(DATA, etag=ETAG, cuts=[CUT])
    http_server.routes["/v2"] = Resource(DATA, etag=ETAG)
    url = http_server.url("/ext")
    with pytest.raises(TransferInterruptedError):
        pm.download(url)
    path = pm.download(url)
    with open(path, "rb") as fp:
        assert fp.read() == DATA
    assert "Range" not in http_server.requests[-1].headers


def test_external_partial_of_other_url_is_not_reused(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/ext"] = Resource(DATA, etag=ETAG, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/ext"))
    http_server.routes["/ext2"] = Resource(DATA, etag=ETAG)
    pm.download(http_server.url("/ext2"))
    assert "Range" not in http_server.requests[-1].headers


#
# Lifecycle
#


def test_cleanup_expired_partials(pm: ToolPackageManager) -> None:
    partial_dir = os.path.join(pm.get_download_dir(), "partial")
    os.makedirs(partial_dir)
    expired = time.time() - pm.DOWNLOAD_CACHE_EXPIRE - 10
    keys = {
        name: hashlib.sha1(name.encode()).hexdigest()
        for name in ("old", "fresh", "locked", "orphan")
    }
    files = {
        "old": (".part", ".json"),
        "fresh": (".part", ".json"),
        "locked": (".part", ".json"),
        "orphan": (".part",),
    }
    for name, exts in files.items():
        for ext in exts:
            path = os.path.join(partial_dir, keys[name] + ext)
            with open(path, "wb") as fp:
                fp.write(b"x")
            if name != "fresh":
                os.utime(path, (expired, expired))
    # files that are not partial downloads expire on their own mtime
    for name, mtime in (
        (".DS_Store", expired),
        ("k.part.bak", expired),
        ("fresh.stray", time.time()),
    ):
        with open(os.path.join(partial_dir, name), "wb") as fp:
            fp.write(b"x")
        os.utime(os.path.join(partial_dir, name), (mtime, mtime))
    with LockFile(os.path.join(pm.get_download_dir(), keys["locked"])):
        pm.cleanup_expired_downloads(random())
    assert sorted(os.listdir(partial_dir)) == sorted(
        [
            keys["fresh"] + ".json",
            keys["fresh"] + ".part",
            "fresh.stray",
            keys["locked"] + ".json",
            keys["locked"] + ".part",
        ]
    )


def test_cleanup_tolerates_download_finishing_concurrently(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    partial_dir = os.path.join(pm.get_download_dir(), "partial")
    os.makedirs(partial_dir)
    expired = time.time() - pm.DOWNLOAD_CACHE_EXPIRE - 10
    key = hashlib.sha1(b"k").hexdigest()
    paths = [os.path.join(partial_dir, key + ext) for ext in (".part", ".json")]
    for path in paths:
        with open(path, "wb") as fp:
            fp.write(b"x")
        os.utime(path, (expired, expired))

    class FinishingLock(LockFile):
        # another process promoted the partial right before we got the lock
        def __enter__(self) -> None:
            for path in paths:
                os.remove(path)
            super().__enter__()

    monkeypatch.setattr(_download, "LockFile", FinishingLock)
    pm.cleanup_expired_downloads(random())
    assert not os.listdir(partial_dir)


def test_cleanup_skips_files_that_cannot_be_removed(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    partial_dir = os.path.join(pm.get_download_dir(), "partial")
    os.makedirs(partial_dir)
    expired = time.time() - pm.DOWNLOAD_CACHE_EXPIRE - 10
    busy, free = hashlib.sha1(b"busy").hexdigest(), hashlib.sha1(b"free").hexdigest()
    for name in (busy + ".part", free + ".part", ".DS_Store"):
        path = os.path.join(partial_dir, name)
        with open(path, "wb") as fp:
            fp.write(b"x")
        os.utime(path, (expired, expired))
    real_remove = os.remove

    def remove(path: str) -> None:
        # e.g. an antivirus scanner holds the file open on Windows
        if os.path.basename(path) in (busy + ".part", ".DS_Store"):
            raise PermissionError(path)
        real_remove(path)

    monkeypatch.setattr(os, "remove", remove)
    pm.cleanup_expired_downloads(random())
    assert sorted(os.listdir(partial_dir)) == sorted([busy + ".part", ".DS_Store"])


def test_concurrent_downloads_share_one_transfer(
    isolated_cache, http_server: TestServer  # pylint: disable=unused-argument
) -> None:
    resource = Resource(DATA, stall=0.5)
    http_server.routes["/a"] = resource
    results: list[str] = []
    errors: list[BaseException] = []

    def worker() -> None:
        manager = ToolPackageManager()
        manager.set_log_level(logging.ERROR)
        try:
            results.append(manager.download(http_server.url("/a"), artifact()))
        except BaseException as exc:  # pylint: disable=broad-except
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert not errors
    assert len(set(results)) == 1 and len(results) == 2
    assert len(http_server.requests) == 1


#
# Registry mirror authorization
#


class FakeMirrors:
    """Stands in for RegistryFileMirrorIterator: mirror N is `mirror-<abc...>`."""

    def __init__(self, mirrors, download_url, get_resume_offset=None) -> None:
        self.mirrors = list(mirrors)
        self.download_url = download_url
        self.get_resume_offset = get_resume_offset
        self.offsets: list[int] = []
        self.mirror: Optional[str] = None

    def __iter__(self):
        for index, (url, checksum) in enumerate(self.mirrors):
            self.offsets.append(self.get_resume_offset())
            self.mirror = "mirror-" + "abcdefgh"[index]
            yield url, checksum


def _patch_registry(
    pm: ToolPackageManager,
    monkeypatch: pytest.MonkeyPatch,
    mirrors: list[tuple[str, Optional[str]]],
    install_from_uri,
) -> list[FakeMirrors]:
    """Return the mirror iterators created (one per registry lookup)."""
    iterators: list[FakeMirrors] = []
    pkgfile = {
        "download_url": "https://dl.example.com/t.tar.gz",
        "checksum": {"sha256": SHA256},
        "size": len(DATA),
    }
    package = {"id": 1, "name": "t", "owner": {"username": "o"}, "versions": []}

    def mirror_iterator(download_url: str, get_resume_offset=None):
        iterators.append(FakeMirrors(mirrors, download_url, get_resume_offset))
        return iterators[-1]

    monkeypatch.setattr(_registry, "RegistryFileMirrorIterator", mirror_iterator)
    monkeypatch.setattr(pm, "fetch_registry_package", lambda _: package)
    monkeypatch.setattr(pm, "pick_best_registry_version", lambda *_: {"files": []})
    monkeypatch.setattr(pm, "pick_compatible_pkg_file", lambda _: pkgfile)
    monkeypatch.setattr(pm, "install_from_uri", install_from_uri)
    return iterators


MIRRORS = [
    ("https://mirror-a.example.com/t.tar.gz", SHA256),
    ("https://mirror-b.example.com/t.tar.gz", None),
    ("https://mirror-c.example.com/t.tar.gz", None),
]
A, B, C = (url for url, _ in MIRRORS)


def test_registry_retries_only_resumed_failures_clean(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, bool]] = []

    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        calls.append((url, resume_partial))
        if not resume_partial:
            return "installed"
        # A resumed a bad partial; B and C failed on clean downloads
        raise ArtifactVerificationError("mismatch", resumed=url == A)

    iterators = _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert calls == [(A, True), (B, True), (C, True), (A, False)]
    assert len(iterators) == 1  # no second pass over the mirrors


def test_registry_clean_retries_stop_after_one_attempt_each(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, bool]] = []

    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        calls.append((url, resume_partial))
        if url == C:
            raise TransferInterruptedError("network")
        raise ArtifactVerificationError("mismatch", resumed=resume_partial)

    iterators = _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) is None
    # interruptions are never retried within one install; partials are kept
    assert calls == [(A, True), (B, True), (C, True), (A, False), (B, False)]
    assert len(iterators) == 1


def test_registry_no_clean_pass_without_resumed_failure(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        calls.append(url)
        raise ArtifactVerificationError("bad mirror", resumed=False)

    _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) is None
    assert calls == [A, B, C]


@pytest.mark.parametrize(
    "checksum,size",
    [({"sha256": "not-a-sha256"}, 1), ({}, 1), (None, 1), ({"sha256": SHA256}, "1")],
    ids=["invalid-sha256", "missing-sha256", "no-checksum", "non-int-size"],
)
def test_registry_invalid_artifact_metadata(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch, checksum, size
) -> None:
    calls: list[str] = []
    _patch_registry(pm, monkeypatch, MIRRORS, lambda url, *_, **__: calls.append(url))
    monkeypatch.setattr(
        pm,
        "pick_compatible_pkg_file",
        lambda _: {
            "download_url": "https://dl.example.com/t.tar.gz",
            "checksum": checksum,
            "size": size,
        },
    )
    assert pm.install_from_registry(PackageSpec("o/t")) is None
    assert not calls


def test_registry_skips_mirror_with_other_sha256(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    mirrors = [
        ("https://mirror-a.example.com/t.tar.gz", "f" * 64),
        ("https://mirror-b.example.com/t.tar.gz", SHA256.upper()),
    ]
    calls: list[tuple[str, TrustedArtifact]] = []
    _patch_registry(
        pm,
        monkeypatch,
        mirrors,
        lambda url, spec, artifact, **_: calls.append((url, artifact)) or "installed",
    )
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert calls == [(mirrors[1][0], TrustedArtifact(SHA256, len(DATA)))]


#
# Download telemetry and the registry resume hint
#

EVENT_PARAMS = {
    "outcome",
    "sha256",
    "total",
    "mirror",
    "host",
    "pass",
    "attempt",
    "range_sent",
    "status",
    "offset",
    "received",
    "ttfb",
    "transfer_time",
    "speed",
    "duration",
    "error",
    "error_cause",
    "proxy",
    "ci",
}


def transfer(attempt: DownloadAttempt, **fields) -> None:
    """Simulate what download() records for one transfer."""
    attempt.transferred = True
    for name, value in fields.items():
        setattr(attempt, name, value)


def test_attempt_records_interrupted_and_resumed_transfer(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    first = DownloadAttempt()
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact(), attempt=first)
    assert first.transferred and not first.completed
    assert first.status == 200 and first.received == CUT
    assert not first.range_sent and not first.offset
    assert first.host == "127.0.0.1"
    assert first.duration >= first.ttfb >= 0 and first.transfer_time >= 0

    second = DownloadAttempt()
    pm.download(http_server.url("/a"), artifact(), attempt=second)
    assert second.transferred and second.completed
    assert second.range_sent and second.status == 206 and second.offset == CUT
    assert second.received == len(DATA) - CUT

    # a cache hit transfers nothing
    third = DownloadAttempt()
    pm.download(http_server.url("/a"), artifact(), attempt=third)
    assert third == DownloadAttempt()


def test_attempt_records_ignored_range(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    http_server.routes["/a"] = Resource(DATA, accept_ranges=False, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    attempt = DownloadAttempt()
    pm.download(http_server.url("/a"), artifact(), attempt=attempt)
    assert (attempt.range_sent, attempt.status, attempt.offset) == (True, 200, 0)
    assert attempt.received == len(DATA)


def test_attempt_records_rejected_status(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    attempt = DownloadAttempt()
    with pytest.raises(ResponseValidationError) as exc_info:
        pm.download(http_server.url("/missing"), artifact(), attempt=attempt)
    assert exc_info.value.status_code == 404
    assert attempt.transferred and attempt.status == 404


def test_resume_offset_of_partial(
    pm: ToolPackageManager, http_server: TestServer
) -> None:
    assert pm.get_resume_offset(artifact()) == 0
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    with pytest.raises(TransferInterruptedError):
        pm.download(http_server.url("/a"), artifact())
    assert pm.get_resume_offset(artifact()) == CUT
    assert pm.get_resume_offset(artifact(sha256="0" * 64)) == 0
    assert pm.get_resume_offset(artifact(size=CUT - 1)) == 0
    # read-only: an unusable partial reports 0 and is left for download()
    part, state = partial_paths(pm, SHA256)
    with open(state, "w", encoding="utf8") as fp:
        fp.write("{")
    assert pm.get_resume_offset(artifact()) == 0
    assert os.path.isfile(part) and os.path.isfile(state)


def test_registry_logs_event_per_attempt(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch, events
) -> None:
    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        if url == A:
            transfer(attempt, status=200, received=CUT, transfer_time=0.5)
            try:
                raise requests.ReadTimeout("slow")
            except requests.ReadTimeout as exc:
                raise TransferInterruptedError("interrupted") from exc
        transfer(
            attempt,
            range_sent=True,
            status=206,
            offset=CUT,
            received=len(DATA) - CUT,
            completed=True,
        )
        return "installed"

    _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert [name for name, _ in events] == ["pkg_download"] * 2
    first, second = (params for _, params in events)
    assert set(first) == EVENT_PARAMS and set(second) == EVENT_PARAMS
    assert {k: first[k] for k in EVENT_PARAMS - {"proxy", "ci"}} == {
        "outcome": "interrupted",
        "sha256": SHA256,
        "total": len(DATA),
        "mirror": "mirror-a",
        "host": "",
        "pass": "main",
        "attempt": 1,
        "range_sent": False,
        "status": 200,
        "offset": 0,
        "received": CUT,
        "ttfb": 0,
        "transfer_time": 0.5,
        "speed": CUT * 2,
        "duration": 0,
        "error": "TransferInterruptedError",
        "error_cause": "ReadTimeout",
    }
    assert second["outcome"] == "completed" and second["error"] == ""
    assert second["mirror"] == "mirror-b" and second["attempt"] == 2
    assert second["range_sent"] and second["offset"] == CUT
    for _, params in events:
        assert not any("://" in str(v) or "t.tar.gz" in str(v) for v in params.values())


def test_registry_logs_skipped_and_clean_pass(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch, events
) -> None:
    mirrors = [(A, "f" * 64), (B, None)]

    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        transfer(attempt, status=206 if resume_partial else 200)
        if resume_partial:
            raise ArtifactVerificationError("mismatch", resumed=True)
        transfer(attempt, completed=True)
        return "installed"

    _patch_registry(pm, monkeypatch, mirrors, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert [
        (p["outcome"], p["mirror"], p["pass"], p["attempt"], p["status"])
        for _, p in events
    ] == [
        ("skipped", "mirror-a", "main", 1, 0),
        ("verification_failed", "mirror-b", "main", 2, 206),
        ("completed", "mirror-b", "clean", 3, 200),
    ]


def test_registry_logs_no_event_for_cache_hit(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch, events
) -> None:
    _patch_registry(pm, monkeypatch, MIRRORS, lambda *_, **__: "installed")
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert not events


def test_registry_completed_outcome_survives_install_failure(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch, events
) -> None:
    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        if url == A:
            transfer(attempt, status=200, completed=True)
            raise RuntimeError("cannot unpack")
        return "installed"  # the artifact is in the download cache now

    _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert [(p["outcome"], p["error"]) for _, p in events] == [("completed", "")]


def test_registry_logs_cancelled_download(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch, events
) -> None:
    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        transfer(attempt, status=200, received=CUT)
        raise KeyboardInterrupt

    _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    with pytest.raises(KeyboardInterrupt):
        pm.install_from_registry(PackageSpec("o/t"))
    assert [(p["outcome"], p["error"]) for _, p in events] == [
        ("cancelled", "KeyboardInterrupt")
    ]


def test_registry_telemetry_failure_does_not_affect_install(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken_log_event(*_, **__):
        raise RuntimeError("telemetry is broken")

    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        transfer(attempt, status=200, completed=True)
        return "installed"

    monkeypatch.setattr(telemetry, "log_event", broken_log_event)
    _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"


def test_registry_respects_disabled_telemetry(
    pm: ToolPackageManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    def install_from_uri(url, spec, artifact, resume_partial=True, attempt=None):
        transfer(attempt, status=200, completed=True)
        return "installed"

    monkeypatch.setattr(telemetry, "log_event", REAL_LOG_EVENT)
    app.set_setting("enable_telemetry", False)
    logger = telemetry.TelemetryLogger()
    pending = len(logger.get_unsent_events())
    _patch_registry(pm, monkeypatch, MIRRORS, install_from_uri)
    assert pm.install_from_registry(PackageSpec("o/t")) == "installed"
    assert len(logger.get_unsent_events()) == pending


def test_registry_resume_end_to_end(
    pm: ToolPackageManager,
    monkeypatch: pytest.MonkeyPatch,
    http_server: TestServer,
    mirror_server: TestServer,
    events,
) -> None:
    http_server.routes["/a"] = Resource(DATA, cuts=[CUT])
    mirror_server.routes["/b"] = Resource(DATA)
    mirrors = [(http_server.url("/a"), None), (mirror_server.url("/b"), None)]
    iterators = _patch_registry(pm, monkeypatch, mirrors, pm.install_from_uri)
    # the artifact downloads, but random bytes are not an installable archive
    assert pm.install_from_registry(PackageSpec("o/t")) is None
    # the registry lookup for the second mirror carries the resume offset
    assert iterators[0].offsets == [0, CUT]
    assert [
        (p["outcome"], p["host"], p["status"], p["offset"], p["received"])
        for _, p in events
    ] == [
        ("interrupted", "127.0.0.1", 200, 0, CUT),
        ("completed", "127.0.0.1", 206, CUT, len(DATA) - CUT),
    ]

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

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, Optional

from platformio import app, compat, util
from platformio.package.download import (
    ArtifactVerificationError,
    DownloadError,
    FileDownloader,
    ResponseInfo,
    ResponseValidationError,
    ResumePoint,
)
from platformio.package.lockfile import (
    LOCKFILE_DELAY,
    LockFile,
    LockFileExists,
    LockFileTimeoutError,
)

MODE_TRUSTED = "trusted"
MODE_EXTERNAL = "external"
STATE_VERSION = 1

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
# <sha256 or sha1(url)>.part / .json / .json.tmp
_PARTIAL_NAME_RE = re.compile(r"^([0-9a-f]{64}|[0-9a-f]{40})\.(part|json|json\.tmp)$")


@dataclass(frozen=True)
class TrustedArtifact:
    """A registry artifact identified by its trusted SHA256.

    Passing it to ``download()`` authorizes reusing a partial file across
    approved mirrors; the complete file is verified before cache promotion.
    """

    sha256: str
    size: Optional[int] = None

    def __post_init__(self) -> None:
        sha256 = self.sha256.lower() if isinstance(self.sha256, str) else ""
        if not _SHA256_RE.match(sha256):
            raise ValueError("Invalid SHA256 checksum '%s'" % self.sha256)
        if self.size is not None and (not isinstance(self.size, int) or self.size < 0):
            raise ValueError("Invalid artifact size '%s'" % self.size)
        object.__setattr__(self, "sha256", sha256)


@dataclass(frozen=True)
class DownloadTarget:
    mode: str
    key: str
    cache_path: str
    partial_path: str
    state_path: str


@dataclass(frozen=True)
class Segment:
    start: int
    url: str
    effective_url: str


@dataclass
class PartialState:  # pylint: disable=too-many-instance-attributes
    mode: str
    key: str
    url: str
    effective_url: str
    sha256: Optional[str] = None
    expected_size: Optional[int] = None
    total_size: Optional[int] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    encoding: str = "identity"
    segments: list[Segment] = field(default_factory=list)
    updated: float = 0

    @classmethod
    def load(cls, path: str) -> Optional["PartialState"]:
        try:
            with open(path, encoding="utf8") as fp:
                data = json.load(fp)
            if data.pop("version") != STATE_VERSION:
                return None
            data["segments"] = [Segment(**item) for item in data["segments"]]
            state = cls(**data)
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            return None
        return state if state.is_well_formed() else None

    def save(self, path: str) -> None:
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf8") as fp:
            json.dump(dict(version=STATE_VERSION, **asdict(self)), fp)
        os.replace(tmp_path, path)

    def is_well_formed(self) -> bool:
        strs = (self.mode, self.key, self.url, self.effective_url, self.encoding)
        optional_ints = (self.expected_size, self.total_size)
        optional_strs = (self.sha256, self.etag, self.last_modified)
        return (
            all(isinstance(v, str) for v in strs)
            and all(v is None or isinstance(v, int) for v in optional_ints)
            and all(v is None or isinstance(v, str) for v in optional_strs)
            and isinstance(self.updated, (int, float))
            and all(
                isinstance(s.start, int)
                and isinstance(s.url, str)
                and isinstance(s.effective_url, str)
                for s in self.segments
            )
        )

    def validator(self) -> Optional[str]:
        return self.etag or self.last_modified


class PackageManagerDownloadMixin:
    DOWNLOAD_CACHE_EXPIRE = 86400 * 30  # keep package in a local cache for 1 month

    def compute_download_path(self, *args):
        request_hash = hashlib.new("sha1")
        for arg in args:
            request_hash.update(compat.hashlib_encode_data(arg))
        dl_path = os.path.join(self.get_download_dir(), request_hash.hexdigest())
        return dl_path

    def get_download_usagedb_path(self):
        return os.path.join(self.get_download_dir(), "usage.db")

    def get_partial_download_dir(self) -> str:
        return self.ensure_dir_exists(os.path.join(self.get_download_dir(), "partial"))

    def set_download_utime(self, path, utime=None):
        with app.State(self.get_download_usagedb_path(), lock=True) as state:
            state[os.path.basename(path)] = int(time.time() if not utime else utime)

    @util.memoized(DOWNLOAD_CACHE_EXPIRE)
    def cleanup_expired_downloads(self, _=None):
        with app.State(self.get_download_usagedb_path(), lock=True) as state:
            # remove outdated
            for fname in list(state.keys()):
                if state[fname] > (time.time() - self.DOWNLOAD_CACHE_EXPIRE):
                    continue
                del state[fname]
                dl_path = os.path.join(self.get_download_dir(), fname)
                if os.path.isfile(dl_path):
                    os.remove(dl_path)
        self._cleanup_expired_partials()

    def _cleanup_expired_partials(self) -> None:
        partial_dir = self.get_partial_download_dir()
        keys = set()
        for name in os.listdir(partial_dir):
            match = _PARTIAL_NAME_RE.match(name)
            if match:
                keys.add(match.group(1))
            else:
                self._remove_expired_stray_file(os.path.join(partial_dir, name))
        for key in keys:
            # the mode is unknown here and irrelevant for the paths
            target = self._make_download_target(MODE_EXTERNAL, key)
            if not self._is_partial_expired(target):
                continue
            try:
                # a single non-blocking attempt: skip a download in progress
                with LockFile(target.cache_path, timeout=LOCKFILE_DELAY):
                    # recheck: a download may have finished before we locked
                    if self._is_partial_expired(target):
                        self._discard_partial(target)
            except (LockFileExists, LockFileTimeoutError):
                continue
            except OSError:
                continue  # e.g. held open on Windows; retried by a later cleanup

    def _remove_expired_stray_file(self, path: str) -> None:
        # not a partial download, so no download can be using it
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < (
                time.time() - self.DOWNLOAD_CACHE_EXPIRE
            ):
                os.remove(path)
        except OSError:
            pass  # removed concurrently or held open; retried by a later cleanup

    def _is_partial_expired(self, target: DownloadTarget) -> bool:
        mtimes = []
        for path in self._partial_paths(target):
            try:
                mtimes.append(os.path.getmtime(path))
            except FileNotFoundError:
                continue  # never created, or removed by a concurrent download
        expire_time = time.time() - self.DOWNLOAD_CACHE_EXPIRE
        return bool(mtimes) and max(mtimes) < expire_time

    def download(
        self,
        url: str,
        artifact: Optional[TrustedArtifact] = None,
        resume_partial: bool = True,
    ) -> str:
        """``resume_partial=False`` discards any partial data and starts clean."""
        if artifact is not None and not isinstance(artifact, TrustedArtifact):
            raise TypeError(
                "download() expects a TrustedArtifact(sha256, size), got %r"
                % type(artifact).__name__
            )
        target = self._resolve_download_target(url, artifact)
        if not os.path.isfile(target.cache_path):
            with LockFile(target.cache_path):
                # another process may have completed it while we waited
                if not os.path.isfile(target.cache_path):
                    self._download_to_cache(url, artifact, target, resume_partial)
        self.set_download_utime(target.cache_path)
        return target.cache_path

    def _resolve_download_target(
        self, url: str, artifact: Optional[TrustedArtifact]
    ) -> DownloadTarget:
        if artifact:
            return self._make_download_target(MODE_TRUSTED, artifact.sha256)
        key = os.path.basename(self.compute_download_path(url, ""))
        return self._make_download_target(MODE_EXTERNAL, key)

    def _make_download_target(self, mode: str, key: str) -> DownloadTarget:
        base_path = os.path.join(self.get_partial_download_dir(), key)
        return DownloadTarget(
            mode=mode,
            key=key,
            cache_path=os.path.join(self.get_download_dir(), key),
            partial_path=base_path + ".part",
            state_path=base_path + ".json",
        )

    def _download_to_cache(
        self,
        url: str,
        artifact: Optional[TrustedArtifact],
        target: DownloadTarget,
        resume_partial: bool,
    ) -> None:
        state = None
        if resume_partial:
            state = self._load_partial_state(url, artifact, target)
        else:
            self._discard_partial(target)
        downloader = FileDownloader(url)
        info: Optional[ResponseInfo] = None
        sha256 = hashlib.sha256()
        try:
            with downloader.open(
                target.partial_path,
                self._make_resume_point(state, artifact, target),
                expected_size=artifact.size if artifact else None,
                caller_verifies=artifact is not None,
            ) as info:
                self._persist_partial_state(url, artifact, target, state, info)
                if artifact and info.offset:
                    # hash the kept bytes once; new bytes are hashed in flight
                    self._hash_file_prefix(
                        sha256.update, target.partial_path, info.offset
                    )
                downloader.receive(
                    with_progress=not app.is_disabled_progressbar(),
                    silent=not self.log.isEnabledFor(logging.INFO),
                    on_chunk=sha256.update if artifact else None,
                )
        except DownloadError as exc:
            # keep valid partial data for a caller-driven retry; a response
            # rejected after the partial was opened may have modified it
            if info is not None and (
                not info.resumable or isinstance(exc, ResponseValidationError)
            ):
                self._discard_partial(target)
            raise
        if artifact:
            self._verify_artifact(
                artifact, target, sha256.hexdigest(), resumed=info.offset > 0
            )
        os.replace(target.partial_path, target.cache_path)
        self._discard_partial(target)

    def _load_partial_state(
        self, url: str, artifact: Optional[TrustedArtifact], target: DownloadTarget
    ) -> Optional[PartialState]:
        if not os.path.isfile(target.partial_path):
            self._discard_partial(target)
            return None
        size = os.path.getsize(target.partial_path)
        state = PartialState.load(target.state_path)
        if (
            state is None
            or size == 0
            or state.mode != target.mode
            or state.key != target.key
        ):
            self._discard_partial(target)
            return None
        known_total = self._known_total_size(artifact, state)
        reusable = (
            (known_total is None or size <= known_total)
            and all(s.start <= size for s in state.segments)
            and (artifact is not None or (state.url == url and state.validator()))
        )
        if not reusable:
            self._discard_partial(target)
            return None
        return state

    def _make_resume_point(
        self,
        state: Optional[PartialState],
        artifact: Optional[TrustedArtifact],
        target: DownloadTarget,
    ) -> Optional[ResumePoint]:
        if state is None:
            return None
        offset = os.path.getsize(target.partial_path)
        if artifact:
            # authorized by the trusted SHA256: never send a mirror's validator
            total = self._known_total_size(artifact, state)
            return ResumePoint(offset, None, total, None)
        return ResumePoint(
            offset, state.validator(), state.total_size, state.effective_url
        )

    @staticmethod
    def _known_total_size(
        artifact: Optional[TrustedArtifact], state: PartialState
    ) -> Optional[int]:
        if artifact and artifact.size is not None:
            return artifact.size
        return state.total_size

    @staticmethod
    def _persist_partial_state(
        url: str,
        artifact: Optional[TrustedArtifact],
        target: DownloadTarget,
        state: Optional[PartialState],
        info: ResponseInfo,
    ) -> None:
        # written before the body, so the partial never outgrows its state
        if not info.resumable:
            if os.path.isfile(target.state_path):
                os.remove(target.state_path)
            return
        if state is None or info.offset == 0:
            state = PartialState(
                mode=target.mode,
                key=target.key,
                url=url,
                effective_url=info.effective_url,
                sha256=artifact.sha256 if artifact else None,
                expected_size=artifact.size if artifact else None,
            )
        state.url = url
        state.effective_url = info.effective_url
        state.total_size = info.total_size
        if info.offset == 0 or info.etag or info.last_modified:
            # a 206 may omit validators; keep the matching ones
            state.etag, state.last_modified = info.etag, info.last_modified
        state.updated = time.time()
        if not info.complete:
            state.segments.append(Segment(info.offset, url, info.effective_url))
        state.save(target.state_path)

    @staticmethod
    def _hash_file_prefix(
        update: Callable[[bytes], None], path: str, size: int
    ) -> None:
        with open(path, "rb") as fp:
            while size > 0:
                chunk = fp.read(min(size, 1024 * 1024))
                if not chunk:
                    break
                update(chunk)
                size -= len(chunk)

    def _verify_artifact(
        self,
        artifact: TrustedArtifact,
        target: DownloadTarget,
        sha256: str,
        resumed: bool,
    ) -> None:
        size = os.path.getsize(target.partial_path)
        if artifact.size is not None and size != artifact.size:
            self._discard_partial(target)
            raise ArtifactVerificationError(
                "The size (%d bytes) of the downloaded file does not match "
                "the expected size (%d bytes)" % (size, artifact.size),
                resumed=resumed,
            )
        if sha256 != artifact.sha256:
            self._discard_partial(target)
            raise ArtifactVerificationError(
                "The SHA256 checksum '%s' of the downloaded file does not match "
                "the expected '%s'" % (sha256, artifact.sha256),
                resumed=resumed,
            )

    @staticmethod
    def _partial_paths(target: DownloadTarget) -> tuple[str, str, str]:
        return target.partial_path, target.state_path, target.state_path + ".tmp"

    @staticmethod
    def _discard_partial(target: DownloadTarget) -> None:
        for path in PackageManagerDownloadMixin._partial_paths(target):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

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

"""Resumable HTTP transfer of a single file.

The downloader knows nothing about artifact identity or checksums. It sends
the request, validates the response headers, decides whether the response may
be appended to the partial file, and streams the body. See
``agent-docs/specs/resumable-downloads.md``.
"""

import re
from contextlib import contextmanager
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import BinaryIO, Callable, Iterator, Optional

import click
import requests
from urllib3.exceptions import HTTPError as Urllib3HTTPError

from platformio.compat import is_terminal
from platformio.http import HTTPSession
from platformio.package.exception import PackageException

DEFAULT_TIMEOUT = (15, 60)  # (connect, read inactivity) in seconds
MAX_REDIRECTS = 10
CHUNK_SIZE = 64 * 1024

_CONTENT_RANGE_RE = re.compile(r"^bytes (\d+)-(\d+)/(\d+)$")
_UNSATISFIED_RANGE_RE = re.compile(r"^bytes \*/(\d+)$")
_STRONG_ETAG_RE = re.compile(r'^"[^"]*"$')


class DownloadError(PackageException):
    pass


class TransferInterruptedError(DownloadError):
    """Recoverable: the partial file holds valid data for a later attempt."""


class ResponseValidationError(DownloadError):
    """The response is unusable; a partial is modified only after validation."""


class ArtifactVerificationError(DownloadError):
    """The complete file does not match the trusted size or SHA256."""

    def __init__(self, message: str, resumed: bool = False) -> None:
        super().__init__(message)
        self.resumed = resumed  # the file contained data from an earlier attempt


@dataclass(frozen=True)
class ResumePoint:
    offset: int  # bytes already in the partial (> 0)
    if_range: Optional[str]  # validator to send; always None in trusted mode
    total_size: Optional[int]  # expected or previously known total
    effective_url: Optional[str]  # a 206 from another URL is not appended


@dataclass(frozen=True)
class ResponseInfo:  # pylint: disable=too-many-instance-attributes
    status: int  # 200, 203, 206 or 416
    effective_url: str
    offset: int  # 0 = partial truncated; > 0 = appending
    total_size: Optional[int]
    etag: Optional[str]  # strong ETags only
    last_modified: Optional[str]  # only if strong per RFC 9110 8.8.2.2
    resumable: bool
    complete: bool  # True for an accepted 416 (no body)


def parse_content_range(value: Optional[str]) -> Optional[tuple[int, int, int]]:
    match = _CONTENT_RANGE_RE.match((value or "").strip())
    if not match:
        return None
    start, end, total = (int(group) for group in match.groups())
    if start > end or end >= total:
        return None
    return start, end, total


def strong_etag(value: Optional[str]) -> Optional[str]:
    if value and _STRONG_ETAG_RE.match(value.strip()):
        return value.strip()
    return None


def strong_last_modified(
    last_modified: Optional[str], date: Optional[str]
) -> Optional[str]:
    # RFC 9110 8.8.2.2: strong only if at least one second older than Date
    if not last_modified or not date:
        return None
    try:
        delta = parsedate_to_datetime(date) - parsedate_to_datetime(last_modified)
    except (TypeError, ValueError, IndexError):
        return None
    return last_modified if delta.total_seconds() >= 1 else None


def _is_identity(response: requests.Response) -> bool:
    encoding = response.headers.get("Content-Encoding", "").strip().lower()
    return encoding in ("", "identity")


def _content_length(response: requests.Response) -> Optional[int]:
    value = response.headers.get("Content-Length")
    if value is None:
        return None
    value = value.strip()
    if not (value.isascii() and value.isdigit()):
        raise ResponseValidationError(
            "Invalid Content-Length '%s' for %s" % (value, response.url)
        )
    return int(value)


def _sizes_conflict(total: int, *known: Optional[int]) -> bool:
    return any(size is not None and size != total for size in known)


class FileDownloader:
    def __init__(
        self, url: str, timeout: tuple[float, float] = DEFAULT_TIMEOUT
    ) -> None:
        self.url = url
        self.timeout = timeout
        self._session: Optional[HTTPSession] = None
        self._response: Optional[requests.Response] = None
        self._info: Optional[ResponseInfo] = None
        self._fp: Optional[BinaryIO] = None
        self._body_size: Optional[int] = None  # declared length of the body

    @contextmanager
    def open(
        self,
        partial_path: str,
        resume: Optional[ResumePoint] = None,
        *,
        expected_size: Optional[int] = None,
        caller_verifies: bool = False,
    ) -> Iterator[ResponseInfo]:
        """Send the request and validate the response headers.

        ``caller_verifies`` means the caller checks the complete file against
        a trusted SHA256, so the partial is resumable without HTTP validators.
        """
        self._session = HTTPSession()
        self._session.max_redirects = MAX_REDIRECTS
        try:
            info = self._request(resume, expected_size, caller_verifies)
            if not info.complete:
                self._fp = self._open_partial(partial_path, info.offset)
            self._info = info
            yield info
        finally:
            self._close()

    def receive(
        self,
        with_progress: bool = True,
        silent: bool = False,
        on_chunk: Optional[Callable[[bytes], None]] = None,
    ) -> None:
        """Stream the body into the partial file.

        ``on_chunk`` is called with every chunk appended to the partial, e.g.
        to hash the content without reading the file back.
        """
        assert self._info, "call receive() inside open()"
        if self._info.complete:
            return
        self._write_body(self._iter_body(on_chunk), with_progress, silent)
        assert self._fp
        size = self._fp.tell()
        if self._info.total_size is not None and size != self._info.total_size:
            raise ResponseValidationError(
                "Downloaded %d bytes of %s, expected %d"
                % (size, self.url, self._info.total_size)
            )

    #
    # Request phase
    #

    def _request(
        self,
        resume: Optional[ResumePoint],
        expected_size: Optional[int],
        caller_verifies: bool,
    ) -> ResponseInfo:
        # without a trusted checksum, appending requires an HTTP validator
        if resume and (caller_verifies or resume.if_range):
            headers = {"Range": "bytes=%d-" % resume.offset}
            if resume.if_range:
                headers["If-Range"] = resume.if_range
            response = self._send(headers)
            info = self._check_range_response(
                response, resume, expected_size, caller_verifies
            )
            if info:
                return info
            # a single clean full-request fallback
            response.close()
        response = self._send({})
        return self._check_full_response(response, expected_size, caller_verifies)

    def _send(self, headers: dict[str, str]) -> requests.Response:
        assert self._session
        try:
            self._response = self._session.get(
                self.url,
                headers={"Accept-Encoding": "identity", **headers},
                stream=True,
                timeout=self.timeout,
            )
        except requests.TooManyRedirects as exc:
            raise ResponseValidationError(
                "Too many redirects for %s" % self.url
            ) from exc
        except requests.RequestException as exc:
            raise TransferInterruptedError(
                "Could not download %s: %s" % (self.url, exc)
            ) from exc
        return self._response

    def _check_range_response(
        self,
        response: requests.Response,
        resume: ResumePoint,
        expected_size: Optional[int],
        caller_verifies: bool,
    ) -> Optional[ResponseInfo]:
        if response.status_code in (200, 203):
            # the server ignored the range or the validator failed
            return self._check_full_response(response, expected_size, caller_verifies)
        if response.status_code == 206:
            return self._check_partial_content(response, resume, expected_size)
        if response.status_code == 416 and caller_verifies:
            return self._check_unsatisfiable(response, resume, expected_size)
        if response.status_code == 416:
            return None
        raise self._status_error(response)

    def _check_full_response(
        self,
        response: requests.Response,
        expected_size: Optional[int],
        caller_verifies: bool,
    ) -> ResponseInfo:
        if response.status_code not in (200, 203):
            raise self._status_error(response)
        identity = _is_identity(response)
        length = _content_length(response) if identity else None
        if length is not None and _sizes_conflict(length, expected_size):
            raise ResponseValidationError(
                "The size (%d bytes) of %s does not match the expected size "
                "(%d bytes)" % (length, response.url, expected_size)
            )
        self._body_size = length
        etag = strong_etag(response.headers.get("ETag"))
        last_modified = strong_last_modified(
            response.headers.get("Last-Modified"), response.headers.get("Date")
        )
        resumable = (
            response.status_code == 200
            and length is not None
            and (caller_verifies or bool(etag or last_modified))
        )
        return ResponseInfo(
            status=response.status_code,
            effective_url=response.url,
            offset=0,
            total_size=length,
            etag=etag,
            last_modified=last_modified,
            resumable=resumable,
            complete=False,
        )

    def _check_partial_content(
        self,
        response: requests.Response,
        resume: ResumePoint,
        expected_size: Optional[int],
    ) -> Optional[ResponseInfo]:
        content_range = parse_content_range(response.headers.get("Content-Range"))
        etag = strong_etag(response.headers.get("ETag"))
        if (
            not content_range
            or not _is_identity(response)
            or response.headers.get("Content-Type", "").lower().startswith("multipart/")
            or self._is_other_resource(response.url, etag, resume)
        ):
            return None
        start, end, total = content_range
        length = end - start + 1
        try:
            content_length = _content_length(response)
        except ResponseValidationError:
            return None  # malformed: use the clean full-request fallback
        if (
            start != resume.offset
            or end != total - 1
            or _sizes_conflict(total, expected_size, resume.total_size)
            or _sizes_conflict(length, content_length)
        ):
            return None
        self._body_size = length
        return ResponseInfo(
            status=206,
            effective_url=response.url,
            offset=start,
            total_size=total,
            etag=etag,
            last_modified=strong_last_modified(
                response.headers.get("Last-Modified"), response.headers.get("Date")
            ),
            resumable=True,
            complete=False,
        )

    @staticmethod
    def _is_other_resource(
        effective_url: str, etag: Optional[str], resume: ResumePoint
    ) -> bool:
        if resume.effective_url and effective_url != resume.effective_url:
            return True
        sent_etag = strong_etag(resume.if_range)
        return bool(etag and sent_etag and etag != sent_etag)

    @staticmethod
    def _check_unsatisfiable(
        response: requests.Response,
        resume: ResumePoint,
        expected_size: Optional[int],
    ) -> Optional[ResponseInfo]:
        # accepted only when the partial is exactly the known complete size;
        # the caller still verifies the trusted SHA256
        match = _UNSATISFIED_RANGE_RE.match(
            response.headers.get("Content-Range", "").strip()
        )
        known = [s for s in (expected_size, resume.total_size) if s is not None]
        if not match or not known:
            return None
        total = int(match.group(1))
        if total != resume.offset or _sizes_conflict(total, *known):
            return None
        return ResponseInfo(
            status=416,
            effective_url=response.url,
            offset=resume.offset,
            total_size=total,
            etag=None,
            last_modified=None,
            resumable=True,
            complete=True,
        )

    @staticmethod
    def _status_error(response: requests.Response) -> ResponseValidationError:
        return ResponseValidationError(
            "Got the unrecognized status code '%d' when downloaded %s"
            % (response.status_code, response.url)
        )

    #
    # Transfer phase
    #

    @staticmethod
    def _open_partial(path: str, offset: int) -> BinaryIO:
        # truncate before the caller persists new state for this response
        fp = open(  # pylint: disable=consider-using-with
            path, "r+b" if offset else "wb"
        )
        fp.seek(offset)
        fp.truncate()
        return fp

    def _iter_body(
        self, on_chunk: Optional[Callable[[bytes], None]]
    ) -> Iterator[bytes]:
        assert self._response
        identity = _is_identity(self._response)
        received = 0
        try:
            for chunk in self._response.raw.stream(
                CHUNK_SIZE, decode_content=not identity
            ):
                received += len(chunk)
                if self._body_size is not None and received > self._body_size:
                    raise ResponseValidationError(
                        "The response body of %s exceeds the declared %d bytes"
                        % (self.url, self._body_size)
                    )
                if on_chunk:
                    on_chunk(chunk)
                yield chunk
        except (Urllib3HTTPError, requests.RequestException) as exc:
            raise TransferInterruptedError(
                "Download of %s was interrupted: %s" % (self.url, exc)
            ) from exc
        if self._body_size is not None and received < self._body_size:
            raise TransferInterruptedError(
                "Download of %s was interrupted after %d of %d bytes"
                % (self.url, received, self._body_size)
            )

    def _write_body(
        self, chunks: Iterator[bytes], with_progress: bool, silent: bool
    ) -> None:
        assert self._info and self._fp
        fp = self._fp
        offset, total = self._info.offset, self._info.total_size
        label = "Resuming download" if offset else "Downloading"
        if not total or not with_progress or silent:
            if not silent:
                click.echo(f"{label}...")
            for chunk in chunks:
                fp.write(chunk)
        elif not is_terminal():
            self._write_with_percents(chunks, label, offset, total)
        else:
            with click.progressbar(
                length=total,
                label=label,
                update_min_steps=min(256 * 1024, total / 100),  # every 256Kb or less
            ) as pb:
                pb.update(offset)
                for chunk in chunks:
                    fp.write(chunk)
                    pb.update(len(chunk))

    def _write_with_percents(
        self, chunks: Iterator[bytes], label: str, offset: int, total: int
    ) -> None:
        assert self._fp
        step = 10
        printed = offset * 100 // total // step * step
        click.echo(f"{label} {printed}%", nl=False)
        downloaded = offset
        for chunk in chunks:
            self._fp.write(chunk)
            downloaded += len(chunk)
            while downloaded * 100 / total >= printed + step:
                printed += step
                click.echo(f" {printed}%", nl=False)
        click.echo("")

    def _close(self) -> None:
        if self._fp:
            self._fp.close()
            self._fp = None
        if self._response is not None:
            self._response.close()
            self._response = None
        if self._session:
            self._session.close()
            self._session = None

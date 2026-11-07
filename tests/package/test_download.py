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

# pylint: disable=redefined-outer-name

import os
import time
from pathlib import Path
from typing import Optional

import pytest

from platformio.package.download import (
    FileDownloader,
    ResponseInfo,
    ResponseValidationError,
    ResumePoint,
    TransferInterruptedError,
    parse_content_range,
    strong_etag,
    strong_last_modified,
)

from .conftest import Reply, Request, Resource, TestServer, http_date, redirect

DATA = bytes(range(256)) * 400  # 102400 bytes
ETAG = '"v1"'


def download(  # pylint: disable=too-many-arguments
    url: str,
    path: Path,
    resume: Optional[ResumePoint] = None,
    *,
    expected_size: Optional[int] = None,
    caller_verifies: bool = False,
    timeout: tuple[float, float] = (5, 5),
) -> ResponseInfo:
    downloader = FileDownloader(url, timeout=timeout)
    with downloader.open(
        str(path), resume, expected_size=expected_size, caller_verifies=caller_verifies
    ) as info:
        downloader.receive(with_progress=False, silent=True)
    return info


def write_partial(path: Path, size: int, data: bytes = DATA) -> None:
    path.write_bytes(data[:size])


#
# Header helpers
#


def test_parse_content_range() -> None:
    assert parse_content_range("bytes 10-99/100") == (10, 99, 100)
    assert parse_content_range(" bytes 0-0/1 ") == (0, 0, 1)
    for value in (
        None,
        "",
        "bytes 10-99/*",
        "bytes */100",
        "bytes 10-99/100, 0-1/100",
        "items 0-1/2",
        "bytes 99-10/100",
        "bytes 0-100/100",
    ):
        assert parse_content_range(value) is None, value


def test_strong_etag() -> None:
    assert strong_etag('"abc"') == '"abc"'
    assert strong_etag('W/"abc"') is None
    assert strong_etag("abc") is None
    assert strong_etag(None) is None


def test_strong_last_modified() -> None:
    now = time.time()
    lm = http_date(now - 10)
    assert strong_last_modified(lm, http_date(now)) == lm
    # RFC 9110 8.8.2.2: needs a Date at least one second later
    assert strong_last_modified(lm, None) is None
    assert strong_last_modified(lm, lm) is None
    assert strong_last_modified("garbage", http_date(now)) is None
    assert strong_last_modified(None, http_date(now)) is None


#
# Lazy connection and full downloads
#


def test_no_network_before_open(http_server: TestServer) -> None:
    http_server.routes["/f"] = Resource(DATA)
    FileDownloader(http_server.url("/f"))
    assert not http_server.requests


def test_full_download(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    info = download(http_server.url("/f"), path)
    assert path.read_bytes() == DATA
    assert info.status == 200 and info.offset == 0
    assert info.total_size == len(DATA)
    assert info.etag == ETAG and info.resumable
    (request,) = http_server.requests
    assert request.headers["Accept-Encoding"] == "identity"
    assert "Range" not in request.headers


def test_validators(
    http_server: TestServer, tmp_path: Path, strong_dates: tuple[str, str]
) -> None:
    path = tmp_path / "f.part"
    http_server.routes["/weak"] = Resource(DATA, etag='W/"v1"')
    info = download(http_server.url("/weak"), path)
    assert info.etag is None and not info.resumable
    # a resumable partial for a trusted artifact needs no HTTP validator
    info = download(http_server.url("/weak"), path, caller_verifies=True)
    assert info.resumable
    lm, date = strong_dates
    http_server.routes["/lm"] = Resource(DATA, last_modified=lm, date=date)
    info = download(http_server.url("/lm"), path)
    assert info.last_modified == lm and info.resumable
    http_server.routes["/weak-lm"] = Resource(DATA, last_modified=lm, date=lm)
    info = download(http_server.url("/weak-lm"), path)
    assert info.last_modified is None and not info.resumable


def test_unknown_length_is_not_resumable(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG, send_length=False)
    path = tmp_path / "f.part"
    info = download(http_server.url("/f"), path, caller_verifies=True)
    assert path.read_bytes() == DATA
    assert info.total_size is None and not info.resumable


def test_non_authoritative_is_not_resumable(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = lambda _: Reply(
        203, {"ETag": ETAG, "Content-Length": str(len(DATA))}, DATA
    )
    path = tmp_path / "f.part"
    info = download(http_server.url("/f"), path, caller_verifies=True)
    assert path.read_bytes() == DATA
    assert info.status == 203 and not info.resumable


def test_unexpected_status(http_server: TestServer, tmp_path: Path) -> None:
    path = tmp_path / "f.part"
    with pytest.raises(ResponseValidationError):
        download(http_server.url("/missing"), path)


def test_expected_size_conflict_keeps_partial(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = Resource(DATA, accept_ranges=False)
    path = tmp_path / "f.part"
    write_partial(path, 1000)
    with pytest.raises(ResponseValidationError):
        download(
            http_server.url("/f"),
            path,
            ResumePoint(1000, None, len(DATA) + 1, None),
            expected_size=len(DATA) + 1,
            caller_verifies=True,
        )
    assert path.read_bytes() == DATA[:1000]


#
# Interruptions
#


def test_truncated_body(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG, cuts=[30000])
    path = tmp_path / "f.part"
    with pytest.raises(TransferInterruptedError):
        download(http_server.url("/f"), path)
    assert path.read_bytes() == DATA[:30000]


def test_read_timeout(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG, stall=1.5)
    path = tmp_path / "f.part"
    with pytest.raises(TransferInterruptedError):
        download(http_server.url("/f"), path, timeout=(5, 0.3))


def test_body_longer_than_declared(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = lambda _: Reply(
        200, {"Content-Length": "100"}, DATA[:200]
    )
    path = tmp_path / "f.part"
    # urllib3 stops at Content-Length; the extra bytes are never appended
    download(http_server.url("/f"), path)
    assert path.read_bytes() == DATA[:100]


def test_partial_body_longer_than_range(
    http_server: TestServer, tmp_path: Path
) -> None:
    # a close-delimited 206 must not write past its declared range
    http_server.routes["/f"] = lambda _: Reply(
        206,
        {"Content-Range": f"bytes 40000-{len(DATA) - 1}/{len(DATA)}"},
        DATA[40000:] + b"x" * 100000,
    )
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    with pytest.raises(ResponseValidationError, match="exceeds"):
        download(
            http_server.url("/f"),
            path,
            ResumePoint(40000, None, len(DATA), None),
            caller_verifies=True,
        )
    size = path.stat().st_size
    assert size <= len(DATA) and path.read_bytes() == DATA[:size]


#
# Range requests
#


def test_resume_requires_validator_or_caller_verification(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = Resource(DATA)
    path = tmp_path / "f.part"
    path.write_bytes(b"x" * 40000)
    info = download(
        http_server.url("/f"), path, ResumePoint(40000, None, len(DATA), None)
    )
    assert path.read_bytes() == DATA and info.offset == 0
    (request,) = http_server.requests
    assert "Range" not in request.headers


def test_resume_with_etag(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    info = download(
        http_server.url("/f"), path, ResumePoint(40000, ETAG, len(DATA), None)
    )
    assert path.read_bytes() == DATA
    assert info.status == 206 and info.offset == 40000 and info.resumable
    (request,) = http_server.requests
    assert request.headers["Range"] == "bytes=40000-"
    assert request.headers["If-Range"] == ETAG


def test_on_chunk_sees_exactly_the_written_bytes(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    seen: list[bytes] = []
    downloader = FileDownloader(http_server.url("/f"))
    with downloader.open(str(path), ResumePoint(40000, ETAG, len(DATA), None)):
        downloader.receive(with_progress=False, silent=True, on_chunk=seen.append)
    assert b"".join(seen) == DATA[40000:]


def test_resume_without_if_range(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    info = download(
        http_server.url("/f"),
        path,
        ResumePoint(40000, None, len(DATA), None),
        expected_size=len(DATA),
        caller_verifies=True,
    )
    assert path.read_bytes() == DATA and info.resumable
    (request,) = http_server.requests
    assert "If-Range" not in request.headers


def test_ignored_range_truncates(http_server: TestServer, tmp_path: Path) -> None:
    http_server.routes["/f"] = Resource(DATA, etag='"v2"')  # validator changed
    path = tmp_path / "f.part"
    path.write_bytes(b"x" * 500)
    info = download(http_server.url("/f"), path, ResumePoint(500, ETAG, None, None))
    assert path.read_bytes() == DATA
    assert info.status == 200 and info.offset == 0 and info.etag == '"v2"'
    assert len(http_server.requests) == 1


def _malformed_206(headers: dict[str, str], body: bytes = DATA[40000:]):
    def route(request: Request) -> Reply:
        if "Range" not in request.headers:
            return Resource(DATA, etag=ETAG)(request)
        base = {
            "ETag": ETAG,
            "Content-Range": f"bytes 40000-{len(DATA) - 1}/{len(DATA)}",
            "Content-Length": str(len(body)),
        }
        base.update(headers)
        return Reply(206, {k: v for k, v in base.items() if v is not None}, body)

    return route


@pytest.mark.parametrize(
    "headers",
    [
        {"Content-Range": None},
        {"Content-Range": f"bytes 39999-{len(DATA) - 1}/{len(DATA)}"},
        {"Content-Range": f"bytes 40000-{len(DATA) - 1}/{len(DATA) + 1}"},
        {"Content-Range": f"bytes 40000-50000/{len(DATA)}"},
        {"Content-Range": "bytes 40000-*/*"},
        {"Content-Length": "10"},
        {"Content-Length": "12, 12"},
        {"Content-Encoding": "gzip"},
        {"Content-Type": "multipart/byteranges; boundary=x"},
        {"ETag": '"other"'},
    ],
    ids=[
        "no-range",
        "wrong-start",
        "wrong-total",
        "short-end",
        "unknown-total",
        "wrong-length",
        "invalid-length",
        "encoded",
        "multipart",
        "other-etag",
    ],
)
def test_malformed_partial_content_falls_back_once(
    http_server: TestServer, tmp_path: Path, headers: dict[str, str]
) -> None:
    http_server.routes["/f"] = _malformed_206(headers)
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    info = download(
        http_server.url("/f"), path, ResumePoint(40000, ETAG, len(DATA), None)
    )
    assert path.read_bytes() == DATA
    assert info.status == 200 and info.offset == 0
    first, second = http_server.requests
    assert "Range" in first.headers
    assert "Range" not in second.headers and "If-Range" not in second.headers


def test_failed_fallback_keeps_partial(http_server: TestServer, tmp_path: Path) -> None:
    def route(request: Request) -> Reply:
        if "Range" in request.headers:
            return _malformed_206({"Content-Range": None})(request)
        return Reply(503, {"Content-Length": "0"})

    http_server.routes["/f"] = route
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    with pytest.raises(ResponseValidationError):
        download(http_server.url("/f"), path, ResumePoint(40000, ETAG, len(DATA), None))
    assert path.read_bytes() == DATA[:40000]
    assert len(http_server.requests) == 2


def test_resume_redirect_target_changed(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = redirect("/b")
    http_server.routes["/b"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    write_partial(path, 40000)
    info = download(
        http_server.url("/f"),
        path,
        ResumePoint(40000, ETAG, len(DATA), http_server.url("/a")),
    )
    assert path.read_bytes() == DATA
    assert info.status == 200 and info.effective_url == http_server.url("/b")
    assert "Range" not in http_server.requests[-1].headers


def test_resume_progress_is_cumulative(
    http_server: TestServer, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    write_partial(path, len(DATA) // 2)
    downloader = FileDownloader(http_server.url("/f"))
    with downloader.open(str(path), ResumePoint(len(DATA) // 2, ETAG, None, None)):
        downloader.receive(with_progress=True, silent=False)
    output = capsys.readouterr().out
    assert output.startswith("Resuming download 50%")
    assert " 40%" not in output and output.rstrip().endswith("100%")


#
# 416 Range Not Satisfiable
#


def test_unsatisfiable_range_accepted_when_verified(
    http_server: TestServer, tmp_path: Path
) -> None:
    http_server.routes["/f"] = Resource(DATA)
    path = tmp_path / "f.part"
    write_partial(path, len(DATA))
    info = download(
        http_server.url("/f"),
        path,
        ResumePoint(len(DATA), None, len(DATA), None),
        expected_size=len(DATA),
        caller_verifies=True,
    )
    assert info.status == 416 and info.complete
    assert path.read_bytes() == DATA
    assert len(http_server.requests) == 1


@pytest.mark.parametrize(
    "caller_verifies,known_total",
    [(False, len(DATA)), (True, None), (True, len(DATA) + 1)],
    ids=["external", "unknown-total", "total-mismatch"],
)
def test_unsatisfiable_range_falls_back(
    http_server: TestServer,
    tmp_path: Path,
    caller_verifies: bool,
    known_total: Optional[int],
) -> None:
    http_server.routes["/f"] = Resource(DATA, etag=ETAG)
    path = tmp_path / "f.part"
    write_partial(path, len(DATA))
    info = download(
        http_server.url("/f"),
        path,
        ResumePoint(len(DATA), None if caller_verifies else ETAG, known_total, None),
        caller_verifies=caller_verifies,
    )
    assert info.status == 200 and path.read_bytes() == DATA
    assert len(http_server.requests) == 2


def test_partial_file_is_not_created_on_rejection(
    http_server: TestServer, tmp_path: Path
) -> None:
    path = tmp_path / "f.part"
    with pytest.raises(ResponseValidationError):
        download(http_server.url("/missing"), path)
    assert not os.path.exists(path)

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

import re
import threading
import time
from dataclasses import dataclass, field
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Iterator, Optional

import pytest

# A deterministic local HTTP server for download tests. Each path maps to a
# route that receives the recorded request and returns a scripted reply.


@dataclass(frozen=True)
class Request:
    path: str
    headers: dict[str, str]


@dataclass
class Reply:
    status: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    cut_after: Optional[int] = None  # close the connection after N body bytes
    stall: float = 0  # sleep before sending the body


Route = Callable[[Request], Reply]


def http_date(timestamp: float) -> str:
    return formatdate(timestamp, usegmt=True)


@dataclass
class Resource:  # pylint: disable=too-many-instance-attributes
    """A static file with RFC 9110 Range / If-Range semantics."""

    data: bytes
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    date: Optional[str] = None
    accept_ranges: bool = True
    send_length: bool = True
    cuts: list[Optional[int]] = field(default_factory=list)  # one per request
    stall: float = 0

    def __call__(self, request: Request) -> Reply:
        headers = {"Content-Type": "application/octet-stream"}
        for name, value in (
            ("ETag", self.etag),
            ("Last-Modified", self.last_modified),
            ("Date", self.date),
        ):
            if value:
                headers[name] = value
        cut_after = self.cuts.pop(0) if self.cuts else None
        offset = self._range_offset(request)
        if offset is None:
            return self._reply(200, headers, self.data, cut_after)
        size = len(self.data)
        if offset >= size:
            headers["Content-Range"] = f"bytes */{size}"
            return Reply(416, headers)
        headers["Content-Range"] = f"bytes {offset}-{size - 1}/{size}"
        return self._reply(206, headers, self.data[offset:], cut_after)

    def _range_offset(self, request: Request) -> Optional[int]:
        match = re.match(r"^bytes=(\d+)-$", request.headers.get("Range", ""))
        if not self.accept_ranges or not match:
            return None
        if_range = request.headers.get("If-Range")
        if if_range and if_range not in (self.etag, self.last_modified):
            return None
        return int(match.group(1))

    def _reply(
        self,
        status: int,
        headers: dict[str, str],
        body: bytes,
        cut_after: Optional[int],
    ) -> Reply:
        if self.send_length:
            headers["Content-Length"] = str(len(body))
        return Reply(status, headers, body, cut_after, self.stall)


def redirect(location: str, status: int = 302) -> Route:
    return lambda _: Reply(status, {"Location": location, "Content-Length": "0"})


class TestServer:
    __test__ = False  # not a pytest test class

    def __init__(self) -> None:
        self.routes: dict[str, Route] = {}
        self.requests: list[Request] = []
        self._lock = threading.Lock()
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._make_handler())
        self._httpd.daemon_threads = True
        self._thread = threading.Thread(
            target=self._httpd.serve_forever, kwargs={"poll_interval": 0.05}
        )

    @property
    def base_url(self) -> str:
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    def url(self, path: str) -> str:
        return self.base_url + path

    def requests_for(self, path: str) -> list[Request]:
        with self._lock:
            return [r for r in self.requests if r.path == path]

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join()

    def _record(self, request: Request) -> Reply:
        with self._lock:
            self.requests.append(request)
            route = self.routes.get(request.path)
        if not route:
            return Reply(404, {"Content-Length": "0"})
        return route(request)

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # pylint: disable=invalid-name
                reply = server._record(  # pylint: disable=protected-access
                    Request(self.path, dict(self.headers.items()))
                )
                try:
                    self._send(reply)
                except OSError:
                    pass  # the client went away (timeouts, interruptions)

            def _send(self, reply: Reply) -> None:
                self.send_response_only(reply.status)
                for name, value in reply.headers.items():
                    self.send_header(name, value)
                self.end_headers()
                if reply.stall:
                    self.wfile.flush()
                    time.sleep(reply.stall)
                body = reply.body
                if reply.cut_after is not None:
                    body = body[: reply.cut_after]
                self.wfile.write(body)
                self.wfile.flush()
                self.close_connection = True

            def log_message(self, *args) -> None:  # pylint: disable=arguments-differ
                pass

        return Handler


def _start_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestServer]:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    server = TestServer()
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def http_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestServer]:
    yield from _start_server(monkeypatch)


@pytest.fixture
def mirror_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestServer]:
    """A second server on a different host:port, used as another mirror."""
    yield from _start_server(monkeypatch)


@pytest.fixture
def strong_dates() -> tuple[str, str]:
    """A (Last-Modified, Date) pair where Last-Modified is a strong validator."""
    now = time.time()
    return http_date(now - 3600), http_date(now)

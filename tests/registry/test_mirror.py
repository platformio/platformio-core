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

import json
from typing import Any

import pytest

from platformio.cache import ContentCache
from platformio.registry import mirror
from platformio.registry.mirror import RegistryFileMirrorIterator


class _FakeContentCache:
    """In memory stand in for ContentCache used by the iterator tests."""

    _store: dict[str, str] = {}

    def __init__(self, _namespace: str | None = None) -> None:
        pass

    def __enter__(self) -> "_FakeContentCache":
        return self

    def __exit__(self, *_exc: Any) -> bool:
        return False

    def get(self, key: str) -> str | None:
        return type(self)._store.get(key)

    def set(self, key: str, data: str, _valid: str) -> None:
        type(self)._store[key] = data

    @staticmethod
    def key_from_args(*args: Any) -> str:
        return ContentCache.key_from_args(*args)


class _FakeResponse:
    def __init__(self, status_code: int, headers: dict[str, str]) -> None:
        self.status_code = status_code
        self.headers = headers


class _FakeHTTPClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = list(responses)
        self.requests: list[tuple[str, str, dict[str, Any]]] = []

    def send_request(self, method: str, path: str, **kwargs: Any) -> _FakeResponse:
        self.requests.append((method, path, kwargs))
        return self._responses.pop(0)


@pytest.fixture
def fake_cache(monkeypatch: pytest.MonkeyPatch) -> type[_FakeContentCache]:
    _FakeContentCache._store = {}
    monkeypatch.setattr(mirror, "ContentCache", _FakeContentCache)
    return _FakeContentCache


def _install_fake_http(
    monkeypatch: pytest.MonkeyPatch, responses: list[_FakeResponse]
) -> _FakeHTTPClient:
    http_client = _FakeHTTPClient(responses)
    monkeypatch.setattr(
        RegistryFileMirrorIterator, "get_http_client", lambda _self: http_client
    )
    return http_client


def test_cache_hit_advances_visited_mirrors(
    fake_cache: type[_FakeContentCache], monkeypatch: pytest.MonkeyPatch
) -> None:
    # A cached mirror must be recorded as visited on the cache hit path,
    # otherwise the next iteration would recompute the same cache key and
    # replay the same redirect forever when the mirror keeps failing.
    url = "https://dl.example.com/packages/tool.tar.gz"
    fake_cache._store[ContentCache.key_from_args("head", url, [])] = json.dumps(
        {
            "Location": "https://mirror-a.example.com/tool.tar.gz",
            "X-PIO-Content-SHA256": "aaa",
            "X-PIO-Mirror": "mirror-a",
        }
    )
    http_client = _install_fake_http(
        monkeypatch,
        [
            _FakeResponse(
                302,
                {
                    "Location": "https://mirror-b.example.com/tool.tar.gz",
                    "X-PIO-Mirror": "mirror-b",
                    "X-PIO-Content-SHA256": "bbb",
                },
            )
        ],
    )

    iterator = RegistryFileMirrorIterator(url)
    first = next(iterator)
    second = next(iterator)

    assert first == ("https://mirror-a.example.com/tool.tar.gz", "aaa")
    assert second == ("https://mirror-b.example.com/tool.tar.gz", "bbb")
    assert http_client.requests, "second iteration should issue a HEAD request"
    assert http_client.requests[-1][2]["params"] == {"bypass": "mirror-a"}


def test_cache_entry_without_mirror_header_falls_through(
    fake_cache: type[_FakeContentCache], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Entries written before X-PIO-Mirror was cached lack the field; the
    # iterator must treat them as unusable and request a fresh redirect so
    # the fix self heals existing caches.
    url = "https://dl.example.com/packages/tool.tar.gz"
    fake_cache._store[ContentCache.key_from_args("head", url, [])] = json.dumps(
        {
            "Location": "https://mirror-a.example.com/tool.tar.gz",
            "X-PIO-Content-SHA256": "aaa",
        }
    )
    _install_fake_http(
        monkeypatch,
        [
            _FakeResponse(
                302,
                {
                    "Location": "https://mirror-b.example.com/tool.tar.gz",
                    "X-PIO-Mirror": "mirror-b",
                    "X-PIO-Content-SHA256": "bbb",
                },
            )
        ],
    )

    iterator = RegistryFileMirrorIterator(url)

    assert next(iterator) == ("https://mirror-b.example.com/tool.tar.gz", "bbb")


def test_head_response_caches_mirror_header(
    fake_cache: type[_FakeContentCache], monkeypatch: pytest.MonkeyPatch
) -> None:
    # The iterator must persist X-PIO-Mirror so later runs can tell whether
    # the cached redirect still names a mirror that has not been tried.
    url = "https://dl.example.com/packages/tool.tar.gz"
    _install_fake_http(
        monkeypatch,
        [
            _FakeResponse(
                302,
                {
                    "Location": "https://mirror-a.example.com/tool.tar.gz",
                    "X-PIO-Mirror": "mirror-a",
                    "X-PIO-Content-SHA256": "aaa",
                },
            )
        ],
    )

    iterator = RegistryFileMirrorIterator(url)
    next(iterator)

    cached = json.loads(
        fake_cache._store[ContentCache.key_from_args("head", url, [])]
    )
    assert cached["X-PIO-Mirror"] == "mirror-a"
    assert cached["Location"] == "https://mirror-a.example.com/tool.tar.gz"

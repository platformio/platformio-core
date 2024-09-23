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
import socket
from urllib.parse import urljoin

import requests.adapters
from urllib3.util.retry import Retry

from platformio import __check_internet_hosts__, app, util
from platformio.cache import ContentCache, cleanup_content_cache
from platformio.compat import is_proxy_set
from platformio.exception import PlatformioException, UserSideException

__default_requests_timeout__ = (10, None)  # (connect, read)


class HTTPClientError(UserSideException):
    def __init__(self, message, response=None):
        super().__init__()
        self.message = message
        self.response = response

    def __str__(self):  # pragma: no cover
        return self.message


class InternetConnectionError(UserSideException):
    MESSAGE = (
        "You are not connected to the Internet.\n"
        "PlatformIO needs the Internet connection to"
        " download dependent packages or to work with PlatformIO Account."
    )


class HTTPSession(requests.Session):
    def __init__(self, *args, **kwargs):
        self._x_base_url = kwargs.pop("x_base_url") if "x_base_url" in kwargs else None
        super().__init__(*args, **kwargs)
        self.headers.update({"User-Agent": app.get_user_agent()})
        try:
            self.verify = app.get_setting("enable_proxy_strict_ssl")
        except PlatformioException:
            self.verify = True

    def request(  # pylint: disable=signature-differs,arguments-differ
        self, method, url, *args, **kwargs
    ):
        # print("HTTPSession::request", self._x_base_url, method, url, args, kwargs)
        if "timeout" not in kwargs:
            kwargs["timeout"] = __default_requests_timeout__
        return super().request(
            method,
            (
                url
                if url.startswith("http") or not self._x_base_url
                else urljoin(self._x_base_url, url)
            ),
            *args,
            **kwargs
        )


class HTTPSessionIterator:
    def __init__(self, endpoints):
        if not isinstance(endpoints, list):
            endpoints = [endpoints]
        self.endpoints = endpoints
        self.endpoints_iter = iter(endpoints)
        # https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html
        self.retry = Retry(
            total=5,
            backoff_factor=1,  # [0, 2, 4, 8, 16] secs
            # method_whitelist=list(Retry.DEFAULT_METHOD_WHITELIST) + ["POST"],
            status_forcelist=[413, 429, 500, 502, 503, 504],
        )

    def __iter__(self):  # pylint: disable=non-iterator-returned
        return self

    def __next__(self):
        base_url = next(self.endpoints_iter)
        session = HTTPSession(x_base_url=base_url)
        adapter = requests.adapters.HTTPAdapter(max_retries=self.retry)
        session.mount(base_url, adapter)
        return session


class HTTPClient:
    def __init__(self, endpoints):
        self._session_iter = HTTPSessionIterator(endpoints)
        self._session = None
        self._next_session()

    def __del__(self):
        if not self._session:
            return
        try:
            self._session.close()
        except:  # pylint: disable=bare-except
            pass
        self._session = None

    def _next_session(self):
        if self._session:
            self._session.close()
        self._session = next(self._session_iter)

    @util.throttle(500)
    def send_request(self, method, path, **kwargs):
        # check Internet before and resolve issue with 60 seconds timeout
        ensure_internet_on(raise_exception=True)

        headers = kwargs.get("headers", {})
        with_authorization = (
            kwargs.pop("x_with_authorization")
            if "x_with_authorization" in kwargs
            else False
        )
        if with_authorization and "Authorization" not in headers:
            # pylint: disable=import-outside-toplevel
            from platformio.account.client import AccountClient

            headers["Authorization"] = (
                "Bearer %s" % AccountClient().fetch_authentication_token()
            )
        kwargs["headers"] = headers

        while True:
            try:
                return getattr(self._session, method)(path, **kwargs)
            except requests.exceptions.RequestException as exc:
                try:
                    self._next_session()
                except Exception as exc2:
                    raise HTTPClientError(str(exc2)) from exc

    def fetch_json_data(self, method, path, **kwargs):
        if method not in ("get", "head", "options"):
            cleanup_content_cache("http")
        cache_valid = kwargs.pop("x_cache_valid") if "x_cache_valid" in kwargs else None
        if not cache_valid:
            return self._parse_json_response(self.send_request(method, path, **kwargs))
        cache_key = ContentCache.key_from_args(
            method, path, kwargs.get("params"), kwargs.get("data")
        )
        with ContentCache("http") as cc:
            result = cc.get(cache_key)
            if result is not None:
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    pass
            response = self.send_request(method, path, **kwargs)
            data = self._parse_json_response(response)
            cc.set(cache_key, response.text, cache_valid)
            return data

    @staticmethod
    def _parse_json_response(response, expected_codes=(200, 201, 202)):
        if response.status_code in expected_codes:
            try:
                return response.json()
            except ValueError:
                pass
        try:
            message = response.json()["message"]
        except (KeyError, ValueError):
            message = response.text
        raise HTTPClientError(message, response)


#
# Helpers
#


@util.memoized(expire="10s")
def _internet_on():
    timeout = 2
    use_proxy = is_proxy_set()
    socket.setdefaulttimeout(timeout)
    for host in __check_internet_hosts__:
        try:
            if use_proxy:
                requests.get("http://%s" % host, allow_redirects=False, timeout=timeout)
                return True
            # try to resolve `host` for both AF_INET and AF_INET6, and then try to connect
            # to all possible addresses (IPv4 and IPv6) in turn until a connection succeeds:
            s = socket.create_connection((host, 80))
            s.close()
            return True
        except:  # pylint: disable=bare-except
            pass

    # falling back to HTTPs, issue #4980
    for host in __check_internet_hosts__:
        try:
            requests.get("https://%s" % host, allow_redirects=False, timeout=timeout)
        except requests.exceptions.RequestException:
            pass
        return True

    return False


def ensure_internet_on(raise_exception=False):
    result = _internet_on()
    if raise_exception and not result:
        raise InternetConnectionError()
    return result


def fetch_remote_content(*args, **kwargs):
    with HTTPSession() as s:
        r = s.get(*args, **kwargs)
        r.raise_for_status()
        r.close()
        return r.text

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

import contextlib
import itertools
import json
import socket
import time

import httpx

from platformio import __check_internet_hosts__, app, util
from platformio.cache import ContentCache, cleanup_content_cache
from platformio.exception import PlatformioException, UserSideException
from platformio.pipdeps import is_proxy_set

RETRIES_BACKOFF_FACTOR = 2  # 0s, 2s, 4s, 8s, etc.
RETRIES_METHOD_WHITELIST = ["GET"]
RETRIES_STATUS_FORCELIST = [429, 500, 502, 503, 504]


class HttpClientApiError(UserSideException):
    def __init__(self, message, response=None):
        super().__init__()
        self.message = message
        self.response = response

    def __str__(self):  # pragma: no cover
        return self.message


class InternetConnectionError(UserSideException):
    MESSAGE = (
        "You are not connected to the Internet.\n"
        "PlatformIO needs the Internet connection to "
        "download dependent packages or to work with PlatformIO Account."
    )


def exponential_backoff(factor):
    yield 0
    for n in itertools.count(2):
        yield factor * (2 ** (n - 2))


def apply_default_kwargs(kwargs=None):
    kwargs = kwargs or {}
    # enable redirects by default
    kwargs["follow_redirects"] = kwargs.get("follow_redirects", True)

    try:
        kwargs["verify"] = kwargs.get(
            "verify", app.get_setting("enable_proxy_strict_ssl")
        )
    except PlatformioException:
        kwargs["verify"] = True

    headers = kwargs.pop("headers", {})
    if "User-Agent" not in headers:
        headers.update({"User-Agent": app.get_user_agent()})
        kwargs["headers"] = headers

    retry = kwargs.pop("retry", None)
    if retry:
        kwargs["transport"] = HTTPRetryTransport(verify=kwargs["verify"], **retry)

    return kwargs


class HTTPRetryTransport(httpx.HTTPTransport):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        verify=True,
        retries=1,
        backoff_factor=None,
        status_forcelist=None,
        method_whitelist=None,
    ):
        super().__init__(verify=verify)
        self._retries = retries
        self._backoff_factor = backoff_factor or RETRIES_BACKOFF_FACTOR
        self._status_forcelist = status_forcelist or RETRIES_STATUS_FORCELIST
        self._method_whitelist = method_whitelist or RETRIES_METHOD_WHITELIST

    def handle_request(self, request):
        retries_left = self._retries
        delays = exponential_backoff(factor=RETRIES_BACKOFF_FACTOR)
        while retries_left > 0:
            retries_left -= 1
            try:
                response = super().handle_request(request)
                if response.status_code in RETRIES_STATUS_FORCELIST:
                    if request.method.upper() not in self._method_whitelist:
                        return response
                    raise httpx.HTTPStatusError(
                        f"Server error '{response.status_code} {response.reason_phrase}' "
                        f"for url '{request.url}'\n",
                        request=request,
                        response=response,
                    )
                return response
            except httpx.HTTPError:
                if retries_left == 0:
                    raise
                time.sleep(next(delays) or 1)

        raise httpx.RequestError(
            f"Could not process '{request.url}' request", request=request
        )


class HTTPSession(httpx.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **apply_default_kwargs(kwargs))


class HttpEndpointPool:
    def __init__(self, endpoints, session_retry=None):
        if not isinstance(endpoints, list):
            endpoints = [endpoints]
        self.endpoints = endpoints
        self.session_retry = session_retry

        self._endpoints_iter = iter(endpoints)
        self._session = None

        self.next()

    def close(self):
        if self._session:
            self._session.close()

    def next(self):
        if self._session:
            self._session.close()
        self._session = HTTPSession(
            base_url=next(self._endpoints_iter), retry=self.session_retry
        )

    def request(self, method, *args, **kwargs):
        while True:
            try:
                return self._session.request(method, *args, **kwargs)
            except httpx.HTTPError as exc:
                try:
                    self.next()
                except StopIteration as exc2:
                    raise exc from exc2


class HttpApiClient(contextlib.AbstractContextManager):
    def __init__(self, endpoints):
        self._endpoint = HttpEndpointPool(endpoints, session_retry=dict(retries=5))

    def __exit__(self, *excinfo):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if getattr(self, "_endpoint"):
            self._endpoint.close()

    @util.throttle(500)
    def send_request(self, method, *args, **kwargs):
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

            with AccountClient() as client:
                headers["Authorization"] = (
                    "Bearer %s" % client.fetch_authentication_token()
                )
        kwargs["headers"] = headers

        try:
            return self._endpoint.request(method, *args, **kwargs)
        except httpx.HTTPError as exc:
            raise HttpClientApiError(str(exc)) from exc

    def fetch_json_data(self, method, path, **kwargs):
        if method not in ("get", "head", "options"):
            cleanup_content_cache("http")
        # remove empty params
        if kwargs.get("params"):
            kwargs["params"] = {
                key: value
                for key, value in kwargs.get("params").items()
                if value is not None
            }

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
        raise HttpClientApiError(message, response)


#
# Helpers
#


@util.memoized(expire="10s")
def _internet_on():
    timeout = 2
    socket.setdefaulttimeout(timeout)
    for host in __check_internet_hosts__:
        try:
            if is_proxy_set():
                httpx.get("http://%s" % host, follow_redirects=False, timeout=timeout)
                return True
            # try to resolve `host` for both AF_INET and AF_INET6, and then try to connect
            # to all possible addresses (IPv4 and IPv6) in turn until a connection succeeds:
            s = socket.create_connection((host, 80))
            s.close()
            return True
        except:  # pylint: disable=bare-except
            pass
    return False


def ensure_internet_on(raise_exception=False):
    result = _internet_on()
    if raise_exception and not result:
        raise InternetConnectionError()
    return result


def fetch_http_content(*args, **kwargs):
    with HTTPSession() as session:
        response = session.get(*args, **kwargs)
        response.raise_for_status()
        return response.text

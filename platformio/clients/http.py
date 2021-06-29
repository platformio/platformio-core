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
import math
import os
import socket

import requests.adapters
from requests.packages.urllib3.util.retry import Retry  # pylint:disable=import-error

from platformio import __check_internet_hosts__, __default_requests_timeout__, app, util
from platformio.cache import ContentCache
from platformio.exception import PlatformioException, UserSideException

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class HTTPClientError(PlatformioException):
    def __init__(self, message, response=None):
        super(HTTPClientError, self).__init__()
        self.message = message
        self.response = response

    def __str__(self):  # pragma: no cover
        return self.message


class InternetIsOffline(UserSideException):

    MESSAGE = (
        "You are not connected to the Internet.\n"
        "PlatformIO needs the Internet connection to"
        " download dependent packages or to work with PlatformIO Account."
    )


class EndpointSession(requests.Session):
    def __init__(self, base_url, *args, **kwargs):
        super(EndpointSession, self).__init__(*args, **kwargs)
        self.base_url = base_url

    def request(  # pylint: disable=signature-differs,arguments-differ
        self, method, url, *args, **kwargs
    ):
        # print(self.base_url, method, url, args, kwargs)
        return super(EndpointSession, self).request(
            method, urljoin(self.base_url, url), *args, **kwargs
        )


class EndpointSessionIterator(object):
    def __init__(self, endpoints):
        if not isinstance(endpoints, list):
            endpoints = [endpoints]
        self.endpoints = endpoints
        self.endpoints_iter = iter(endpoints)
        self.retry = Retry(
            total=math.ceil(6 / len(self.endpoints)),
            backoff_factor=1,
            # method_whitelist=list(Retry.DEFAULT_METHOD_WHITELIST) + ["POST"],
            status_forcelist=[413, 429, 500, 502, 503, 504],
        )

    def __iter__(self):  # pylint: disable=non-iterator-returned
        return self

    def next(self):
        """For Python 2 compatibility"""
        return self.__next__()

    def __next__(self):
        base_url = next(self.endpoints_iter)
        session = EndpointSession(base_url)
        session.headers.update({"User-Agent": app.get_user_agent()})
        adapter = requests.adapters.HTTPAdapter(max_retries=self.retry)
        session.mount(base_url, adapter)
        return session


class HTTPClient(object):
    def __init__(self, endpoints):
        self._session_iter = EndpointSessionIterator(endpoints)
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

        # set default timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = __default_requests_timeout__

        while True:
            try:
                return getattr(self._session, method)(path, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as e:
                try:
                    self._next_session()
                except:  # pylint: disable=bare-except
                    raise HTTPClientError(str(e))

    def fetch_json_data(self, method, path, **kwargs):
        cache_valid = kwargs.pop("cache_valid") if "cache_valid" in kwargs else None
        if not cache_valid:
            return self._parse_json_response(self.send_request(method, path, **kwargs))
        cache_key = ContentCache.key_from_args(
            method, path, kwargs.get("params"), kwargs.get("data")
        )
        with ContentCache("http") as cc:
            result = cc.get(cache_key)
            if result is not None:
                return json.loads(result)
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
    socket.setdefaulttimeout(timeout)
    for host in __check_internet_hosts__:
        try:
            for var in ("HTTP_PROXY", "HTTPS_PROXY"):
                if not os.getenv(var) and not os.getenv(var.lower()):
                    continue
                requests.get("http://%s" % host, allow_redirects=False, timeout=timeout)
                return True
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            s.close()
            return True
        except:  # pylint: disable=bare-except
            pass
    return False


def ensure_internet_on(raise_exception=False):
    result = _internet_on()
    if raise_exception and not result:
        raise InternetIsOffline()
    return result


def fetch_remote_content(*args, **kwargs):
    kwargs["headers"] = kwargs.get("headers", {})
    if "User-Agent" not in kwargs["headers"]:
        kwargs["headers"]["User-Agent"] = app.get_user_agent()

    if "timeout" not in kwargs:
        kwargs["timeout"] = __default_requests_timeout__

    r = requests.get(*args, **kwargs)
    r.raise_for_status()
    return r.text

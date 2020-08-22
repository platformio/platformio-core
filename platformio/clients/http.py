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
import os
import socket

import requests.adapters
from requests.packages.urllib3.util.retry import Retry  # pylint:disable=import-error

from platformio import DEFAULT_REQUESTS_TIMEOUT, app, util
from platformio.cache import ContentCache
from platformio.exception import PlatformioException, UserSideException

PING_REMOTE_HOSTS = [
    "140.82.118.3",  # Github.com
    "35.231.145.151",  # Gitlab.com
    "88.198.170.159",  # platformio.org
    "github.com",
    "platformio.org",
]


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
        " download dependent packages or to work with PIO Account."
    )


class HTTPClient(object):
    def __init__(
        self, base_url,
    ):
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": app.get_user_agent()})
        retry = Retry(
            total=5,
            backoff_factor=1,
            # method_whitelist=list(Retry.DEFAULT_METHOD_WHITELIST) + ["POST"],
            status_forcelist=[413, 429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount(base_url, adapter)

    def __del__(self):
        if not self._session:
            return
        self._session.close()
        self._session = None

    @util.throttle(500)
    def send_request(self, method, path, **kwargs):
        # check Internet before and resolve issue with 60 seconds timeout
        # print(self, method, path, kwargs)
        ensure_internet_on(raise_exception=True)

        # set default timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = DEFAULT_REQUESTS_TIMEOUT

        try:
            return getattr(self._session, method)(self.base_url + path, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise HTTPClientError(str(e))

    def fetch_json_data(self, method, path, **kwargs):
        cache_valid = kwargs.pop("cache_valid") if "cache_valid" in kwargs else None
        if not cache_valid:
            return self.raise_error_from_response(
                self.send_request(method, path, **kwargs)
            )
        cache_key = ContentCache.key_from_args(
            method, path, kwargs.get("params"), kwargs.get("data")
        )
        with ContentCache("http") as cc:
            result = cc.get(cache_key)
            if result is not None:
                return json.loads(result)
            response = self.send_request(method, path, **kwargs)
            cc.set(cache_key, response.text, cache_valid)
            return self.raise_error_from_response(response)

    @staticmethod
    def raise_error_from_response(response, expected_codes=(200, 201, 202)):
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
    for host in PING_REMOTE_HOSTS:
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
        kwargs["timeout"] = DEFAULT_REQUESTS_TIMEOUT

    r = requests.get(*args, **kwargs)
    r.raise_for_status()
    return r.text

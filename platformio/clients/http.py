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

import requests.adapters
from requests.packages.urllib3.util.retry import Retry  # pylint:disable=import-error

from platformio import app, util
from platformio.exception import PlatformioException


class HTTPClientError(PlatformioException):
    def __init__(self, message, response=None):
        super(HTTPClientError, self).__init__()
        self.message = message
        self.response = response

    def __str__(self):  # pragma: no cover
        return self.message


class HTTPClient(object):
    def __init__(self, base_url):
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

    def send_request(self, method, path, **kwargs):
        # check Internet before and resolve issue with 60 seconds timeout
        # print(self, method, path, kwargs)
        util.internet_on(raise_exception=True)
        try:
            return getattr(self._session, method)(self.base_url + path, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise HTTPClientError(str(e))

    def request_json_data(self, *args, **kwargs):
        response = self.send_request(*args, **kwargs)
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

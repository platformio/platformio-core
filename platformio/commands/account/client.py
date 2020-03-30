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

# pylint: disable=unused-argument

import os
import time

import requests.adapters
from requests.packages.urllib3.util.retry import Retry  # pylint:disable=import-error

from platformio import app, exception

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class AccountClient(object):
    def __init__(
        self,
        base_url="http://account.platormio.org/v1/",
        timeout=60,
        verify=True,
        retries=3,
    ):
        if not base_url.endswith("/"):
            base_url += "/"
        self._base_url = base_url
        self._timeout = timeout
        self._verify = verify
        self._session = requests.Session()
        method_whitelist = set(Retry.DEFAULT_METHOD_WHITELIST)
        method_whitelist.add("POST")
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=2,
            status_forcelist=(500, 502, 503, 504),
            method_whitelist=frozenset(method_whitelist),
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get_authentication_token(self):
        auth = app.get_state_item("account", {}).get("auth", {})
        if auth.get("access_token") and auth.get("access_token_expire"):
            if auth.get("access_token_expire") > time.time():
                return auth.get("access_token")
            if not auth.get("refresh_token"):
                return None
            resp = self._session.post(
                urljoin(self._base_url, "account/login"),
                headers={"Authorization": "Bearer %s" % auth.get("refresh_token")},
                verify=self._verify,
                timeout=self._timeout,
            )
            return self._finalize_login_response(resp).get("auth").get("access_token")
        if "PLATFORMIO_AUTH_TOKEN" not in os.environ:
            return None
        resp = self._session.post(
            urljoin(self._base_url, "account/login"),
            headers={
                "Authorization": "Bearer %s" % os.environ["PLATFORMIO_AUTH_TOKEN"]
            },
            verify=self._verify,
            timeout=self._timeout,
        )
        return self._finalize_login_response(resp).get("auth").get("access_token")

    def login(self, username, password):
        try:
            if self.get_authentication_token():
                raise exception.AccountAlreadyLoggedIn(
                    app.get_state_item("account").get("email")
                )
        except exception.AccountAlreadyLoggedIn as e:
            raise e
        except:  # pylint:disable=bare-except
            pass

        resp = self._session.post(
            urljoin(self._base_url, "account/login"),
            json={"username": username, "password": password},
            verify=self._verify,
            timeout=self._timeout,
        )
        return self._finalize_login_response(resp)

    def logout(self):
        refresh_token = self._get_refresh_token()
        if not refresh_token:
            raise exception.AccountNotLoggedIn()
        requests.post(
            urljoin(self._base_url, "account/logout"),
            json={"refresh_token": refresh_token},
            verify=self._verify,
            timeout=self._timeout,
        )
        app.delete_state_item("account")
        return True

    def change_password(self, new_password):
        token = self.get_authentication_token()
        if not token:
            raise exception.AccountNotLoggedIn()
        response = self._session.post(
            urljoin(self._base_url, "account/password"),
            headers={"Authorization": "Bearer %s" % token},
            json={"new_password": new_password},
            verify=self._verify,
            timeout=self._timeout,
        )
        if response.status_code != 200:
            raise exception.AccountError(response.json().get("message"))
        return True

    @staticmethod
    def _finalize_login_response(response):
        resp_json = response.json()
        if response.status_code != 200:
            raise exception.AccountError(resp_json.get("message"))
        app.set_state_item("account", resp_json)
        return resp_json

    @staticmethod
    def _get_refresh_token():
        auth = app.get_state_item("account", {}).get("auth", {})
        return auth.get("refresh_token")

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


class AccountClient(object):
    def __init__(
        self, api_base_url="https://api.account.platormio.org/", retries=3,
    ):
        if not api_base_url.endswith("/"):
            api_base_url += "/"
        self.api_base_url = api_base_url
        self._session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=2,
            method_whitelist=list(Retry.DEFAULT_METHOD_WHITELIST) + ["POST"],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount(api_base_url, adapter)

    def login(self, username, password):
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise exception.AccountAlreadyAuthenticated(
                app.get_state_item("account").get("email")
            )

        response = self._session.post(
            self.api_base_url + "v1/login",
            json={"username": username, "password": password},
        )
        result = self.raise_error_from_response(response)
        app.set_state_item("account", result)
        return result

    def logout(self):
        try:
            refresh_token = self.get_refresh_token()
        except:  # pylint:disable=bare-except
            raise exception.AccountNotAuthenticated()
        response = requests.post(
            self.api_base_url + "v1/logout", json={"refresh_token": refresh_token},
        )
        self.raise_error_from_response(response)
        app.delete_state_item("account")
        return True

    def change_password(self, old_password, new_password):
        try:
            token = self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            raise exception.AccountNotAuthenticated()
        response = self._session.post(
            self.api_base_url + "v1/password",
            headers={"Authorization": "Bearer %s" % token},
            json={"old_password": old_password, "new_password": new_password},
        )
        self.raise_error_from_response(response)
        return True

    def fetch_authentication_token(self):
        auth = app.get_state_item("account", {}).get("auth", {})
        if auth.get("access_token") and auth.get("access_token_expire"):
            if auth.get("access_token_expire") > time.time():
                return auth.get("access_token")
            if auth.get("refresh_token"):
                response = self._session.post(
                    self.api_base_url + "v1/login",
                    headers={"Authorization": "Bearer %s" % auth.get("refresh_token")},
                )
                result = self.raise_error_from_response(response)
                app.set_state_item("account", result)
                return result.get("auth").get("access_token")
        if "PLATFORMIO_AUTH_TOKEN" not in os.environ:
            raise exception.AccountNotAuthenticated()
        response = self._session.post(
            self.api_base_url + "v1/login",
            headers={
                "Authorization": "Bearer %s" % os.environ["PLATFORMIO_AUTH_TOKEN"]
            },
        )
        result = self.raise_error_from_response(response)
        app.set_state_item("account", result)
        return result.get("auth").get("access_token")

    @staticmethod
    def get_refresh_token():
        try:
            auth = app.get_state_item("account").get("auth").get("refresh_token")
            return auth
        except:  # pylint:disable=bare-except
            raise exception.AccountNotAuthenticated()

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
            message = response.content
        raise exception.AccountError(message)

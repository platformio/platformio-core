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

import os
import time

from platformio import __accounts_api__, app
from platformio.clients.rest import RESTClient
from platformio.exception import PlatformioException


class AccountError(PlatformioException):

    MESSAGE = "{0}"


class AccountNotAuthorized(AccountError):

    MESSAGE = "You are not authorized! Please log in to PIO Account."


class AccountAlreadyAuthorized(AccountError):

    MESSAGE = "You are already authorized with {0} account."


class AccountClient(RESTClient):

    SUMMARY_CACHE_TTL = 60 * 60 * 24 * 7

    def __init__(self):
        super(AccountClient, self).__init__(base_url=__accounts_api__)

    @staticmethod
    def get_refresh_token():
        try:
            return app.get_state_item("account").get("auth").get("refresh_token")
        except:  # pylint:disable=bare-except
            raise AccountNotAuthorized()

    @staticmethod
    def delete_local_session():
        app.delete_state_item("account")

    @staticmethod
    def delete_local_state(key):
        account = app.get_state_item("account")
        if not account or key not in account:
            return
        del account[key]
        app.set_state_item("account", account)

    def login(self, username, password):
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise AccountAlreadyAuthorized(
                app.get_state_item("account", {}).get("email", "")
            )

        result = self.send_request(
            "post", "/v1/login", data={"username": username, "password": password},
        )
        app.set_state_item("account", result)
        return result

    def login_with_code(self, client_id, code, redirect_uri):
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise AccountAlreadyAuthorized(
                app.get_state_item("account", {}).get("email", "")
            )

        result = self.send_request(
            "post",
            "/v1/login/code",
            data={"client_id": client_id, "code": code, "redirect_uri": redirect_uri},
        )
        app.set_state_item("account", result)
        return result

    def logout(self):
        refresh_token = self.get_refresh_token()
        self.delete_local_session()
        try:
            self.send_request(
                "post", "/v1/logout", data={"refresh_token": refresh_token},
            )
        except AccountError:
            pass
        return True

    def change_password(self, old_password, new_password):
        token = self.fetch_authentication_token()
        self.send_request(
            "post",
            "/v1/password",
            headers={"Authorization": "Bearer %s" % token},
            data={"old_password": old_password, "new_password": new_password},
        )
        return True

    def registration(
        self, username, email, password, firstname, lastname
    ):  # pylint:disable=too-many-arguments
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise AccountAlreadyAuthorized(
                app.get_state_item("account", {}).get("email", "")
            )

        return self.send_request(
            "post",
            "/v1/registration",
            data={
                "username": username,
                "email": email,
                "password": password,
                "firstname": firstname,
                "lastname": lastname,
            },
        )

    def auth_token(self, password, regenerate):
        token = self.fetch_authentication_token()
        result = self.send_request(
            "post",
            "/v1/token",
            headers={"Authorization": "Bearer %s" % token},
            data={"password": password, "regenerate": 1 if regenerate else 0},
        )
        return result.get("auth_token")

    def forgot_password(self, username):
        return self.send_request("post", "/v1/forgot", data={"username": username},)

    def get_profile(self):
        token = self.fetch_authentication_token()
        return self.send_request(
            "get", "/v1/profile", headers={"Authorization": "Bearer %s" % token},
        )

    def update_profile(self, profile, current_password):
        token = self.fetch_authentication_token()
        profile["current_password"] = current_password
        self.delete_local_state("summary")
        response = self.send_request(
            "put",
            "/v1/profile",
            headers={"Authorization": "Bearer %s" % token},
            data=profile,
        )
        return response

    def get_account_info(self, offline=False):
        account = app.get_state_item("account")
        if not account:
            raise AccountNotAuthorized()
        if (
            account.get("summary")
            and account["summary"].get("expire_at", 0) > time.time()
        ):
            return account["summary"]
        if offline:
            return {
                "profile": {
                    "email": account.get("email"),
                    "username": account.get("username"),
                }
            }
        token = self.fetch_authentication_token()
        result = self.send_request(
            "get", "/v1/summary", headers={"Authorization": "Bearer %s" % token},
        )
        account["summary"] = dict(
            profile=result.get("profile"),
            packages=result.get("packages"),
            subscriptions=result.get("subscriptions"),
            user_id=result.get("user_id"),
            expire_at=int(time.time()) + self.SUMMARY_CACHE_TTL,
        )
        app.set_state_item("account", account)
        return result

    def fetch_authentication_token(self):
        if "PLATFORMIO_AUTH_TOKEN" in os.environ:
            return os.environ["PLATFORMIO_AUTH_TOKEN"]
        auth = app.get_state_item("account", {}).get("auth", {})
        if auth.get("access_token") and auth.get("access_token_expire"):
            if auth.get("access_token_expire") > time.time():
                return auth.get("access_token")
            if auth.get("refresh_token"):
                try:
                    result = self.send_request(
                        "post",
                        "/v1/login",
                        headers={
                            "Authorization": "Bearer %s" % auth.get("refresh_token")
                        },
                    )
                    app.set_state_item("account", result)
                    return result.get("auth").get("access_token")
                except AccountError:
                    self.delete_local_session()
        raise AccountNotAuthorized()

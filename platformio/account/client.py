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
from platformio.exception import PlatformioException, UserSideException
from platformio.http import HTTPClient, HTTPClientError


class AccountError(PlatformioException):
    MESSAGE = "{0}"


class AccountNotAuthorized(AccountError, UserSideException):
    MESSAGE = "You are not authorized! Please log in to PlatformIO Account."


class AccountAlreadyAuthorized(AccountError, UserSideException):
    MESSAGE = "You are already authorized with {0} account."


class AccountClient(HTTPClient):  # pylint:disable=too-many-public-methods
    SUMMARY_CACHE_TTL = 60 * 60 * 24 * 7

    def __init__(self):
        super().__init__(__accounts_api__)

    @staticmethod
    def get_refresh_token():
        try:
            return app.get_state_item("account").get("auth").get("refresh_token")
        except Exception as exc:
            raise AccountNotAuthorized() from exc

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

    def fetch_json_data(self, *args, **kwargs):
        try:
            return super().fetch_json_data(*args, **kwargs)
        except HTTPClientError as exc:
            raise AccountError(exc) from exc

    def fetch_authentication_token(self):
        if os.environ.get("PLATFORMIO_AUTH_TOKEN"):
            return os.environ.get("PLATFORMIO_AUTH_TOKEN")
        auth = app.get_state_item("account", {}).get("auth", {})
        if auth.get("access_token") and auth.get("access_token_expire"):
            if auth.get("access_token_expire") > time.time():
                return auth.get("access_token")
            if auth.get("refresh_token"):
                try:
                    data = self.fetch_json_data(
                        "post",
                        "/v1/login",
                        headers={
                            "Authorization": "Bearer %s" % auth.get("refresh_token")
                        },
                    )
                    app.set_state_item("account", data)
                    return data.get("auth").get("access_token")
                except AccountError:
                    self.delete_local_session()
        raise AccountNotAuthorized()

    def login(self, username, password):
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise AccountAlreadyAuthorized(
                app.get_state_item("account", {}).get("email", "")
            )

        data = self.fetch_json_data(
            "post",
            "/v1/login",
            data={"username": username, "password": password},
        )
        app.set_state_item("account", data)
        return data

    def login_with_code(self, client_id, code, redirect_uri):
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise AccountAlreadyAuthorized(
                app.get_state_item("account", {}).get("email", "")
            )

        result = self.fetch_json_data(
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
            self.fetch_json_data(
                "post",
                "/v1/logout",
                data={"refresh_token": refresh_token},
            )
        except AccountError:
            pass
        return True

    def change_password(self, old_password, new_password):
        return self.fetch_json_data(
            "post",
            "/v1/password",
            data={"old_password": old_password, "new_password": new_password},
            x_with_authorization=True,
        )

    def registration(
        self, username, email, password, firstname, lastname
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        try:
            self.fetch_authentication_token()
        except:  # pylint:disable=bare-except
            pass
        else:
            raise AccountAlreadyAuthorized(
                app.get_state_item("account", {}).get("email", "")
            )

        return self.fetch_json_data(
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
        return self.fetch_json_data(
            "post",
            "/v1/token",
            data={"password": password, "regenerate": 1 if regenerate else 0},
            x_with_authorization=True,
        ).get("auth_token")

    def forgot_password(self, username):
        return self.fetch_json_data(
            "post",
            "/v1/forgot",
            data={"username": username},
        )

    def get_profile(self):
        return self.fetch_json_data(
            "get",
            "/v1/profile",
            x_with_authorization=True,
        )

    def update_profile(self, profile, current_password):
        profile["current_password"] = current_password
        self.delete_local_state("summary")
        response = self.fetch_json_data(
            "put",
            "/v1/profile",
            data=profile,
            x_with_authorization=True,
        )
        return response

    def get_account_info(self, offline=False):
        account = app.get_state_item("account") or {}
        if (
            account.get("summary")
            and account["summary"].get("expire_at", 0) > time.time()
        ):
            return account["summary"]
        if offline and account.get("email"):
            return {
                "profile": {
                    "email": account.get("email"),
                    "username": account.get("username"),
                }
            }
        result = self.fetch_json_data(
            "get",
            "/v1/summary",
            x_with_authorization=True,
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

    def get_logged_username(self):
        return self.get_account_info(offline=True).get("profile").get("username")

    def destroy_account(self):
        return self.fetch_json_data(
            "delete",
            "/v1/account",
            x_with_authorization=True,
        )

    def create_org(self, orgname, email, displayname):
        return self.fetch_json_data(
            "post",
            "/v1/orgs",
            data={"orgname": orgname, "email": email, "displayname": displayname},
            x_with_authorization=True,
        )

    def get_org(self, orgname):
        return self.fetch_json_data(
            "get",
            "/v1/orgs/%s" % orgname,
            x_with_authorization=True,
        )

    def list_orgs(self):
        return self.fetch_json_data(
            "get",
            "/v1/orgs",
            x_with_authorization=True,
        )

    def update_org(self, orgname, data):
        return self.fetch_json_data(
            "put",
            "/v1/orgs/%s" % orgname,
            data={k: v for k, v in data.items() if v},
            x_with_authorization=True,
        )

    def destroy_org(self, orgname):
        return self.fetch_json_data(
            "delete",
            "/v1/orgs/%s" % orgname,
            x_with_authorization=True,
        )

    def add_org_owner(self, orgname, username):
        return self.fetch_json_data(
            "post",
            "/v1/orgs/%s/owners" % orgname,
            data={"username": username},
            x_with_authorization=True,
        )

    def list_org_owners(self, orgname):
        return self.fetch_json_data(
            "get",
            "/v1/orgs/%s/owners" % orgname,
            x_with_authorization=True,
        )

    def remove_org_owner(self, orgname, username):
        return self.fetch_json_data(
            "delete",
            "/v1/orgs/%s/owners" % orgname,
            params={"username": username},
            x_with_authorization=True,
        )

    def create_team(self, orgname, teamname, description):
        return self.fetch_json_data(
            "post",
            "/v1/orgs/%s/teams" % orgname,
            data={"name": teamname, "description": description},
            x_with_authorization=True,
        )

    def destroy_team(self, orgname, teamname):
        return self.fetch_json_data(
            "delete",
            "/v1/orgs/%s/teams/%s" % (orgname, teamname),
            x_with_authorization=True,
        )

    def get_team(self, orgname, teamname):
        return self.fetch_json_data(
            "get",
            "/v1/orgs/%s/teams/%s" % (orgname, teamname),
            x_with_authorization=True,
        )

    def list_teams(self, orgname):
        return self.fetch_json_data(
            "get",
            "/v1/orgs/%s/teams" % orgname,
            x_with_authorization=True,
        )

    def update_team(self, orgname, teamname, data):
        return self.fetch_json_data(
            "put",
            "/v1/orgs/%s/teams/%s" % (orgname, teamname),
            data={k: v for k, v in data.items() if v},
            x_with_authorization=True,
        )

    def add_team_member(self, orgname, teamname, username):
        return self.fetch_json_data(
            "post",
            "/v1/orgs/%s/teams/%s/members" % (orgname, teamname),
            data={"username": username},
            x_with_authorization=True,
        )

    def remove_team_member(self, orgname, teamname, username):
        return self.fetch_json_data(
            "delete",
            "/v1/orgs/%s/teams/%s/members" % (orgname, teamname),
            params={"username": username},
            x_with_authorization=True,
        )

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

import jwt
import requests

from platformio import app, exception
from platformio.commands.account import (
    PIO_ACCOUNT_LOGIN_URL,
    PIO_ACCOUNT_REFRESH_TOKEN_URL,
)


def get_authentication_token():
    auth = app.get_state_item("account", {}).get("auth", {})
    if auth.get("access_token"):
        try:
            jwt.decode(
                auth.get("access_token"),
                algorithms="RS256",
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                    "verify_aud": False,
                },
            )
            return auth.get("access_token")
        except jwt.ExpiredSignatureError:
            if not auth.get("refresh_token"):
                return None
            resp = requests.post(
                PIO_ACCOUNT_REFRESH_TOKEN_URL,
                json={"refresh_token": auth.get("refresh_token")},
            )
            return process_login_response(resp).get("access_token")
    if "PLATFORMIO_AUTH_TOKEN" not in os.environ:
        return None
    resp = requests.post(
        PIO_ACCOUNT_LOGIN_URL,
        headers={"Authorization": "Bearer %s" % os.environ["PLATFORMIO_AUTH_TOKEN"]},
    )
    return process_login_response(resp).get("access_token")


def get_user_info_from_token(token):
    try:
        data = jwt.decode(token, algorithms="RS256", verify=False)
        return {
            "username": data.get("preferred_username"),
            "email": data.get("email"),
            "email_verified": data.get("email_verified"),
        }
    except:  # pylint:disable=bare-except
        return {}


def process_login_response(response):
    resp_json = response.json()
    if response.status_code != 200:
        raise exception.AccountError(resp_json.get("message"))
    data = get_user_info_from_token(resp_json.get("access_token"))
    data["auth"] = resp_json
    app.set_state_item("account", data)
    return resp_json

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
import time

import pytest

from platformio.commands.account.command import cli as cmd_account


@pytest.fixture(scope="session")
def credentials():
    return {
        "login": os.environ["PLATFORMIO_TEST_ACCOUNT_LOGIN"],
        "password": os.environ["PLATFORMIO_TEST_ACCOUNT_PASSWORD"],
    }


def test_account_register_with_already_exists_username(
    clirunner, credentials, isolated_pio_home
):
    username = credentials["login"]
    email = "test@test.com"
    if "@" in credentials["login"]:
        username = "Testusername"
        email = credentials["login"]
    result = clirunner.invoke(
        cmd_account,
        [
            "register",
            "-u",
            username,
            "-e",
            email,
            "-p",
            credentials["password"],
            "--firstname",
            "First",
            "--lastname",
            "Last",
        ],
    )
    assert result.exit_code > 0
    assert result.exception
    assert "User with same username already exists" in str(
        result.exception
    ) or "User with same email already exists" in str(result.exception)


@pytest.mark.skip_ci
def test_account_login_with_invalid_creds(clirunner, credentials, isolated_pio_home):
    result = clirunner.invoke(cmd_account, ["login", "-u", "123", "-p", "123"])
    assert result.exit_code > 0
    assert result.exception
    assert "Invalid user credentials" in str(result.exception)


def test_account_login(clirunner, credentials, validate_cliresult, isolated_pio_home):
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)
        assert "Successfully logged in!" in result.output

        with open(str(isolated_pio_home.join("appstate.json"))) as fp:
            appstate = json.load(fp)
            assert appstate.get("account")
            assert appstate.get("account").get("email")
            assert appstate.get("account").get("username")
            assert appstate.get("account").get("auth")
            assert appstate.get("account").get("auth").get("access_token")
            assert appstate.get("account").get("auth").get("access_token_expire")
            assert appstate.get("account").get("auth").get("refresh_token")

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are already authenticated with" in str(result.exception)
    finally:
        clirunner.invoke(cmd_account, ["logout"])


def test_account_logout(clirunner, credentials, validate_cliresult, isolated_pio_home):
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_account, ["logout"])
        validate_cliresult(result)
        assert "Successfully logged out" in result.output

        result = clirunner.invoke(cmd_account, ["logout"])
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )
    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_password_change_with_invalid_old_password(
    clirunner, credentials, validate_cliresult
):
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            ["password", "--old-password", "test", "--new-password", "test"],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "Invalid user password" in str(result.exception)

    finally:
        clirunner.invoke(cmd_account, ["logout"])


def test_account_password_change_with_invalid_new_password_format(
    clirunner, credentials, validate_cliresult
):
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            [
                "password",
                "--old-password",
                credentials["password"],
                "--new-password",
                "test",
            ],
        )
        assert result.exit_code > 0
        assert result.exception
        assert (
            "Invalid password format. Password must contain at"
            " least 8 characters including a number and a lowercase letter"
            in str(result.exception)
        )

    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_password_change(
    clirunner, credentials, validate_cliresult, isolated_pio_home
):
    try:
        result = clirunner.invoke(
            cmd_account,
            [
                "password",
                "--old-password",
                credentials["password"],
                "--new-password",
                "Testpassword123",
            ],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            [
                "password",
                "--old-password",
                credentials["password"],
                "--new-password",
                "Testpassword123",
            ],
        )
        validate_cliresult(result)
        assert "Password successfully changed!" in result.output

        result = clirunner.invoke(cmd_account, ["logout"])
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account, ["login", "-u", credentials["login"], "-p", "Testpassword123"],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            [
                "password",
                "--old-password",
                "Testpassword123",
                "--new-password",
                credentials["password"],
            ],
        )
        validate_cliresult(result)
        assert "Password successfully changed!" in result.output

    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_token_with_invalid_password(
    clirunner, credentials, validate_cliresult
):
    try:
        result = clirunner.invoke(
            cmd_account, ["token", "--password", credentials["password"],],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_account, ["token", "--password", "test",],)
        assert result.exit_code > 0
        assert result.exception
        assert "Invalid user password" in str(result.exception)

    finally:
        clirunner.invoke(cmd_account, ["logout"])


def test_account_token(clirunner, credentials, validate_cliresult, isolated_pio_home):
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account, ["token", "--password", credentials["password"],],
        )
        validate_cliresult(result)
        assert "Personal Authentication Token:" in result.output
        token = result.output.strip().split(": ")[-1]

        result = clirunner.invoke(
            cmd_account,
            ["token", "--password", credentials["password"], "--json-output"],
        )
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result
        assert json_result.get("status") == "success"
        assert json_result.get("result") == token
        token = json_result.get("result")

        clirunner.invoke(cmd_account, ["logout"])

        result = clirunner.invoke(
            cmd_account, ["token", "--password", credentials["password"],],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        os.environ["PLATFORMIO_AUTH_TOKEN"] = token

        result = clirunner.invoke(
            cmd_account,
            ["token", "--password", credentials["password"], "--json-output"],
        )
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result
        assert json_result.get("status") == "success"
        assert json_result.get("result") == token

        os.environ.pop("PLATFORMIO_AUTH_TOKEN")

    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_token_with_refreshing(
    clirunner, credentials, validate_cliresult, isolated_pio_home
):
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            ["token", "--password", credentials["password"], "--json-output"],
        )
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result
        assert json_result.get("status") == "success"
        assert json_result.get("result")
        token = json_result.get("result")

        result = clirunner.invoke(
            cmd_account,
            [
                "token",
                "--password",
                credentials["password"],
                "--json-output",
                "--regenerate",
            ],
        )
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result
        assert json_result.get("status") == "success"
        assert json_result.get("result")
        assert token != json_result.get("result")
    finally:
        clirunner.invoke(cmd_account, ["logout"])


def test_account_summary(clirunner, credentials, validate_cliresult, isolated_pio_home):
    try:
        result = clirunner.invoke(cmd_account, ["show"],)
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_account, ["show"])
        validate_cliresult(result)
        assert credentials["login"] in result.output
        assert "Community" in result.output
        assert "100 Concurrent Remote Agents" in result.output

        result = clirunner.invoke(cmd_account, ["show", "--json-output"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result.get("user_id")
        assert json_result.get("profile")
        assert json_result.get("profile").get("username")
        assert json_result.get("profile").get("email")
        assert credentials["login"] == json_result.get("profile").get(
            "username"
        ) or credentials["login"] == json_result.get("profile").get("email")
        assert json_result.get("profile").get("firstname")
        assert json_result.get("profile").get("lastname")
        assert json_result.get("packages")
        assert json_result.get("packages")[0].get("name")
        assert json_result.get("packages")[0].get("path")
        assert json_result.get("subscriptions") is not None

        result = clirunner.invoke(cmd_account, ["show", "--json-output", "--offline"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert not json_result.get("user_id")
        assert json_result.get("profile")
        assert json_result.get("profile").get("username")
        assert json_result.get("profile").get("email")
        assert not json_result.get("packages")
        assert not json_result.get("subscriptions")
    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_profile_update_with_invalid_password(
    clirunner, credentials, validate_cliresult
):
    try:
        result = clirunner.invoke(
            cmd_account, ["update", "--current-password", credentials["password"]],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        firstname = "First " + str(int(time.time() * 1000))

        result = clirunner.invoke(
            cmd_account,
            ["update", "--current-password", "test", "--firstname", firstname],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "Invalid user password" in str(result.exception)
    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_profile_update_only_firstname_and_lastname(
    clirunner, credentials, validate_cliresult, isolated_pio_home
):
    try:
        result = clirunner.invoke(
            cmd_account, ["update", "--current-password", credentials["password"]],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        firstname = "First " + str(int(time.time() * 1000))
        lastname = "Last" + str(int(time.time() * 1000))

        result = clirunner.invoke(
            cmd_account,
            [
                "update",
                "--current-password",
                credentials["password"],
                "--firstname",
                firstname,
                "--lastname",
                lastname,
            ],
        )
        validate_cliresult(result)
        assert "Profile successfully updated!" in result.output

        result = clirunner.invoke(cmd_account, ["show", "--json-output"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result.get("profile").get("firstname") == firstname
        assert json_result.get("profile").get("lastname") == lastname

    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip_ci
def test_account_profile_update(
    clirunner, credentials, validate_cliresult, isolated_pio_home
):
    try:
        result = clirunner.invoke(
            cmd_account, ["update", "--current-password", credentials["password"]],
        )
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_account, ["show", "--json-output"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())

        firstname = "First " + str(int(time.time() * 1000))
        lastname = "Last" + str(int(time.time() * 1000))

        old_username = json_result.get("profile").get("username")
        new_username = "username" + str(int(time.time() * 1000))[-5:]

        result = clirunner.invoke(
            cmd_account,
            [
                "update",
                "--current-password",
                credentials["password"],
                "--firstname",
                firstname,
                "--lastname",
                lastname,
                "--username",
                new_username,
            ],
        )
        validate_cliresult(result)
        assert "Profile successfully updated!" in result.output
        assert "Please re-login." in result.output

        result = clirunner.invoke(cmd_account, ["show"],)
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authenticated! Please login to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account, ["login", "-u", new_username, "-p", credentials["password"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            [
                "update",
                "--current-password",
                credentials["password"],
                "--username",
                old_username,
            ],
        )
        validate_cliresult(result)
        assert "Profile successfully updated!" in result.output
        assert "Please re-login." in result.output

        result = clirunner.invoke(
            cmd_account, ["login", "-u", old_username, "-p", credentials["password"]],
        )
        validate_cliresult(result)
    finally:
        clirunner.invoke(cmd_account, ["logout"])

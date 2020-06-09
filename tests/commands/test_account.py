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
import requests

from platformio.commands.account import cli as cmd_account
from platformio.commands.package import cli as cmd_package
from platformio.downloader import FileDownloader
from platformio.unpacker import FileUnpacker


@pytest.mark.skipif(
    not os.environ.get("TEST_EMAIL_LOGIN"),
    reason="requires TEST_EMAIL_LOGIN, TEST_EMAIL_PASSWORD environ variables",
)  # pylint:disable=too-many-arguments
def test_account(
    clirunner, validate_cliresult, receive_email, isolated_pio_home, tmpdir_factory
):
    username = "test-piocore-%s" % str(int(time.time() * 1000))
    splited_email = os.environ.get("TEST_EMAIL_LOGIN").split("@")
    email = "%s+%s@%s" % (splited_email[0], username, splited_email[1])
    firstname = "Test"
    lastname = "User"
    password = "Qwerty123!"

    # pio account register
    result = clirunner.invoke(
        cmd_account,
        [
            "register",
            "-u",
            username,
            "-e",
            email,
            "-p",
            password,
            "--firstname",
            firstname,
            "--lastname",
            lastname,
        ],
    )
    validate_cliresult(result)

    # email verification
    result = receive_email(email)
    link = (
        result.split("Click on the link below to start this process.")[1]
        .split("This link will expire within 12 hours.")[0]
        .strip()
    )
    session = requests.Session()
    result = session.get(link).text
    link = result.split('<a href="')[1].split('"', 1)[0]
    link = link.replace("&amp;", "&")
    session.get(link)

    # pio account login
    result = clirunner.invoke(cmd_account, ["login", "-u", username, "-p", password],)
    validate_cliresult(result)
    try:
        # pio account summary
        result = clirunner.invoke(cmd_account, ["show", "--json-output", "--offline"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert not json_result.get("user_id")
        assert json_result.get("profile")
        assert json_result.get("profile").get("username")
        assert json_result.get("profile").get("email")
        assert not json_result.get("packages")
        assert not json_result.get("subscriptions")

        result = clirunner.invoke(cmd_account, ["show"])
        validate_cliresult(result)
        assert username in result.output
        # assert "100 Concurrent Remote Agents" in result.output

        result = clirunner.invoke(cmd_account, ["show", "--json-output"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result.get("user_id")
        assert json_result.get("profile")
        assert json_result.get("profile").get("username")
        assert json_result.get("profile").get("email")
        assert username == json_result.get("profile").get(
            "username"
        ) or username == json_result.get("profile").get("email")
        assert json_result.get("profile").get("firstname")
        assert json_result.get("profile").get("lastname")
        assert json_result.get("packages")
        assert json_result.get("packages")[0].get("name")
        assert json_result.get("packages")[0].get("path")
        assert json_result.get("subscriptions") is not None

        result = clirunner.invoke(cmd_account, ["show", "--json-output", "--offline"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result.get("user_id")
        assert json_result.get("profile")
        assert json_result.get("profile").get("username")
        assert json_result.get("profile").get("email")
        assert username == json_result.get("profile").get(
            "username"
        ) or username == json_result.get("profile").get("email")
        assert json_result.get("profile").get("firstname")
        assert json_result.get("profile").get("lastname")
        assert json_result.get("packages")
        assert json_result.get("packages")[0].get("name")
        assert json_result.get("packages")[0].get("path")
        assert json_result.get("subscriptions") is not None

        # pio account token
        result = clirunner.invoke(cmd_account, ["token", "--password", password,],)
        validate_cliresult(result)
        assert "Personal Authentication Token:" in result.output
        token = result.output.strip().split(": ")[-1]

        result = clirunner.invoke(
            cmd_account, ["token", "--password", password, "--json-output"],
        )
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result
        assert json_result.get("status") == "success"
        assert json_result.get("result") == token
        token = json_result.get("result")

        clirunner.invoke(cmd_account, ["logout"])

        result = clirunner.invoke(cmd_account, ["token", "--password", password,],)
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authorized! Please log in to PIO Account" in str(
            result.exception
        )

        os.environ["PLATFORMIO_AUTH_TOKEN"] = token

        result = clirunner.invoke(
            cmd_account, ["token", "--password", password, "--json-output"],
        )
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result
        assert json_result.get("status") == "success"
        assert json_result.get("result") == token

        os.environ.pop("PLATFORMIO_AUTH_TOKEN")

        result = clirunner.invoke(
            cmd_account, ["login", "-u", username, "-p", password],
        )
        validate_cliresult(result)

        # pio account password
        new_password = "Testpassword123"
        result = clirunner.invoke(
            cmd_account,
            ["password", "--old-password", password, "--new-password", new_password,],
        )
        validate_cliresult(result)
        assert "Password successfully changed!" in result.output

        clirunner.invoke(cmd_account, ["logout"])

        result = clirunner.invoke(
            cmd_account, ["login", "-u", username, "-p", new_password],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_account,
            ["password", "--old-password", new_password, "--new-password", password,],
        )
        validate_cliresult(result)

        # pio account update
        firstname = "First " + str(int(time.time() * 1000))
        lastname = "Last" + str(int(time.time() * 1000))

        new_username = "username" + str(int(time.time() * 1000))[-5:]
        new_email = "%s+new-%s@%s" % (splited_email[0], username, splited_email[1])
        result = clirunner.invoke(
            cmd_account,
            [
                "update",
                "--current-password",
                password,
                "--firstname",
                firstname,
                "--lastname",
                lastname,
                "--username",
                new_username,
                "--email",
                new_email,
            ],
        )
        validate_cliresult(result)
        assert "Profile successfully updated!" in result.output
        assert (
            "Please check your mail to verify your new email address and re-login. "
            in result.output
        )

        result = receive_email(new_email)
        link = (
            result.split("Click on the link below to start this process.")[1]
            .split("This link will expire within 12 hours.")[0]
            .strip()
        )
        session = requests.Session()
        result = session.get(link).text
        link = result.split('<a href="')[1].split('"', 1)[0]
        link = link.replace("&amp;", "&")
        session.get(link)

        result = clirunner.invoke(cmd_account, ["show"],)
        assert result.exit_code > 0
        assert result.exception
        assert "You are not authorized! Please log in to PIO Account" in str(
            result.exception
        )

        result = clirunner.invoke(
            cmd_account, ["login", "-u", new_username, "-p", password],
        )
        validate_cliresult(result)

        # pio account destroy with linked resource

        package_url = "https://github.com/bblanchon/ArduinoJson/archive/v6.11.0.tar.gz"

        tmp_dir = tmpdir_factory.mktemp("package")
        fd = FileDownloader(package_url, tmp_dir)
        pkg_dir = tmp_dir.mkdir("raw_package")
        fd.start(with_progress=False, silent=True)
        with FileUnpacker(fd.get_filepath()) as unpacker:
            unpacker.unpack(pkg_dir, with_progress=False, silent=True)

        result = clirunner.invoke(cmd_package, ["publish", str(pkg_dir)],)
        validate_cliresult(result)

        result = receive_email(new_email)
        assert "Congrats" in result
        assert "was published" in result

        result = clirunner.invoke(cmd_account, ["destroy"], "y")
        assert result.exit_code != 0
        assert (
            "We can not destroy the %s account due to 1 linked resources from registry"
            % username
        )

        result = clirunner.invoke(cmd_package, ["unpublish", "ArduinoJson"],)
        validate_cliresult(result)
    finally:
        result = clirunner.invoke(cmd_account, ["destroy"], "y")
        validate_cliresult(result)

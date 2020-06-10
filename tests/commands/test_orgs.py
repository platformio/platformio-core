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
import random

import pytest
import requests

from platformio.commands.account import cli as cmd_account
from platformio.commands.org import cli as cmd_org


@pytest.mark.skipif(
    not os.environ.get("TEST_EMAIL_LOGIN"),
    reason="requires TEST_EMAIL_LOGIN, TEST_EMAIL_PASSWORD environ variables",
)  # pylint:disable=too-many-arguments
def test_org(clirunner, validate_cliresult, receive_email, isolated_pio_home):
    username = "test-piocore-%s" % str(random.randint(0, 100000))
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

    orgname = "testorg-piocore-%s" % str(random.randint(0, 100000))
    display_name = "Test Org for PIO Core"
    second_username = "ivankravets"
    try:
        # pio org create
        result = clirunner.invoke(
            cmd_org,
            ["create", "--email", email, "--displayname", display_name, orgname],
        )
        validate_cliresult(result)

        # pio org list
        result = clirunner.invoke(cmd_org, ["list", "--json-output"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result == [
            {
                "orgname": orgname,
                "displayname": display_name,
                "email": email,
                "owners": [
                    {"username": username, "firstname": firstname, "lastname": lastname}
                ],
            }
        ]

        # pio org add (owner)
        result = clirunner.invoke(cmd_org, ["add", orgname, second_username])
        validate_cliresult(result)

        result = clirunner.invoke(cmd_org, ["list", "--json-output"])
        validate_cliresult(result)
        assert second_username in result.output

        # pio org remove (owner)
        result = clirunner.invoke(cmd_org, ["remove", orgname, second_username])
        validate_cliresult(result)

        result = clirunner.invoke(cmd_org, ["list", "--json-output"])
        validate_cliresult(result)
        assert second_username not in result.output

        # pio org update
        new_orgname = "neworg-piocore-%s" % str(random.randint(0, 100000))
        new_display_name = "Test Org for PIO Core"

        result = clirunner.invoke(
            cmd_org,
            [
                "update",
                orgname,
                "--new-orgname",
                new_orgname,
                "--displayname",
                new_display_name,
            ],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_org, ["list", "--json-output"])
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert json_result == [
            {
                "orgname": new_orgname,
                "displayname": new_display_name,
                "email": email,
                "owners": [
                    {"username": username, "firstname": firstname, "lastname": lastname}
                ],
            }
        ]

        result = clirunner.invoke(
            cmd_org,
            [
                "update",
                new_orgname,
                "--new-orgname",
                orgname,
                "--displayname",
                display_name,
            ],
        )
        validate_cliresult(result)
    finally:
        result = clirunner.invoke(cmd_org, ["destroy", orgname], "y")
        validate_cliresult(result)
        result = clirunner.invoke(cmd_account, ["destroy"], "y")
        validate_cliresult(result)

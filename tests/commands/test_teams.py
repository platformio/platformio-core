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
from platformio.commands.team import cli as cmd_team


@pytest.mark.skipif(
    not os.environ.get("TEST_EMAIL_LOGIN"),
    reason="requires TEST_EMAIL_LOGIN, TEST_EMAIL_PASSWORD environ variables",
)  # pylint:disable=too-many-arguments
def test_teams(clirunner, validate_cliresult, receive_email, isolated_pio_home):
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

    # pio org create
    result = clirunner.invoke(
        cmd_org, ["create", "--email", email, "--displayname", display_name, orgname]
    )
    validate_cliresult(result)

    teamname = "test-" + str(random.randint(0, 100000))
    team_description = "team for CI test"
    second_username = "ivankravets"
    try:
        # pio team create
        result = clirunner.invoke(
            cmd_team,
            [
                "create",
                "%s:%s" % (orgname, teamname),
                "--description",
                team_description,
            ],
        )
        validate_cliresult(result)

        # pio team list
        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        for item in json_result:
            del item["id"]
        assert json_result == [
            {"name": teamname, "description": team_description, "members": []}
        ]

        # pio team add (member)
        result = clirunner.invoke(
            cmd_team, ["add", "%s:%s" % (orgname, teamname), second_username],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        assert second_username in result.output

        # pio team remove (member)
        result = clirunner.invoke(
            cmd_team, ["remove", "%s:%s" % (orgname, teamname), second_username],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        assert second_username not in result.output

        # pio team update
        new_teamname = "new-" + str(random.randint(0, 100000))
        newteam_description = "Updated Description"
        result = clirunner.invoke(
            cmd_team,
            [
                "update",
                "%s:%s" % (orgname, teamname),
                "--name",
                new_teamname,
                "--description",
                newteam_description,
            ],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        for item in json_result:
            del item["id"]
        assert json_result == [
            {"name": new_teamname, "description": newteam_description, "members": []}
        ]

        result = clirunner.invoke(
            cmd_team,
            [
                "update",
                "%s:%s" % (orgname, new_teamname),
                "--name",
                teamname,
                "--description",
                team_description,
            ],
        )
        validate_cliresult(result)
    finally:
        result = clirunner.invoke(
            cmd_team, ["destroy", "%s:%s" % (orgname, teamname)], "y"
        )
        validate_cliresult(result)
        result = clirunner.invoke(cmd_org, ["destroy", orgname], "y")
        validate_cliresult(result)
        result = clirunner.invoke(cmd_account, ["destroy"], "y")
        validate_cliresult(result)

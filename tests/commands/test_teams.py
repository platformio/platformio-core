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

from platformio.commands.account import cli as cmd_account
from platformio.commands.org import cli as cmd_org
from platformio.commands.team import cli as cmd_team

pytestmark = pytest.mark.skipif(
    not (
        os.environ.get("PLATFORMIO_TEST_ACCOUNT_LOGIN")
        and os.environ.get("PLATFORMIO_TEST_ACCOUNT_PASSWORD")
    ),
    reason="requires PLATFORMIO_TEST_ACCOUNT_LOGIN, PLATFORMIO_TEST_ACCOUNT_PASSWORD environ variables",
)


@pytest.fixture(scope="session")
def credentials():
    return {
        "login": os.environ["PLATFORMIO_TEST_ACCOUNT_LOGIN"],
        "password": os.environ["PLATFORMIO_TEST_ACCOUNT_PASSWORD"],
    }


def test_teams(clirunner, credentials, validate_cliresult, isolated_pio_home):
    orgname = ""
    teamname = "test-" + str(int(time.time() * 1000))
    try:
        result = clirunner.invoke(
            cmd_account,
            ["login", "-u", credentials["login"], "-p", credentials["password"]],
        )
        validate_cliresult(result)
        assert "Successfully logged in!" in result.output

        result = clirunner.invoke(cmd_org, ["list", "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        if len(json_result) < 3:
            for i in range(3 - len(json_result)):
                result = clirunner.invoke(
                    cmd_org,
                    [
                        "create",
                        "%s-%s" % (i, credentials["login"]),
                        "--email",
                        "test@test.com",
                        "--display-name",
                        "TEST ORG %s" % i,
                    ],
                )
                validate_cliresult(result)
        result = clirunner.invoke(cmd_org, ["list", "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 3
        orgname = json_result[0].get("orgname")

        result = clirunner.invoke(
            cmd_team,
            [
                "create",
                "%s:%s" % (orgname, teamname),
                "--description",
                "team for CI test",
            ],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 1
        assert json_result[0]["id"]
        assert json_result[0]["name"] == teamname
        assert json_result[0]["description"] == "team for CI test"
        assert json_result[0]["members"] == []

        result = clirunner.invoke(
            cmd_team, ["add", "%s:%s" % (orgname, teamname), credentials["login"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 1
        assert json_result[0]["id"]
        assert json_result[0]["name"] == teamname
        assert json_result[0]["description"] == "team for CI test"
        assert json_result[0]["members"][0]["username"] == credentials["login"]

        result = clirunner.invoke(
            cmd_team, ["remove", "%s:%s" % (orgname, teamname), credentials["login"]],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 1
        assert json_result[0]["id"]
        assert json_result[0]["name"] == teamname
        assert json_result[0]["description"] == "team for CI test"
        assert json_result[0]["members"] == []

        result = clirunner.invoke(
            cmd_team,
            [
                "update",
                "%s:%s" % (orgname, teamname),
                "--description",
                "Updated Description",
            ],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_team, ["list", "%s" % orgname, "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 1
        assert json_result[0]["id"]
        assert json_result[0]["name"] == teamname
        assert json_result[0]["description"] == "Updated Description"
        assert json_result[0]["members"] == []
        validate_cliresult(result)
    finally:
        clirunner.invoke(
            cmd_team, ["destroy", "%s:%s" % (orgname, teamname),],
        )
        clirunner.invoke(cmd_account, ["logout"])

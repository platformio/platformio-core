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

import pytest

from platformio.commands.account import cli as cmd_account
from platformio.commands.org import cli as cmd_org

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


def test_orgs(clirunner, credentials, validate_cliresult, isolated_pio_home):
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
        check = False
        for org in json_result:
            assert "orgname" in org
            orgname = org["orgname"]
            assert "displayname" in org
            assert "email" in org
            assert "owners" in org
            for owner in org.get("owners"):
                assert "username" in owner
                check = owner["username"] == credentials["login"] if not check else True
                assert "firstname" in owner
                assert "lastname" in owner
        assert check

        result = clirunner.invoke(cmd_org, ["add", orgname, "ivankravets"],)
        validate_cliresult(result)

        result = clirunner.invoke(cmd_org, ["list", "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 3
        check = False
        for item in json_result:
            if item["orgname"] != orgname:
                continue
            for owner in item.get("owners"):
                check = owner["username"] == "ivankravets" if not check else True
        assert check

        result = clirunner.invoke(cmd_org, ["remove", orgname, "ivankravets"],)
        validate_cliresult(result)

        result = clirunner.invoke(cmd_org, ["list", "--json-output"],)
        validate_cliresult(result)
        json_result = json.loads(result.output.strip())
        assert len(json_result) >= 3
        check = False
        for item in json_result:
            if item["orgname"] != orgname:
                continue
            for owner in item.get("owners"):
                check = owner["username"] == "ivankravets" if not check else True
        assert not check
    finally:
        clirunner.invoke(cmd_account, ["logout"])


@pytest.mark.skip
def test_org_update(clirunner, credentials, validate_cliresult, isolated_pio_home):
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
        assert len(json_result) >= 3
        org = json_result[0]
        assert "orgname" in org
        assert "displayname" in org
        assert "email" in org
        assert "owners" in org

        old_orgname = org["orgname"]
        if len(old_orgname) > 10:
            new_orgname = "neworg" + org["orgname"][6:]

        result = clirunner.invoke(
            cmd_org, ["update", old_orgname, "--new-orgname", new_orgname],
        )
        validate_cliresult(result)

        result = clirunner.invoke(
            cmd_org, ["update", new_orgname, "--new-orgname", old_orgname],
        )
        validate_cliresult(result)

        result = clirunner.invoke(cmd_org, ["list", "--json-output"],)
        validate_cliresult(result)
        assert json.loads(result.output.strip()) == json_result
    finally:
        clirunner.invoke(cmd_account, ["logout"])

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

# pylint: disable=global-statement,unused-argument

import json
import os
import random

import pytest
import requests

from platformio.account.cli import cli as cmd_account
from platformio.account.org.cli import cli as cmd_org
from platformio.account.team.cli import cli as cmd_team

pytestmark = pytest.mark.skipif(
    not all(
        os.environ.get(name)
        for name in (
            "TEST_EMAIL_LOGIN",
            "TEST_EMAIL_PASSWORD",
            "TEST_EMAIL_IMAP_SERVER",
        )
    ),
    reason=(
        "requires TEST_EMAIL_LOGIN, TEST_EMAIL_PASSWORD, "
        "and TEST_EMAIL_IMAP_SERVER environment variables"
    ),
)

USER_NAME = "test-piocore-%s" % str(random.randint(0, 100000))
USER_EMAIL = os.environ.get("TEST_EMAIL_LOGIN", "").replace("@", f"+{USER_NAME}@")
USER_PASSWORD = f"Qwerty-{random.randint(0, 100000)}"
USER_FIRST_NAME = "FirstName"
USER_LAST_NAME = "LastName"

ORG_NAME = "testorg-piocore-%s" % str(random.randint(0, 100000))
ORG_DISPLAY_NAME = "Test Org for PIO Core"
EXISTING_OWNER = "piolabs"

TEAM_NAME = "test-" + str(random.randint(0, 100000))
TEAM_DESCRIPTION = "team for CI test"


def verify_account(email_contents):
    link = (
        email_contents.split("Click on the link below to start this process.")[1]
        .split("This link will expire within 12 hours.")[0]
        .strip()
    )
    with requests.Session() as session:
        result = session.get(link).text
        link = result.split('<a href="')[1].split('"', 1)[0]
        link = link.replace("&amp;", "&")
        session.get(link)
        session.close()


def test_account_register(
    clirunner, validate_cliresult, receive_email, isolated_pio_core
):
    result = clirunner.invoke(
        cmd_account,
        [
            "register",
            "-u",
            USER_NAME,
            "-e",
            USER_EMAIL,
            "-p",
            USER_PASSWORD,
            "--firstname",
            USER_FIRST_NAME,
            "--lastname",
            USER_LAST_NAME,
        ],
    )
    validate_cliresult(result)
    verify_account(receive_email(USER_EMAIL))


def test_account_login(
    clirunner,
    validate_cliresult,
    isolated_pio_core,
):
    result = clirunner.invoke(
        cmd_account,
        ["login", "-u", USER_NAME, "-p", USER_PASSWORD],
    )
    validate_cliresult(result)


def test_account_summary(
    clirunner,
    validate_cliresult,
    isolated_pio_core,
):
    result = clirunner.invoke(cmd_account, ["show", "--json-output", "--offline"])
    validate_cliresult(result)
    json_result = json.loads(result.output.strip())
    assert not json_result.get("user_id")
    assert json_result.get("profile")
    assert json_result.get("profile").get("username") == USER_NAME
    assert json_result.get("profile").get("email") == USER_EMAIL
    assert not json_result.get("packages")
    assert not json_result.get("subscriptions")

    result = clirunner.invoke(cmd_account, ["show"])
    validate_cliresult(result)
    assert USER_NAME in result.output
    # assert "100 Concurrent Remote Agents" in result.output

    result = clirunner.invoke(cmd_account, ["show", "--json-output"])
    validate_cliresult(result)
    json_result = json.loads(result.output.strip())
    assert json_result.get("user_id")
    assert json_result.get("profile")
    assert json_result.get("profile").get("username") == USER_NAME
    assert json_result.get("profile").get("email") == USER_EMAIL
    assert json_result.get("profile").get("firstname") == USER_FIRST_NAME
    assert json_result.get("profile").get("lastname") == USER_LAST_NAME
    assert json_result.get("packages")
    assert json_result.get("packages")[0].get("name")
    assert json_result.get("packages")[0].get("path")
    assert json_result.get("subscriptions") is not None


def test_account_token(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_account,
        [
            "token",
            "--password",
            USER_PASSWORD,
        ],
    )
    validate_cliresult(result)
    assert "Personal Authentication Token:" in result.output
    token = result.output.strip().split(": ")[-1]

    result = clirunner.invoke(
        cmd_account,
        ["token", "--password", USER_PASSWORD, "--json-output"],
    )
    validate_cliresult(result)
    json_result = json.loads(result.output.strip())
    assert json_result
    assert json_result.get("status") == "success"
    assert json_result.get("result") == token

    # logout
    result = clirunner.invoke(cmd_account, ["logout"])
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_account,
        [
            "token",
            "--password",
            USER_PASSWORD,
        ],
    )
    assert result.exit_code != 0
    assert result.exception
    assert "You are not authorized!" in str(result.exception)

    # use env tokem
    os.environ["PLATFORMIO_AUTH_TOKEN"] = token

    result = clirunner.invoke(
        cmd_account,
        ["show", "--json-output"],
    )
    validate_cliresult(result)
    json_result = json.loads(result.output.strip())
    assert json_result.get("user_id")
    assert json_result.get("profile").get("username") == USER_NAME
    assert json_result.get("profile").get("email") == USER_EMAIL

    os.environ.pop("PLATFORMIO_AUTH_TOKEN")

    result = clirunner.invoke(
        cmd_account,
        ["login", "-u", USER_NAME, "-p", USER_PASSWORD],
    )
    validate_cliresult(result)


def test_account_change_password(clirunner, validate_cliresult, isolated_pio_core):
    new_password = "Testpassword123"
    result = clirunner.invoke(
        cmd_account,
        [
            "password",
            "--old-password",
            USER_PASSWORD,
            "--new-password",
            new_password,
        ],
    )
    validate_cliresult(result)
    assert "Password successfully changed!" in result.output

    result = clirunner.invoke(cmd_account, ["logout"])
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_account,
        ["login", "-u", USER_NAME, "-p", new_password],
    )
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_account,
        [
            "password",
            "--old-password",
            new_password,
            "--new-password",
            USER_PASSWORD,
        ],
    )
    validate_cliresult(result)


def test_account_update(
    clirunner, validate_cliresult, receive_email, isolated_pio_core
):
    global USER_NAME, USER_EMAIL, USER_FIRST_NAME, USER_LAST_NAME

    USER_NAME = "test-piocore-%s" % str(random.randint(0, 100000))
    USER_EMAIL = os.environ.get("TEST_EMAIL_LOGIN", "").replace(
        "@", f"+new-{USER_NAME}@"
    )
    USER_FIRST_NAME = "First " + str(random.randint(0, 100000))
    USER_LAST_NAME = "Last" + str(random.randint(0, 100000))

    result = clirunner.invoke(
        cmd_account,
        [
            "update",
            "--current-password",
            USER_PASSWORD,
            "--firstname",
            USER_FIRST_NAME,
            "--lastname",
            USER_LAST_NAME,
            "--username",
            USER_NAME,
            "--email",
            USER_EMAIL,
        ],
    )
    validate_cliresult(result)
    assert "Profile successfully updated!" in result.output
    assert (
        "Please check your mail to verify your new email address and re-login. "
        in result.output
    )
    verify_account(receive_email(USER_EMAIL))

    result = clirunner.invoke(
        cmd_account,
        ["show"],
    )
    assert result.exit_code > 0
    assert result.exception
    assert "You are not authorized!" in str(result.exception)

    result = clirunner.invoke(
        cmd_account,
        ["login", "-u", USER_NAME, "-p", USER_PASSWORD],
    )
    validate_cliresult(result)


# def _test_account_destroy_with_linked_resources(
#     clirunner, validate_cliresult, receive_email, isolated_pio_core, tmpdir_factory
# ):
#     package_url = "https://github.com/bblanchon/ArduinoJson/archive/v6.11.0.tar.gz"
#
#     tmp_dir = tmpdir_factory.mktemp("package")
#     fd = FileDownloader(package_url, str(tmp_dir))
#     pkg_dir = tmp_dir.mkdir("raw_package")
#     fd.start(with_progress=False, silent=True)
#     with FileUnpacker(fd.get_filepath()) as unpacker:
#         unpacker.unpack(str(pkg_dir), with_progress=False, silent=True)
#
#     result = clirunner.invoke(cmd_package, ["publish", str(pkg_dir)],)
#     validate_cliresult(result)
#     try:
#         result = receive_email(email)
#         assert "Congrats" in result
#         assert "was published" in result
#     except:  # pylint:disable=bare-except
#         pass
#
#     result = clirunner.invoke(cmd_account, ["destroy"], "y")
#     assert result.exit_code != 0
#     assert (
#         "We can not destroy the %s account due to 1 linked resources from registry"
#         % username
#     )
#
#     result = clirunner.invoke(cmd_package, ["unpublish", "ArduinoJson"],)
#     validate_cliresult(result)


def test_org_create(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_org,
        ["create", "--email", USER_EMAIL, "--displayname", ORG_DISPLAY_NAME, ORG_NAME],
    )
    validate_cliresult(result)


def test_org_list(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(cmd_org, ["list", "--json-output"])
    validate_cliresult(result)
    json_result = json.loads(result.output.strip())
    assert json_result == [
        {
            "orgname": ORG_NAME,
            "displayname": ORG_DISPLAY_NAME,
            "email": USER_EMAIL,
            "owners": [
                {
                    "username": USER_NAME,
                    "firstname": USER_FIRST_NAME,
                    "lastname": USER_LAST_NAME,
                }
            ],
        }
    ]


def test_org_add_owner(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(cmd_org, ["add", ORG_NAME, EXISTING_OWNER])
    validate_cliresult(result)

    result = clirunner.invoke(cmd_org, ["list", "--json-output"])
    validate_cliresult(result)
    assert EXISTING_OWNER in result.output


def test_org_remove_owner(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(cmd_org, ["remove", ORG_NAME, EXISTING_OWNER])
    validate_cliresult(result)

    result = clirunner.invoke(cmd_org, ["list", "--json-output"])
    validate_cliresult(result)
    assert EXISTING_OWNER not in result.output


def test_org_update(clirunner, validate_cliresult, isolated_pio_core):
    new_orgname = "neworg-piocore-%s" % str(random.randint(0, 100000))
    new_display_name = "Test Org for PIO Core"

    result = clirunner.invoke(
        cmd_org,
        [
            "update",
            ORG_NAME,
            "--orgname",
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
            "email": USER_EMAIL,
            "owners": [
                {
                    "username": USER_NAME,
                    "firstname": USER_FIRST_NAME,
                    "lastname": USER_LAST_NAME,
                }
            ],
        }
    ]

    result = clirunner.invoke(
        cmd_org,
        [
            "update",
            new_orgname,
            "--orgname",
            ORG_NAME,
            "--displayname",
            ORG_DISPLAY_NAME,
        ],
    )
    validate_cliresult(result)


def test_team_create(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_team,
        [
            "create",
            "%s:%s" % (ORG_NAME, TEAM_NAME),
            "--description",
            TEAM_DESCRIPTION,
        ],
    )
    validate_cliresult(result)


def test_team_list(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_team,
        ["list", "%s" % ORG_NAME, "--json-output"],
    )
    validate_cliresult(result)
    json_result = json.loads(result.output.strip())
    for item in json_result:
        del item["id"]
    assert json_result == [
        {"name": TEAM_NAME, "description": TEAM_DESCRIPTION, "members": []}
    ]


def _test_team_add_member(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_team,
        ["add", "%s:%s" % (ORG_NAME, TEAM_NAME), EXISTING_OWNER],
    )
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_team,
        ["list", "%s" % ORG_NAME, "--json-output"],
    )
    validate_cliresult(result)
    assert EXISTING_OWNER in result.output


def _test_team_remove(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cmd_team,
        ["remove", "%s:%s" % (ORG_NAME, TEAM_NAME), EXISTING_OWNER],
    )
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_team,
        ["list", "%s" % ORG_NAME, "--json-output"],
    )
    validate_cliresult(result)
    assert EXISTING_OWNER not in result.output


def _test_team_update(clirunner, validate_cliresult, receive_email, isolated_pio_core):
    new_teamname = "new-" + str(random.randint(0, 100000))
    newteam_description = "Updated Description"
    result = clirunner.invoke(
        cmd_team,
        [
            "update",
            "%s:%s" % (ORG_NAME, TEAM_NAME),
            "--name",
            new_teamname,
            "--description",
            newteam_description,
        ],
    )
    validate_cliresult(result)

    result = clirunner.invoke(
        cmd_team,
        ["list", "%s" % ORG_NAME, "--json-output"],
    )
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
            "%s:%s" % (ORG_NAME, new_teamname),
            "--name",
            TEAM_NAME,
            "--description",
            TEAM_DESCRIPTION,
        ],
    )
    validate_cliresult(result)


def test_cleanup(clirunner, validate_cliresult, receive_email, isolated_pio_core):
    result = clirunner.invoke(
        cmd_team, ["destroy", "%s:%s" % (ORG_NAME, TEAM_NAME)], "y"
    )
    validate_cliresult(result)
    result = clirunner.invoke(cmd_org, ["destroy", ORG_NAME], "y")
    validate_cliresult(result)
    result = clirunner.invoke(cmd_account, ["destroy"], "y")
    validate_cliresult(result)

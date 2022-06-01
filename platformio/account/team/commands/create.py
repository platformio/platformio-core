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

import click

from platformio.account.client import AccountClient
from platformio.account.validate import validate_orgname_teamname


@click.command("create", short_help="Create a new team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(
        value, teamname_validate=True
    ),
)
@click.option(
    "--description",
)
def team_create_cmd(orgname_teamname, description):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    client.create_team(orgname, teamname, description)
    return click.secho(
        "The team %s has been successfully created." % teamname,
        fg="green",
    )

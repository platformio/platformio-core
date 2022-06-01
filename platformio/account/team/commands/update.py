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
from platformio.account.validate import validate_orgname_teamname, validate_teamname


@click.command("update", short_help="Update team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
@click.option(
    "--name",
    callback=lambda _, __, value: validate_teamname(value),
    help="A new team name",
)
@click.option(
    "--description",
)
def team_update_cmd(orgname_teamname, **kwargs):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    team = client.get_team(orgname, teamname)
    del team["id"]
    del team["members"]
    new_team = team.copy()
    if not any(kwargs.values()):
        for field in team:
            new_team[field] = click.prompt(
                field.replace("_", " ").capitalize(), default=team[field]
            )
            if field == "name":
                validate_teamname(new_team[field])
    else:
        new_team.update({key: value for key, value in kwargs.items() if value})
    client.update_team(orgname, teamname, new_team)
    return click.secho(
        "The team %s has been successfully updated." % teamname,
        fg="green",
    )

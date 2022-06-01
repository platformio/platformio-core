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


@click.command("destroy", short_help="Destroy a team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
def team_destroy_cmd(orgname_teamname):
    orgname, teamname = orgname_teamname.split(":", 1)
    click.confirm(
        click.style(
            "Are you sure you want to destroy the %s team?" % teamname, fg="yellow"
        ),
        abort=True,
    )
    client = AccountClient()
    client.destroy_team(orgname, teamname)
    return click.secho(
        "The team %s has been successfully destroyed." % teamname,
        fg="green",
    )

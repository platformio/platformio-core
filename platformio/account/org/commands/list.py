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

import click
from tabulate import tabulate

from platformio.account.client import AccountClient


@click.command("list", short_help="List organizations and their members")
@click.option("--json-output", is_flag=True)
def org_list_cmd(json_output):
    client = AccountClient()
    orgs = client.list_orgs()
    if json_output:
        return click.echo(json.dumps(orgs))
    if not orgs:
        return click.echo("You do not have any organization")
    for org in orgs:
        click.echo()
        click.secho(org.get("orgname"), fg="cyan")
        click.echo("-" * len(org.get("orgname")))
        data = []
        if org.get("displayname"):
            data.append(("Display Name:", org.get("displayname")))
        if org.get("email"):
            data.append(("Email:", org.get("email")))
        data.append(
            (
                "Owners:",
                ", ".join((owner.get("username") for owner in org.get("owners"))),
            )
        )
        click.echo(tabulate(data, tablefmt="plain"))
    return click.echo()

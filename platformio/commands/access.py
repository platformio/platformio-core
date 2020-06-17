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

# pylint: disable=unused-argument

import json
import re

import click
from tabulate import tabulate

from platformio.clients.registry import RegistryClient
from platformio.commands.account import validate_username
from platformio.commands.team import validate_orgname_teamname


def validate_client(value):
    if ":" in value:
        validate_orgname_teamname(value)
    else:
        validate_username(value)
    return value


@click.group("access", short_help="Manage Resource Access")
def cli():
    pass


def validate_prn(value):
    value = str(value).strip()
    if not re.match(r"^reg:pkg:(\d+):(\w+)$", value, flags=re.I):
        raise click.BadParameter("Invalid PRN format.")
    return value


@cli.command("public", short_help="Make resource public")
@click.argument(
    "prn", callback=lambda _, __, value: validate_prn(value),
)
@click.option("--prn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_public(prn, prn_type):
    client = RegistryClient()
    client.update_resource(prn=prn, private=0)
    return click.secho(
        "The resource %s has been successfully updated." % prn, fg="green",
    )


@cli.command("private", short_help="Make resource private")
@click.argument(
    "prn", callback=lambda _, __, value: validate_prn(value),
)
@click.option("--prn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_private(prn, prn_type):
    client = RegistryClient()
    client.update_resource(prn=prn, private=1)
    return click.secho(
        "The resource %s has been successfully updated." % prn, fg="green",
    )


@cli.command("grant", short_help="Grant access")
@click.argument("level", type=click.Choice(["admin", "maintainer", "guest"]))
@click.argument(
    "client",
    metavar="[ORGNAME:TEAMNAME|USERNAME]",
    callback=lambda _, __, value: validate_client(value),
)
@click.argument(
    "prn", callback=lambda _, __, value: validate_prn(value),
)
@click.option("--prn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_grant(level, client, prn, prn_type):
    reg_client = RegistryClient()
    reg_client.grant_access_for_resource(prn=prn, client=client, level=level)
    return click.secho(
        "Access for resource %s has been granted for %s" % (prn, client), fg="green",
    )


@cli.command("revoke", short_help="Revoke access")
@click.argument(
    "client",
    metavar="[ORGNAME:TEAMNAME|USERNAME]",
    callback=lambda _, __, value: validate_client(value),
)
@click.argument(
    "prn", callback=lambda _, __, value: validate_prn(value),
)
@click.option("--prn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
def access_revoke(client, prn, prn_type):
    reg_client = RegistryClient()
    reg_client.revoke_access_from_resource(prn=prn, client=client)
    return click.secho(
        "Access for resource %s has been revoked for %s" % (prn, client), fg="green",
    )


@cli.command("list", short_help="List resources")
@click.argument("owner", required=False)
@click.option("--prn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
@click.option("--json-output", is_flag=True)
def access_list(owner, prn_type, json_output):
    reg_client = RegistryClient()
    resources = reg_client.list_resources(owner=owner)
    if json_output:
        return click.echo(json.dumps(resources))
    if not resources:
        return click.secho("You do not have any resources.", fg="yellow")
    for resource in resources:
        click.echo()
        click.secho(resource.get("name"), fg="cyan")
        click.echo("-" * len(resource.get("name")))
        table_data = []
        table_data.append(("PRN:", resource.get("prn")))
        table_data.append(("Owner:", resource.get("owner")))
        table_data.append(
            (
                "Access level(s):",
                ", ".join(
                    (level.capitalize() for level in resource.get("access_levels"))
                ),
            )
        )
        click.echo(tabulate(table_data, tablefmt="plain"))
    return click.echo()

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

from platformio.registry.client import RegistryClient


@click.command("list", short_help="List published resources")
@click.argument("owner", required=False)
@click.option("--urn-type", type=click.Choice(["prn:reg:pkg"]), default="prn:reg:pkg")
@click.option("--json-output", is_flag=True)
def access_list_cmd(owner, urn_type, json_output):  # pylint: disable=unused-argument
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
        table_data.append(("URN:", resource.get("urn")))
        table_data.append(("Owner:", resource.get("owner")))
        table_data.append(
            (
                "Access:",
                (
                    click.style("Private", fg="red")
                    if resource.get("private", False)
                    else "Public"
                ),
            )
        )
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

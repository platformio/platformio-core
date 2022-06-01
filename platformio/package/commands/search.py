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

import math

import click

from platformio import util
from platformio.registry.client import RegistryClient


@click.command("search", short_help="Search for packages")
@click.argument("query")
@click.option("-p", "--page", type=click.IntRange(min=1))
@click.option(
    "-s",
    "--sort",
    type=click.Choice(["relevance", "popularity", "trending", "added", "updated"]),
)
def package_search_cmd(query, page, sort):
    client = RegistryClient()
    result = client.list_packages(query, page=page, sort=sort)
    if not result["total"]:
        click.secho("Nothing has been found by your request", fg="yellow")
        click.echo(
            "Try a less-specific search or use truncation (or wildcard) operator *"
        )
        return
    print_search_result(result)


def print_search_result(result):
    click.echo(
        "Found %d packages (page %d of %d)"
        % (
            result["total"],
            result["page"],
            math.ceil(result["total"] / result["limit"]),
        )
    )
    for item in result["items"]:
        click.echo()
        print_search_item(item)


def print_search_item(item):
    click.echo(
        "%s/%s"
        % (
            click.style(item["owner"]["username"], fg="cyan"),
            click.style(item["name"], fg="cyan", bold=True),
        )
    )
    click.echo(
        "%s • %s • Published on %s"
        % (
            item["type"].capitalize()
            if item["tier"] == "community"
            else click.style(
                ("%s %s" % (item["tier"], item["type"])).title(), bold=True
            ),
            item["version"]["name"],
            util.parse_datetime(item["version"]["released_at"]).strftime("%c"),
        )
    )
    click.echo(item["description"])

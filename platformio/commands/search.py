# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

import click

from platformio.platforms.base import PlatformFactory


@click.command("search", short_help="Search for development platforms")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def cli(query, json_output):

    data = []
    platforms = PlatformFactory.get_platforms().keys()
    platforms.sort()
    for platform in platforms:
        p = PlatformFactory.newPlatform(platform)
        name = p.get_name()
        description = p.get_description()

        if query == "all":
            query = ""

        search_data = "%s %s %s" % (name, description, p.get_packages())
        if query and query.lower() not in search_data.lower():
            continue

        data.append({
            "name": name,
            "description": description,
            "packages": p.get_packages()
        })

    if json_output:
        click.echo(json.dumps(data))
    else:
        for item in data:
            click.secho(item['name'], fg="cyan", nl=False)
            click.echo(" (available packages: %s)" % ", ".join(
                p.get_packages().keys()))
            click.secho("-" * len(item['name']), fg="cyan")
            click.echo(item['description'])
            click.echo()

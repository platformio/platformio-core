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
        type_ = p.get_type()
        description = p.get_description()

        if query == "all":
            query = ""

        search_data = "%s %s %s" % (type_, description, p.get_packages())
        if query and query.lower() not in search_data.lower():
            continue

        data.append({
            "type": type_,
            "description": description,
            "packages": p.get_packages()
        })

    if json_output:
        click.echo(json.dumps(data))
    else:
        for item in data:
            click.secho(item['type'], fg="cyan", nl=False)
            click.echo(" (available packages: %s)" % ", ".join(
                p.get_packages().keys()))
            click.secho("-" * len(item['type']), fg="cyan")
            click.echo(item['description'])
            click.echo()

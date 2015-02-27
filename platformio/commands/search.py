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
        info = p.get_short_info()

        if query == "all":
            query = ""

        search_data = "%s %s" % (name, info)
        if query and query.lower() not in search_data.lower():
            continue

        data.append({
            "name": name,
            "info": info
        })

    if json_output:
        click.echo(json.dumps(data))
    else:
        for item in data:
            click.echo("{name:<20} - {info}".format(
                name=click.style(item['name'], fg="cyan"), info=item['info']))

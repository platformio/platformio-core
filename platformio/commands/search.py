# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.platforms.base import PlatformFactory


@click.command("search", short_help="Search for development platforms")
@click.argument("query", required=False)
def cli(query):
    for platform in PlatformFactory.get_platforms().keys():
        p = PlatformFactory.newPlatform(platform)
        name = p.get_name()
        shinfo = p.get_short_info()

        if query == "all":
            query = ""

        search_data = "%s %s" % (name, shinfo)
        if query and query.lower() not in search_data.lower():
            continue

        click.echo("{name:<20} - {info}".format(
            name=click.style(name, fg="cyan"), info=shinfo))

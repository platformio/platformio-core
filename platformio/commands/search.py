# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import argument, command, echo, style

from platformio.platforms.base import PlatformFactory
from platformio.util import get_platforms


@command("search", short_help="Search for development platforms")
@argument("query")
def cli(query):
    for platform in get_platforms():
        p = PlatformFactory().newPlatform(platform)
        name = p.get_name()
        shinfo = p.get_short_info()

        search_data = "%s %s" % (name, shinfo)
        if query != "all" and query.lower() not in search_data.lower():
            continue

        echo("{name:<20} - {info}".format(name=style(name, fg="cyan"),
                                          info=shinfo))

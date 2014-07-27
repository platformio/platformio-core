# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, secho

from platformio.util import get_serialports


@command("serialports", short_help="List Serial ports")
def cli():

    for item in get_serialports():
        secho(item['port'], fg="cyan")
        echo("----------")
        echo("Hardware ID: %s" % item['hwid'])
        echo("Description: %s" % item['description'])
        echo("")

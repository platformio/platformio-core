# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.platforms.base import PlatformFactory


@click.command("uninstall", short_help="Uninstall platforms")
@click.argument("platforms", nargs=-1)
def cli(platforms):

    for platform in platforms:
        p = PlatformFactory.newPlatform(platform)
        if p.uninstall():
            click.secho("The platform '%s' has been successfully "
                        "uninstalled!" % platform, fg="green")

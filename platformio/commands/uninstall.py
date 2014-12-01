# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import argument, command, secho

from platformio.platforms.base import PlatformFactory


@command("uninstall", short_help="Uninstall platforms")
@argument("platforms", nargs=-1)
def cli(platforms):

    for platform in platforms:
        p = PlatformFactory().newPlatform(platform)
        if p.uninstall():
            secho("The platform '%s' has been successfully "
                  "uninstalled!" % platform, fg="green")

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, style

from platformio.platforms.base import PlatformFactory


@command("update", short_help="Update installed platforms")
def cli():

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    sorted(installed_platforms)

    for platform in installed_platforms:
        echo("\nPlatform %s" % style(platform, fg="cyan"))
        echo("--------")
        p = PlatformFactory().newPlatform(platform)
        p.update()

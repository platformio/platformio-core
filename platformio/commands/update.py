# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.platforms.base import PlatformFactory


@click.command("update", short_help="Update installed platforms")
def cli():

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    installed_platforms.sort()

    for platform in installed_platforms:
        click.echo("\nPlatform %s" % click.style(platform, fg="cyan"))
        click.echo("--------")
        p = PlatformFactory.newPlatform(platform)
        p.update()

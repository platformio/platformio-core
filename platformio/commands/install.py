# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.platforms.base import PlatformFactory


@click.command("install", short_help="Install new platforms")
@click.argument("platforms", nargs=-1)
@click.option("--with-package", multiple=True, metavar="<package>")
@click.option("--without-package", multiple=True, metavar="<package>")
@click.option("--skip-default-package", is_flag=True)
def cli(platforms, with_package, without_package, skip_default_package):

    for platform in platforms:
        p = PlatformFactory.newPlatform(platform)
        if p.install(with_package, without_package, skip_default_package):
            click.secho("The platform '%s' has been successfully installed!" %
                        platform, fg="green")

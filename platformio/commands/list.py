# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, style

from platformio.platforms.base import PlatformFactory


@command("list", short_help="List installed platforms")
def cli():

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    installed_platforms = sorted(installed_platforms)

    for platform in installed_platforms:
        p = PlatformFactory().newPlatform(platform)
        echo("{name:<20} with packages: {pkgs}".format(
            name=style(p.get_name(), fg="cyan"),
            pkgs=", ".join(p.get_installed_packages())
        ))

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import command, echo, style

from platformio.pkgmanager import PackageManager
from platformio.platforms.base import PlatformFactory


@command("update", short_help="Update installed platforms")
def cli():

    for platform in PackageManager.get_installed().keys():
        echo("\nPlatform %s" % style(platform, fg="cyan"))
        echo("--------")
        p = PlatformFactory().newPlatform(platform)
        p.update()

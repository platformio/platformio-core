# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import join

from click import argument, command, echo, style

from platformio.exception import PlatformNotInstalledYet
from platformio.pkgmanager import PackageManager
from platformio.platforms.base import PlatformFactory


@command("show", short_help="Show details about an installed platforms")
@argument("platform")
def cli(platform):
    p = PlatformFactory().newPlatform(platform)
    if platform not in PackageManager.get_installed():
        raise PlatformNotInstalledYet(platform)

    # print info about platform
    echo("{name:<20} - {info}".format(name=style(p.get_name(), fg="cyan"),
                                      info=p.get_short_info()))

    pm = PackageManager(platform)
    for name, data in pm.get_installed(platform).items():
        echo("----------")
        echo("Package: %s" % style(name, fg="yellow"))
        echo("Location: %s" % join(pm.get_platform_dir(), data['path']))
        echo("Version: %d" % int(data['version']))

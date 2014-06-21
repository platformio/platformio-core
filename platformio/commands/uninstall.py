# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import argument, command, secho

from platformio.exception import PlatformNotInstalledYet
from platformio.pkgmanager import PackageManager
from platformio.platforms._base import PlatformFactory


@command("uninstall", short_help="Uninstall the platforms")
@argument("platforms", nargs=-1)
def cli(platforms):

    for platform in platforms:

        if platform not in PackageManager.get_installed():
            raise PlatformNotInstalledYet(platform)

        p = PlatformFactory().newPlatform(platform)
        if p.uninstall():
            secho("The platform '%s' has been successfully "
                  "uninstalled!" % platform, fg="green")

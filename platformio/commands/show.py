# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from datetime import datetime

from click import argument, command, echo, style

from platformio.exception import PlatformNotInstalledYet
from platformio.pkgmanager import PackageManager
from platformio.platforms.base import PlatformFactory


@command("show", short_help="Show details about installed platforms")
@argument("platform")
def cli(platform):

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()

    if platform not in installed_platforms:
        if click.confirm("The platform '%s' has not been installed yet. "
                         "Would you like to install it now?" % platform):
            ctx.invoke(cmd_install, platforms=[platform])
        else:
            raise PlatformNotInstalledYet(platform)

    p = PlatformFactory().newPlatform(platform)
    echo("{name:<20} - {info}".format(name=style(p.get_name(), fg="cyan"),
                                      info=p.get_short_info()))

    installed_packages = PackageManager.get_installed()
    for name in p.get_installed_packages():
        data = installed_packages[name]
        pkgalias = p.get_pkg_alias(name)
        echo("----------")
        echo("Package: %s" % style(name, fg="yellow"))
        if pkgalias:
            echo("Alias: %s" % pkgalias)
        echo("Version: %d" % int(data['version']))
        echo("Installed: %s" % datetime.fromtimestamp(
            data['time']).strftime("%Y-%m-%d %H:%M:%S"))

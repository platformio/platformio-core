# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import argument, command, option, secho

from platformio.platforms.base import PlatformFactory


@command("run", short_help="Install new platforms")
@argument("platform")
@option('--with-package', multiple=True, metavar="<package>")
@option('--without-package', multiple=True, metavar="<package>")
def cli(platform, with_package, without_package):

    p = PlatformFactory().newPlatform(platform)

    if p.install(with_package, without_package):
        secho("The platform '%s' has been successfully installed!" % platform,
              fg="green")

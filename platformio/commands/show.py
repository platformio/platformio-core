# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from datetime import datetime

import click

from platformio import app
from platformio.commands.install import cli as cmd_install
from platformio.exception import PlatformNotInstalledYet
from platformio.pkgmanager import PackageManager
from platformio.platforms.base import PlatformFactory


@click.command("show", short_help="Show details about installed platform")
@click.argument("platform")
@click.pass_context
def cli(ctx, platform):

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()

    if platform not in installed_platforms:
        if (not app.get_setting("enable_prompts") or
                click.confirm("The platform '%s' has not been installed yet. "
                              "Would you like to install it now?" % platform)):
            ctx.invoke(cmd_install, platforms=[platform])
        else:
            raise PlatformNotInstalledYet(platform)

    p = PlatformFactory.newPlatform(platform)
    click.echo("{name:<20} - {description} [ {url} ]".format(
        name=click.style(p.get_type(), fg="cyan"),
        description=p.get_description(), url=p.get_vendor_url()))

    installed_packages = PackageManager.get_installed()
    for name in p.get_installed_packages():
        data = installed_packages[name]
        pkgalias = p.get_pkg_alias(name)
        click.echo("----------")
        click.echo("Package: %s" % click.style(name, fg="yellow"))
        if pkgalias:
            click.echo("Alias: %s" % pkgalias)
        click.echo("Version: %d" % int(data['version']))
        click.echo("Installed: %s" % datetime.fromtimestamp(
            data['time']).strftime("%Y-%m-%d %H:%M:%S"))

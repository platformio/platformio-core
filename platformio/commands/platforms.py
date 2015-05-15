# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from datetime import datetime

import click

from platformio import app
from platformio.exception import PlatformNotInstalledYet
from platformio.pkgmanager import PackageManager
from platformio.platforms.base import PlatformFactory


@click.group(short_help="Platforms and Packages Manager")
def cli():
    pass


@cli.command("install", short_help="Install new platforms")
@click.argument("platforms", nargs=-1, required=True)
@click.option("--with-package", multiple=True, metavar="<package>")
@click.option("--without-package", multiple=True, metavar="<package>")
@click.option("--skip-default-package", is_flag=True)
def platforms_install(platforms, with_package, without_package,
                      skip_default_package):
    for platform in platforms:
        p = PlatformFactory.newPlatform(platform)
        if p.install(with_package, without_package, skip_default_package):
            click.secho("The platform '%s' has been successfully installed!" %
                        platform, fg="green")


@cli.command("list", short_help="List installed platforms")
@click.option("--json-output", is_flag=True)
def platforms_list(json_output):

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    installed_platforms.sort()

    data = []
    for platform in installed_platforms:
        p = PlatformFactory.newPlatform(platform)
        data.append({
            "name": platform,
            "packages": p.get_installed_packages()
        })

    if json_output:
        click.echo(json.dumps(data))
    else:
        for item in data:
            click.echo("{name:<20} with packages: {pkgs}".format(
                name=click.style(item['name'], fg="cyan"),
                pkgs=", ".join(item['packages'])
            ))


@cli.command("search", short_help="Search for development platforms")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def platforms_search(query, json_output):

    data = []
    platforms = PlatformFactory.get_platforms().keys()
    platforms.sort()
    for platform in platforms:
        p = PlatformFactory.newPlatform(platform)
        type_ = p.get_type()
        description = p.get_description()

        if query == "all":
            query = ""

        search_data = "%s %s %s" % (type_, description, p.get_packages())
        if query and query.lower() not in search_data.lower():
            continue

        data.append({
            "type": type_,
            "description": description,
            "packages": p.get_packages()
        })

    if json_output:
        click.echo(json.dumps(data))
    else:
        terminal_width, _ = click.get_terminal_size()
        for item in data:
            click.secho(item['type'], fg="cyan", nl=False)
            click.echo(" (available packages: %s)" % ", ".join(
                item.get("packages").keys()))
            click.echo("-" * terminal_width)
            click.echo(item['description'])
            click.echo()


@cli.command("show", short_help="Show details about installed platform")
@click.argument("platform")
@click.pass_context
def platforms_show(ctx, platform):

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()

    if platform not in installed_platforms:
        if (not app.get_setting("enable_prompts") or
                click.confirm("The platform '%s' has not been installed yet. "
                              "Would you like to install it now?" % platform)):
            ctx.invoke(platforms_install, platforms=[platform])
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


@cli.command("uninstall", short_help="Uninstall platforms")
@click.argument("platforms", nargs=-1, required=True)
def platforms_uninstall(platforms):

    for platform in platforms:
        p = PlatformFactory.newPlatform(platform)
        if p.uninstall():
            click.secho("The platform '%s' has been successfully "
                        "uninstalled!" % platform, fg="green")


@cli.command("update", short_help="Update installed Platforms and Packages")
def platforms_update():

    installed_platforms = PlatformFactory.get_platforms(
        installed=True).keys()
    installed_platforms.sort()

    for platform in installed_platforms:
        click.echo("\nPlatform %s" % click.style(platform, fg="cyan"))
        click.echo("--------")
        p = PlatformFactory.newPlatform(platform)
        p.update()

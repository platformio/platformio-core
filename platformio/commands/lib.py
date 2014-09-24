# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.exception import LibAlreadyInstalledError
from platformio.libmanager import LibraryManager
from platformio.util import get_api_result, get_lib_dir


@click.group(short_help="Library Manager")
def cli():
    pass


@cli.command("search", short_help="Search for library")
@click.option("-a", "--author", multiple=True)
@click.option("-k", "--keyword", multiple=True)
@click.argument("query")
def lib_search(query, author, keyword):
    for key, values in dict(author=author, keyword=keyword).iteritems():
        for value in values:
            query += ' %s:"%s"' % (key, value)

    result = get_api_result("/lib/search", dict(query=query))
    click.secho("Found %d libraries:" % result['total'],
                fg="green" if result['total'] else "yellow")

    while True:
        for item in result['items']:
            click.echo("{name:<30} {description}".format(
                name=click.style(item['name'], fg="cyan"),
                description=item['description']
            ))

        if int(result['page'])*int(result['perpage']) >= int(result['total']):
            break

        if click.confirm("Show next libraries?"):
            result = get_api_result(
                "/lib/search",
                dict(query=query, page=str(int(result['page']) + 1))
            )
        else:
            break


@cli.command("install", short_help="Install library")
@click.argument("names", nargs=-1)
@click.option("-v", "--version")
def lib_install_cli(names, version):
    lib_install(names, version)


def lib_install(names, version=None):
    lm = LibraryManager(get_lib_dir())
    for name in names:
        click.echo("Installing %s library:" % click.style(name, fg="cyan"))
        try:
            if lm.install(name, version):
                click.secho(
                    "The library '%s' has been successfully installed!" %
                    name, fg="green")
                info = lm.get_info(name)
                if "dependencies" in info:
                    click.secho("Installing dependencies:", fg="yellow")
                    lib_install(info['dependencies'])

        except LibAlreadyInstalledError:
            click.secho("Already installed", fg="yellow")


@cli.command("uninstall", short_help="Uninstall libraries")
@click.argument("names", nargs=-1)
def lib_uninstall_cli(names):
    lib_uninstall(names)


def lib_uninstall_dependency(dependency):
    lm = LibraryManager(get_lib_dir())

    for name in lm.get_installed():
        info = lm.get_info(name)
        if dependency in info.get("dependencies", []):
            return

    lib_uninstall([dependency])


def lib_uninstall(names):
    lm = LibraryManager(get_lib_dir())
    for name in names:
        info = lm.get_info(name)
        if lm.uninstall(name):
            # find dependencies
            if "dependencies" in info:
                for d in info['dependencies']:
                    lib_uninstall_dependency(d)

            click.secho("The library '%s' has been successfully "
                        "uninstalled!" % name, fg="green")


@cli.command("list", short_help="List installed libraries")
def lib_list():
    lm = LibraryManager(get_lib_dir())
    for name in lm.get_installed():
        info = lm.get_info(name)
        click.echo("{name:<30} {description}".format(
            name=click.style(info['name'], fg="cyan"),
            description=info['description']
        ))


@cli.command("show", short_help="Show details about installed libraries")
@click.argument("name")
def lib_show(name):
    lm = LibraryManager(get_lib_dir())
    info = lm.get_info(name)
    click.secho(info['name'], fg="cyan")
    click.echo("-" * len(info['name']))

    if "author" in info:
        _data = []
        for k in ("name", "email"):
            if k in info['author'] and info['author'][k] is not None:
                _value = info['author'][k]
                if k == "email":
                    _value = "<%s>" % _value
                _data.append(_value)
        click.echo("Author: %s" % " ".join(_data))

    click.echo("Keywords: %s" % info['keywords'])
    click.echo("Version: %s" % info['version'])
    click.echo()
    click.echo(info['description'])
    click.echo()


@cli.command("update", short_help="Update installed libraries")
def lib_update():
    lm = LibraryManager(get_lib_dir())
    lib_names = lm.get_installed()
    versions = get_api_result("/lib/version/" + ",".join(lib_names))

    for name in lib_names:
        info = lm.get_info(name)

        click.echo("Updating %s library:" % click.style(name, fg="yellow"))

        current_version = info['version']
        latest_version = versions[name]

        click.echo("Versions: Current=%s, Latest=%s \t " % (
            current_version, latest_version), nl=False)

        if current_version == latest_version:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
            continue
        else:
            click.echo("[%s]" % (click.style("Out-of-date", fg="red")))

        lib_uninstall([name])
        lib_install([name])


@cli.command("register", short_help="Register new library")
@click.argument("config_url")
def lib_register(config_url):
    result = get_api_result("/lib/register", data=dict(config_url=config_url))
    if "message" in result and result['message']:
        click.secho(result['message'], fg="green" if "successed" in result and
                    result['successed'] else "red")

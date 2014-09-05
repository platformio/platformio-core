# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from urllib import quote

from click import argument, echo, group, option, secho, style

from platformio.exception import LibAlreadyInstalledError
from platformio.libmanager import LibraryManager
from platformio.util import get_api_result, get_lib_dir


@group(short_help="Library Manager")
def cli():
    pass


@cli.command("search", short_help="Search for library")
@argument("query")
def lib_search(query):
    result = get_api_result("/lib/search", dict(query=quote(query)))
    secho("Found %d libraries:" % result['total'],
          fg="green" if result['total'] else "yellow")
    for item in result['items']:
        echo("{name:<30} {description}".format(
            name=style(item['name'], fg="cyan"),
            description=item['description']
        ))


@cli.command("install", short_help="Install library")
@argument("names", nargs=-1)
@option("-v", "--version")
def lib_install_cli(names, version):
    lib_install(names, version)


def lib_install(names, version=None):
    lm = LibraryManager(get_lib_dir())
    for name in names:
        echo("Installing %s library:" % style(name, fg="cyan"))
        try:
            if lm.install(name, version):
                secho("The library '%s' has been successfully installed!" %
                      name, fg="green")
        except LibAlreadyInstalledError:
            secho("Already installed", fg="yellow")


@cli.command("uninstall", short_help="Uninstall libraries")
@argument("names", nargs=-1)
def lib_uninstall_cli(names):
    lib_uninstall(names)


def lib_uninstall(names):
    lm = LibraryManager(get_lib_dir())
    for name in names:
        if lm.uninstall(name):
            secho("The library '%s' has been successfully "
                  "uninstalled!" % name, fg="green")


@cli.command("list", short_help="List installed libraries")
def lib_list():
    lm = LibraryManager(get_lib_dir())
    for name in lm.get_installed():
        info = lm.get_info(name)
        echo("{name:<30} {description}".format(
            name=style(info['name'], fg="cyan"),
            description=info['description']
        ))


@cli.command("show", short_help="Show details about installed libraries")
@argument("name")
def lib_show(name):
    lm = LibraryManager(get_lib_dir())
    info = lm.get_info(name)
    secho(info['name'], fg="cyan")
    echo("-" * len(info['name']))

    if "author" in info:
        _data = []
        for k in ("name", "email"):
            if k in info['author'] and info['author'][k] is not None:
                _value = info['author'][k]
                if k == "email":
                    _value = "<%s>" % _value
                _data.append(_value)
        echo("Author: %s" % " ".join(_data))

    echo("Keywords: %s" % info['keywords'])
    echo("Version: %s" % info['version'])
    echo()
    echo(info['description'])
    echo()


@cli.command("update", short_help="Update installed libraries")
def lib_update():
    lm = LibraryManager(get_lib_dir())
    lib_names = lm.get_installed()
    versions = get_api_result("/lib/version/" + ",".join(lib_names))

    for name in lib_names:
        info = lm.get_info(name)

        echo("Updating %s library:" % style(name, fg="yellow"))

        current_version = info['version']
        latest_version = versions[name]

        echo("Versions: Current=%s, Latest=%s \t " % (
            current_version, latest_version), nl=False)

        if current_version == latest_version:
            echo("[%s]" % (style("Up-to-date", fg="green")))
            continue
        else:
            echo("[%s]" % (style("Out-of-date", fg="red")))

        lib_uninstall([name])
        lib_install([name])

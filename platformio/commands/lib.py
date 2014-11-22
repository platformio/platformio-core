# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import click

from platformio.exception import (LibAlreadyInstalledError,
                                  LibInstallDependencyError)
from platformio.libmanager import LibraryManager
from platformio.util import get_api_result, get_lib_dir

LIBLIST_TPL = ("[{id:^14}] {name:<25} {compatibility:<30} "
               "\"{authornames}\": {description}")


def echo_liblist_header():
    click.echo(LIBLIST_TPL.format(
        id=click.style("ID", fg="green"),
        name=click.style("Name", fg="cyan"),
        compatibility=click.style("Compatibility", fg="yellow"),
        authornames="Authors",
        description="Description"
    ))
    click.echo("-" * 85)


def echo_liblist_item(item):
    click.echo(LIBLIST_TPL.format(
        id=click.style(str(item['id']), fg="green"),
        name=click.style(item['name'], fg="cyan"),
        compatibility=click.style(
            ", ".join(item['frameworks'] + item['platforms']),
            fg="yellow"
        ),
        authornames=", ".join(item['authornames']),
        description=item['description']
    ))


@click.group(short_help="Library Manager")
def cli():
    pass


@cli.command("search", short_help="Search for library")
@click.option("-a", "--author", multiple=True)
@click.option("-k", "--keyword", multiple=True)
@click.option("-f", "--framework", multiple=True)
@click.option("-p", "--platform", multiple=True)
@click.argument("query")
def lib_search(query, **filters):
    for key, values in filters.iteritems():
        for value in values:
            query += ' %s:"%s"' % (key, value)

    result = get_api_result("/lib/search", dict(query=query))
    click.secho("Found %d libraries:\n" % result['total'],
                fg="green" if result['total'] else "yellow")

    if result['total']:
        echo_liblist_header()

    while True:
        for item in result['items']:
            echo_liblist_item(item)

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
@click.argument("ids", type=click.INT, nargs=-1, metavar="[LIBRARY_ID]")
@click.option("-v", "--version")
def lib_install_cli(ids, version):
    lib_install(ids, version)


def lib_install(ids, version=None):
    lm = LibraryManager(get_lib_dir())
    for id_ in ids:
        click.echo(
            "Installing library [ %s ]:" % click.style(str(id_), fg="green"))
        try:
            if not lm.install(id_, version):
                continue

            info = lm.get_info(id_)
            click.secho(
                "The library #%s '%s' has been successfully installed!"
                % (str(id_), info['name']), fg="green")

            if "dependencies" in info:
                click.secho("Installing dependencies:", fg="yellow")
                _dependencies = info['dependencies']
                if not isinstance(_dependencies, list):
                    _dependencies = [_dependencies]
                for item in _dependencies:
                    try:
                        lib_install_dependency(item)
                    except AssertionError:
                        raise LibInstallDependencyError(str(item))

        except LibAlreadyInstalledError:
            click.secho("Already installed", fg="yellow")


def lib_install_dependency(data):
    assert isinstance(data, dict)
    query = []
    for key in data.keys():
        if key in ("authors", "frameworks", "platforms", "keywords"):
            values = data[key]
            if not isinstance(values, list):
                values = [v.strip() for v in values.split(",") if v]
            for value in values:
                query.append('%s:"%s"' % (key[:-1], value))
        elif isinstance(data[key], basestring):
            query.append('+"%s"' % data[key])

    result = get_api_result("/lib/search", dict(query=" ".join(query)))
    assert result['total'] == 1
    lib_install([result['items'][0]['id']])


@cli.command("uninstall", short_help="Uninstall libraries")
@click.argument("ids", type=click.INT, nargs=-1)
def lib_uninstall_cli(ids):
    lib_uninstall(ids)


def lib_uninstall(ids):
    lm = LibraryManager(get_lib_dir())
    for id_ in ids:
        info = lm.get_info(id_)
        if lm.uninstall(id_):
            click.secho("The library #%s '%s' has been successfully "
                        "uninstalled!" % (str(id_), info['name']), fg="green")


@cli.command("list", short_help="List installed libraries")
def lib_list():
    lm = LibraryManager(get_lib_dir())
    items = lm.get_installed().values()
    if not items:
        return

    echo_liblist_header()
    for item in items:
        item['authornames'] = [i['name'] for i in item['authors']]
        echo_liblist_item(item)


@cli.command("show", short_help="Show details about installed libraries")
@click.argument("libid", type=click.INT)
def lib_show(libid):
    lm = LibraryManager(get_lib_dir())
    info = lm.get_info(libid)
    click.secho(info['name'], fg="cyan")
    click.echo("-" * len(info['name']))

    _authors = []
    for author in info['authors']:
        _data = []
        for key in ("name", "email", "url", "maintainer"):
            if not author[key]:
                continue
            if key == "email":
                _data.append("<%s>" % author[key])
            elif key == "maintainer":
                _data.append("(maintainer)")
            else:
                _data.append(author[key])
        _authors.append(" ".join(_data))
    click.echo("Authors: %s" % ", ".join(_authors))

    click.echo("Keywords: %s" % ", ".join(info['keywords']))
    if "frameworks" in info:
        click.echo("Frameworks: %s" % ", ".join(info['frameworks']))
    if "platforms" in info:
        click.echo("Platforms: %s" % ", ".join(info['platforms']))
    click.echo("Version: %s" % info['version'])
    click.echo()
    click.echo(info['description'])
    click.echo()


@cli.command("update", short_help="Update installed libraries")
def lib_update():
    lm = LibraryManager(get_lib_dir())

    lib_ids = [str(item['id']) for item in lm.get_installed().values()]
    if not lib_ids:
        return

    versions = get_api_result("/lib/version/" + str(",".join(lib_ids)))
    for id_ in lib_ids:
        info = lm.get_info(int(id_))

        click.echo("Updating  [ %s ] %s library:" % (
            click.style(id_, fg="yellow"),
            click.style(info['name'], fg="cyan")))

        current_version = info['version']
        latest_version = versions[id_]

        if latest_version is None:
            click.secho("Unknown library", fg="red")
            continue

        click.echo("Versions: Current=%s, Latest=%s \t " % (
            current_version, latest_version), nl=False)

        if current_version == latest_version:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
            continue
        else:
            click.echo("[%s]" % (click.style("Out-of-date", fg="red")))

        lib_uninstall([int(id_)])
        lib_install([int(id_)])


@cli.command("register", short_help="Register new library")
@click.argument("config_url")
def lib_register(config_url):
    result = get_api_result("/lib/register", data=dict(config_url=config_url))
    if "message" in result and result['message']:
        click.secho(result['message'], fg="green" if "successed" in result and
                    result['successed'] else "red")

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json

import click

from platformio import app, exception
from platformio.libmanager import LibraryManager
from platformio.util import get_api_result

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

    terminal_width, _ = click.get_terminal_size()
    click.echo("-" * terminal_width)


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
@click.argument("query", required=False)
def lib_search(query, **filters):
    if not query:
        query = ""

    for key, values in filters.iteritems():
        for value in values:
            query += ' %s:"%s"' % (key, value)

    result = get_api_result("/lib/search", dict(query=query))
    if result['total'] == 0:
        click.secho(
            "Nothing has been found by your request\n"
            "Try a less-specific search or use truncation (or wildcard) "
            "operator", fg="yellow", nl=False)
        click.secho(" *", fg="green")
        click.secho("For example: DS*, PCA*, DHT* and etc.\n", fg="yellow")
        click.echo("For more examples and advanced search syntax, "
                   "please use documentation:")
        click.secho("http://docs.platformio.org"
                    "/en/latest/userguide/lib/cmd_search.html\n", fg="cyan")
        return

    click.secho("Found %d libraries:\n" % result['total'],
                fg="green" if result['total'] else "yellow")

    if result['total']:
        echo_liblist_header()

    while True:
        for item in result['items']:
            echo_liblist_item(item)

        if int(result['page'])*int(result['perpage']) >= int(result['total']):
            break

        if (app.get_setting("enable_prompts") and
                click.confirm("Show next libraries?")):
            result = get_api_result(
                "/lib/search",
                dict(query=query, page=str(int(result['page']) + 1))
            )
        else:
            break


@cli.command("install", short_help="Install library")
@click.argument("libid", type=click.INT, nargs=-1, metavar="[LIBRARY_ID]")
@click.option("-v", "--version")
@click.pass_context
def lib_install(ctx, libid, version):
    lm = LibraryManager()
    for id_ in libid:
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
                        lib_install_dependency(ctx, item)
                    except AssertionError:
                        raise exception.LibInstallDependencyError(str(item))

        except exception.LibAlreadyInstalledError:
            click.secho("Already installed", fg="yellow")


def lib_install_dependency(ctx, data):
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
    assert result['total'] > 0

    if result['total'] == 1 or not app.get_setting("enable_prompts"):
        ctx.invoke(lib_install, libid=[result['items'][0]['id']])
    else:
        click.secho(
            "Conflict: More then one dependent libraries have been found "
            "by request %s:" % json.dumps(data), fg="red")

        echo_liblist_header()
        for item in result['items']:
            echo_liblist_item(item)

        deplib_id = click.prompt(
            "Please choose one dependent library ID",
            type=click.Choice([str(i['id']) for i in result['items']]))
        ctx.invoke(lib_install, libid=[int(deplib_id)])


@cli.command("uninstall", short_help="Uninstall libraries")
@click.argument("libid", type=click.INT, nargs=-1)
def lib_uninstall(libid):
    lm = LibraryManager()
    for id_ in libid:
        info = lm.get_info(id_)
        if lm.uninstall(id_):
            click.secho("The library #%s '%s' has been successfully "
                        "uninstalled!" % (str(id_), info['name']), fg="green")


@cli.command("list", short_help="List installed libraries")
@click.option("--json-output", is_flag=True)
def lib_list(json_output):
    lm = LibraryManager()
    items = lm.get_installed().values()

    if json_output:
        click.echo(json.dumps(items))
        return

    if not items:
        return

    echo_liblist_header()
    for item in sorted(items, key=lambda i: i['id']):
        item['authornames'] = [i['name'] for i in item['authors']]
        echo_liblist_item(item)


@cli.command("show", short_help="Show details about installed library")
@click.argument("libid", type=click.INT)
def lib_show(libid):
    lm = LibraryManager()
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
@click.argument("libid", type=click.INT, nargs=-1, required=False,
                metavar="[LIBRARY_ID]")
@click.pass_context
def lib_update(ctx, libid):
    lm = LibraryManager()
    for id_, latest_version in (lm.get_latest_versions() or {}).items():
        if libid and int(id_) not in libid:
            continue

        info = lm.get_info(int(id_))

        click.echo("Updating [ %s ] %s library:" % (
            click.style(id_, fg="yellow"),
            click.style(info['name'], fg="cyan")))

        current_version = info['version']
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

        ctx.invoke(lib_uninstall, libid=[int(id_)])
        ctx.invoke(lib_install, libid=[int(id_)])


@cli.command("register", short_help="Register new library")
@click.argument("config_url")
def lib_register(config_url):
    if (not config_url.startswith("http://") and not
            config_url.startswith("https://")):
        raise exception.InvalidLibConfURL(config_url)

    result = get_api_result("/lib/register", data=dict(config_url=config_url))
    if "message" in result and result['message']:
        click.secho(result['message'], fg="green" if "successed" in result and
                    result['successed'] else "red")

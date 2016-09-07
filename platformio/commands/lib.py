# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from os.path import join
from time import sleep

import click

from platformio import exception, util
from platformio.managers.lib import LibraryManager
from platformio.util import get_api_result


@click.group(short_help="Library Manager")
@click.option(
    "-g",
    "--global",
    is_flag=True,
    help="Manager global PlatformIO"
    " library storage `%s`" % join(util.get_home_dir(), "lib"))
@click.option(
    "-d",
    "--storage-dir",
    default=None,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True),
    help="Manage custom library storage")
@click.pass_context
def cli(ctx, **options):
    # skip commands that don't need storage folder
    if ctx.invoked_subcommand in ("search", "register") or \
            (len(ctx.args) == 2 and ctx.args[1] in ("-h", "--help")):
        return
    storage_dir = options['storage_dir']
    if not storage_dir:
        if options['global']:
            storage_dir = join(util.get_home_dir(), "lib")
        elif util.is_platformio_project():
            storage_dir = util.get_projectlibdeps_dir()
        elif util.is_ci():
            storage_dir = join(util.get_home_dir(), "lib")
            click.secho(
                "Warning! Global library storage is used automatically. "
                "Please use `platformio lib --global %s` command to remove "
                "this warning." % ctx.invoked_subcommand,
                fg="yellow")

    if not storage_dir and not util.is_platformio_project():
        raise exception.NotGlobalLibDir(util.get_project_dir(),
                                        join(util.get_home_dir(), "lib"),
                                        ctx.invoked_subcommand)

    ctx.obj = LibraryManager(storage_dir)
    if "--json-output" not in ctx.args:
        click.echo("Library Storage: " + storage_dir)


@cli.command("install", short_help="Install library")
@click.argument("libraries", required=False, nargs=-1, metavar="[LIBRARY...]")
# @click.option(
#     "--save",
#     is_flag=True,
#     help="Save installed libraries into the project's platformio.ini "
#     "library dependencies")
@click.option(
    "-s", "--silent", is_flag=True, help="Suppress progress reporting")
@click.option(
    "--interactive",
    is_flag=True,
    help="Allow to make a choice for all prompts")
@click.pass_obj
def lib_install(lm, libraries, silent, interactive):
    # @TODO "save" option
    for library in libraries:
        lm.install(library, silent=silent, interactive=interactive)


@cli.command("uninstall", short_help="Uninstall libraries")
@click.argument("libraries", nargs=-1, metavar="[LIBRARY...]")
@click.pass_obj
def lib_uninstall(lm, libraries):
    for library in libraries:
        lm.uninstall(library)


@cli.command("update", short_help="Update installed libraries")
@click.argument("libraries", required=False, nargs=-1, metavar="[LIBRARY...]")
@click.option(
    "-c",
    "--only-check",
    is_flag=True,
    help="Do not update, only check for new version")
@click.pass_obj
def lib_update(lm, libraries, only_check):
    if not libraries:
        libraries = [str(m.get("id", m['name'])) for m in lm.get_installed()]
    for library in libraries:
        lm.update(library, only_check=only_check)

#######

LIBLIST_TPL = ("[{id:^14}] {name:<25} {compatibility:<30} "
               "\"{authornames}\": {description}")


def echo_liblist_header():
    click.echo(
        LIBLIST_TPL.format(
            id=click.style(
                "ID", fg="green"),
            name=click.style(
                "Name", fg="cyan"),
            compatibility=click.style(
                "Compatibility", fg="yellow"),
            authornames="Authors",
            description="Description"))

    terminal_width, _ = click.get_terminal_size()
    click.echo("-" * terminal_width)


def echo_liblist_item(item):
    description = item.get("description", item.get("url", "")).encode("utf-8")
    if "version" in item:
        description += " | @" + click.style(item['version'], fg="yellow")

    click.echo(
        LIBLIST_TPL.format(
            id=click.style(
                str(item.get("id", "-")), fg="green"),
            name=click.style(
                item['name'], fg="cyan"),
            compatibility=click.style(
                ", ".join(
                    item.get("frameworks", ["-"]) + item.get("platforms", [])),
                fg="yellow"),
            authornames=", ".join(item.get("authornames", ["Unknown"])).encode(
                "utf-8"),
            description=description))


@cli.command("search", short_help="Search for library")
@click.argument("query", required=False, nargs=-1)
@click.option("--json-output", is_flag=True)
@click.option("--page", type=click.INT, default=1)
@click.option("-n", "--name", multiple=True)
@click.option("-a", "--author", multiple=True)
@click.option("-k", "--keyword", multiple=True)
@click.option("-f", "--framework", multiple=True)
@click.option("-p", "--platform", multiple=True)
@click.option("-i", "--header", multiple=True)
@click.option(
    "--noninteractive",
    is_flag=True,
    help="Do not prompt, automatically paginate with delay")
def lib_search(query, json_output, page, noninteractive, **filters):
    if not query:
        query = []
    if not isinstance(query, list):
        query = list(query)

    for key, values in filters.iteritems():
        for value in values:
            query.append('%s:"%s"' % (key, value))

    result = get_api_result(
        "/lib/search", dict(
            query=" ".join(query), page=page))

    if json_output:
        click.echo(json.dumps(result))
        return

    if result['total'] == 0:
        click.secho(
            "Nothing has been found by your request\n"
            "Try a less-specific search or use truncation (or wildcard) "
            "operator",
            fg="yellow",
            nl=False)
        click.secho(" *", fg="green")
        click.secho("For example: DS*, PCA*, DHT* and etc.\n", fg="yellow")
        click.echo("For more examples and advanced search syntax, "
                   "please use documentation:")
        click.secho(
            "http://docs.platformio.org"
            "/en/stable/userguide/lib/cmd_search.html\n",
            fg="cyan")
        return

    click.secho(
        "Found %d libraries:\n" % result['total'],
        fg="green" if result['total'] else "yellow")

    if result['total']:
        echo_liblist_header()

    while True:
        for item in result['items']:
            echo_liblist_item(item)

        if (int(result['page']) * int(result['perpage']) >=
                int(result['total'])):
            break

        if noninteractive:
            click.echo()
            click.secho(
                "Loading next %d libraries... Press Ctrl+C to stop!" %
                result['perpage'],
                fg="yellow")
            click.echo()
            sleep(5)
        elif not click.confirm("Show next libraries?"):
            break
        result = get_api_result(
            "/lib/search",
            dict(
                query=" ".join(query), page=int(result['page']) + 1))


@cli.command("list", short_help="List installed libraries")
@click.option("--json-output", is_flag=True)
@click.pass_obj
def lib_list(lm, json_output):
    items = lm.get_installed()

    if json_output:
        click.echo(json.dumps(items))
        return

    if not items:
        return

    echo_liblist_header()
    for item in sorted(items, key=lambda i: i['name']):
        if "authors" in item:
            item['authornames'] = [i['name'] for i in item['authors']]
        echo_liblist_item(item)


@cli.command("show", short_help="Show details about installed library")
@click.pass_obj
@click.argument("library", metavar="[LIBRARY]")
def lib_show(lm, library):  # pylint: disable=too-many-branches
    name, requirements, url = lm.parse_pkg_name(library)
    package_dir = lm.get_package_dir(name, requirements, url)
    if not package_dir:
        click.secho(
            "%s @ %s is not installed" % (name, requirements or "*"),
            fg="yellow")
        return

    manifest = lm.load_manifest(package_dir)

    click.secho(manifest['name'], fg="cyan")
    click.echo("=" * len(manifest['name']))
    if "description" in manifest:
        click.echo(manifest['description'])
    click.echo()

    _authors = []
    for author in manifest.get("authors", []):
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
    if _authors:
        click.echo("Authors: %s" % ", ".join(_authors))

    for key in ("keywords", "frameworks", "platforms", "license", "url",
                "version"):
        if key not in manifest:
            continue
        if isinstance(manifest[key], list):
            click.echo("%s: %s" % (key.title(), ", ".join(manifest[key])))
        else:
            click.echo("%s: %s" % (key.title(), manifest[key]))


@cli.command("register", short_help="Register new library")
@click.argument("config_url")
def lib_register(config_url):
    if (not config_url.startswith("http://") and
            not config_url.startswith("https://")):
        raise exception.InvalidLibConfURL(config_url)

    result = get_api_result("/lib/register", data=dict(config_url=config_url))
    if "message" in result and result['message']:
        click.secho(
            result['message'],
            fg="green"
            if "successed" in result and result['successed'] else "red")

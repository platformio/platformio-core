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

# pylint: disable=too-many-branches, too-many-locals

import json
from os.path import isdir, join
from time import sleep
from urllib import quote

import arrow
import click

from platformio import exception, util
from platformio.managers.lib import LibraryManager
from platformio.managers.platform import PlatformFactory, PlatformManager
from platformio.util import get_api_result


@click.group(short_help="Library Manager")
@click.option(
    "-g",
    "--global",
    is_flag=True,
    help="Manage global PlatformIO"
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
    non_storage_cmds = ("search", "show", "register", "stats", "builtin")
    # skip commands that don't need storage folder
    if ctx.invoked_subcommand in non_storage_cmds or \
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
@click.option("--json-output", is_flag=True)
@click.pass_obj
def lib_update(lm, libraries, only_check, json_output):
    if not libraries:
        libraries = [manifest['__pkg_dir'] for manifest in lm.get_installed()]

    if only_check and json_output:
        result = []
        for library in libraries:
            pkg_dir = library if isdir(library) else None
            requirements = None
            url = None
            if not pkg_dir:
                name, requirements, url = lm.parse_pkg_input(library)
                pkg_dir = lm.get_package_dir(name, requirements, url)
            if not pkg_dir:
                continue
            latest = lm.outdated(pkg_dir, requirements)
            if not latest:
                continue
            manifest = lm.load_manifest(pkg_dir)
            manifest['versionLatest'] = latest
            result.append(manifest)
        return click.echo(json.dumps(result))
    else:
        for library in libraries:
            lm.update(library, only_check=only_check)


def print_lib_item(item):
    click.secho(item['name'], fg="cyan")
    click.echo("=" * len(item['name']))
    if "id" in item:
        click.secho("#ID: %d" % item['id'], bold=True)
    if "description" in item or "url" in item:
        click.echo(item.get("description", item.get("url", "")))
    click.echo()

    for key in ("version", "homepage", "license", "keywords"):
        if key not in item or not item[key]:
            continue
        if isinstance(item[key], list):
            click.echo("%s: %s" % (key.title(), ", ".join(item[key])))
        else:
            click.echo("%s: %s" % (key.title(), item[key]))

    for key in ("frameworks", "platforms"):
        if key not in item:
            continue
        click.echo("Compatible %s: %s" % (key, ", ".join(
            [i['title'] if isinstance(i, dict) else i for i in item[key]])))

    if "authors" in item or "authornames" in item:
        click.echo("Authors: %s" % ", ".join(
            item.get("authornames",
                     [a.get("name", "") for a in item.get("authors", [])])))

    if "__src_url" in item:
        click.secho("Source: %s" % item['__src_url'])
    click.echo()


@cli.command("search", short_help="Search for a library")
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
        "/v2/lib/search",
        dict(query=" ".join(query), page=page),
        cache_valid="3d")

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
            "http://docs.platformio.org/page/userguide/lib/cmd_search.html\n",
            fg="cyan")
        return

    click.secho(
        "Found %d libraries:\n" % result['total'],
        fg="green" if result['total'] else "yellow")

    while True:
        for item in result['items']:
            print_lib_item(item)

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
            "/v2/lib/search",
            {"query": " ".join(query),
             "page": int(result['page']) + 1},
            cache_valid="3d")


@cli.command("list", short_help="List installed libraries")
@click.option("--json-output", is_flag=True)
@click.pass_obj
def lib_list(lm, json_output):
    items = lm.get_installed()

    if json_output:
        return click.echo(json.dumps(items))

    if not items:
        return

    for item in sorted(items, key=lambda i: i['name']):
        print_lib_item(item)


@util.memoized
def get_builtin_libs(storage_names=None):
    items = []
    storage_names = storage_names or []
    pm = PlatformManager()
    for manifest in pm.get_installed():
        p = PlatformFactory.newPlatform(manifest['__pkg_dir'])
        for storage in p.get_lib_storages():
            if storage_names and storage['name'] not in storage_names:
                continue
            lm = LibraryManager(storage['path'])
            items.append({
                "name": storage['name'],
                "path": storage['path'],
                "items": lm.get_installed()
            })
    return items


@cli.command("builtin", short_help="List built-in libraries")
@click.option("--storage", multiple=True)
@click.option("--json-output", is_flag=True)
def lib_builtin(storage, json_output):
    items = get_builtin_libs(storage)
    if json_output:
        return click.echo(json.dumps(items))

    for storage in items:
        if not storage['items']:
            continue
        click.secho(storage['name'], fg="green")
        click.echo("*" * len(storage['name']))
        click.echo()

        for item in sorted(storage['items'], key=lambda i: i['name']):
            print_lib_item(item)


@cli.command("show", short_help="Show detailed info about a library")
@click.argument("library", metavar="[LIBRARY]")
@click.option("--json-output", is_flag=True)
def lib_show(library, json_output):
    lm = LibraryManager()
    name, requirements, _ = lm.parse_pkg_input(library)
    lib_id = lm.get_pkg_id_by_name(
        name, requirements, silent=json_output, interactive=not json_output)
    lib = get_api_result("/lib/info/%d" % lib_id, cache_valid="1d")
    if json_output:
        return click.echo(json.dumps(lib))

    click.secho(lib['name'], fg="cyan")
    click.echo("=" * len(lib['name']))
    click.secho("#ID: %d" % lib['id'], bold=True)
    click.echo(lib['description'])
    click.echo()

    click.echo("Version: %s, released %s" %
               (lib['version']['name'],
                arrow.get(lib['version']['released']).humanize()))
    click.echo("Manifest: %s" % lib['confurl'])
    for key in ("homepage", "repository", "license"):
        if key not in lib or not lib[key]:
            continue
        if isinstance(lib[key], list):
            click.echo("%s: %s" % (key.title(), ", ".join(lib[key])))
        else:
            click.echo("%s: %s" % (key.title(), lib[key]))

    blocks = []

    _authors = []
    for author in lib.get("authors", []):
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
        blocks.append(("Authors", _authors))

    blocks.append(("Keywords", lib['keywords']))
    for key in ("frameworks", "platforms"):
        if key not in lib or not lib[key]:
            continue
        blocks.append(("Compatible %s" % key, [i['title'] for i in lib[key]]))
    blocks.append(("Headers", lib['headers']))
    blocks.append(("Examples", lib['examples']))
    blocks.append(("Versions", [
        "%s, released %s" % (v['name'], arrow.get(v['released']).humanize())
        for v in lib['versions']
    ]))
    blocks.append(("Unique Downloads", [
        "Today: %s" % lib['dlstats']['day'], "Week: %s" %
        lib['dlstats']['week'], "Month: %s" % lib['dlstats']['month']
    ]))

    for (title, rows) in blocks:
        click.echo()
        click.secho(title, bold=True)
        click.echo("-" * len(title))
        for row in rows:
            click.echo(row)


@cli.command("register", short_help="Register a new library")
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


@cli.command("stats", short_help="Library Registry Statistics")
@click.option("--json-output", is_flag=True)
def lib_stats(json_output):
    result = get_api_result("/lib/stats", cache_valid="1h")

    if json_output:
        return click.echo(json.dumps(result))

    printitem_tpl = "{name:<33} {url}"
    printitemdate_tpl = "{name:<33} {date:23} {url}"

    def _print_title(title):
        click.secho(title.upper(), bold=True)
        click.echo("*" * len(title))

    def _print_header(with_date=False):
        click.echo((printitemdate_tpl if with_date else printitem_tpl).format(
            name=click.style("Name", fg="cyan"),
            date="Date",
            url=click.style("Url", fg="blue")))

        terminal_width, _ = click.get_terminal_size()
        click.echo("-" * terminal_width)

    def _print_lib_item(item):
        click.echo((
            printitemdate_tpl if "date" in item else printitem_tpl
        ).format(
            name=click.style(item['name'], fg="cyan"),
            date=str(
                arrow.get(item['date']).humanize() if "date" in item else ""),
            url=click.style(
                "http://platformio.org/lib/show/%s/%s" % (item['id'],
                                                          quote(item['name'])),
                fg="blue")))

    def _print_tag_item(name):
        click.echo(
            printitem_tpl.format(
                name=click.style(name, fg="cyan"),
                url=click.style(
                    "http://platformio.org/lib/search?query=" + quote(
                        "keyword:%s" % name),
                    fg="blue")))

    for key in ("updated", "added"):
        _print_title("Recently " + key)
        _print_header(with_date=True)
        for item in result.get(key, []):
            _print_lib_item(item)
        click.echo()

    _print_title("Recent keywords")
    _print_header(with_date=False)
    for item in result.get("lastkeywords"):
        _print_tag_item(item)
    click.echo()

    _print_title("Popular keywords")
    _print_header(with_date=False)
    for item in result.get("topkeywords"):
        _print_tag_item(item)
    click.echo()

    for key, title in (("dlday", "Today"), ("dlweek", "Week"),
                       ("dlmonth", "Month")):
        _print_title("Featured: " + title)
        _print_header(with_date=False)
        for item in result.get(key, []):
            _print_lib_item(item)
        click.echo()

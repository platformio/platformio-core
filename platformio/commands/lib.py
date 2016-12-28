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
from os.path import join
from time import sleep
from urllib import quote

import arrow
import click

from platformio import exception, util
from platformio.managers.lib import LibraryManager
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
    # skip commands that don't need storage folder
    if ctx.invoked_subcommand in ("search", "show", "register", "stats") or \
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

LIBLIST_TPL = ("[{id:^15}] {name:<25} {compatibility:<30} "
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
        "/lib/search",
        dict(
            query=" ".join(query), page=page),
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
                query=" ".join(query), page=int(result['page']) + 1),
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

    echo_liblist_header()
    for item in sorted(items, key=lambda i: i['name']):
        if "authors" in item:
            item['authornames'] = [i['name'] for i in item['authors']]
        echo_liblist_item(item)


@cli.command("show", short_help="Show detailed info about a library")
@click.argument("library", metavar="[LIBRARY]")
@click.option("--json-output", is_flag=True)
def lib_show(library, json_output):
    lm = LibraryManager()
    name, requirements, _ = lm.parse_pkg_name(library)
    lib_id = lm.get_pkg_id_by_name(
        name, requirements, silent=json_output, interactive=not json_output)
    lib = get_api_result("/lib/info/%d" % lib_id, cache_valid="1d")
    if json_output:
        return click.echo(json.dumps(lib))

    click.secho(lib['name'], fg="cyan")
    click.echo("=" * len(lib['name']))
    click.echo(lib['description'])
    click.echo()

    click.echo("Version: %s, released %s" %
               (lib['version']['name'],
                arrow.get(lib['version']['released']).humanize()))
    click.echo("Registry ID: %d" % lib['id'])
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
    if lib['frameworks']:
        blocks.append(("Compatible Frameworks", lib['frameworks']))
    if lib['platforms']:
        blocks.append(("Compatible Platforms", lib['platforms']))
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
            name=click.style(
                "Name", fg="cyan"),
            date="Date",
            url=click.style(
                "Url", fg="blue")))

        terminal_width, _ = click.get_terminal_size()
        click.echo("-" * terminal_width)

    def _print_lib_item(item):
        click.echo((printitemdate_tpl
                    if "date" in item else printitem_tpl).format(
                        name=click.style(
                            item['name'], fg="cyan"),
                        date=str(
                            arrow.get(item['date']).humanize()
                            if "date" in item else ""),
                        url=click.style(
                            "http://platformio.org/lib/show/%s/%s" % (item[
                                'id'], quote(item['name'])),
                            fg="blue")))

    def _print_tag_item(name):
        click.echo(
            printitem_tpl.format(
                name=click.style(
                    name, fg="cyan"),
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

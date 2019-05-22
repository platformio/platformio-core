# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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
import time
from os.path import isdir, join

import click

from platformio import exception, util
from platformio.managers.lib import LibraryManager, get_builtin_libs
from platformio.proc import is_ci
from platformio.project.config import ProjectConfig
from platformio.project.helpers import (
    get_project_dir, get_projectlibdeps_dir, is_platformio_project)

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


@click.group(short_help="Library Manager")
@click.option(
    "-d",
    "--storage-dir",
    multiple=True,
    default=None,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True),
    help="Manage custom library storage")
@click.option(
    "-g",
    "--global",
    is_flag=True,
    help="Manage global PlatformIO library storage")
@click.option(
    "-e",
    "--environment",
    multiple=True,
    help=("Manage libraries for the specific project build environments "
          "declared in `platformio.ini`"))
@click.pass_context
def cli(ctx, **options):
    storage_cmds = ("install", "uninstall", "update", "list")
    # skip commands that don't need storage folder
    if ctx.invoked_subcommand not in storage_cmds or \
            (len(ctx.args) == 2 and ctx.args[1] in ("-h", "--help")):
        return
    storage_dirs = list(options['storage_dir'])
    if options['global']:
        storage_dirs.append(join(util.get_home_dir(), "lib"))
    if not storage_dirs:
        if is_platformio_project():
            storage_dirs = [get_project_dir()]
        elif is_ci():
            storage_dirs = [join(util.get_home_dir(), "lib")]
            click.secho(
                "Warning! Global library storage is used automatically. "
                "Please use `platformio lib --global %s` command to remove "
                "this warning." % ctx.invoked_subcommand,
                fg="yellow")

    if not storage_dirs:
        raise exception.NotGlobalLibDir(get_project_dir(),
                                        join(util.get_home_dir(), "lib"),
                                        ctx.invoked_subcommand)
    ctx.obj = []
    for storage_dir in storage_dirs:
        if is_platformio_project(storage_dir):
            with util.cd(storage_dir):
                config = ProjectConfig.get_instance(
                    join(storage_dir, "platformio.ini"))
                config.validate(options['environment'])
                libdeps_dir = get_projectlibdeps_dir()
                for env in config.envs():
                    if (not options['environment']
                            or env in options['environment']):
                        ctx.obj.append(join(libdeps_dir, env))
        else:
            ctx.obj.append(storage_dir)


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
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Reinstall/redownload library if exists")
@click.pass_obj
def lib_install(storage_dirs, libraries, silent, interactive, force):
    for storage_dir in storage_dirs:
        print_storage_header(storage_dirs, storage_dir)
        lm = LibraryManager(storage_dir)
        for library in libraries:
            lm.install(
                library, silent=silent, interactive=interactive, force=force)


@cli.command("uninstall", short_help="Uninstall libraries")
@click.argument("libraries", nargs=-1, metavar="[LIBRARY...]")
@click.pass_obj
def lib_uninstall(storage_dirs, libraries):
    for storage_dir in storage_dirs:
        print_storage_header(storage_dirs, storage_dir)
        lm = LibraryManager(storage_dir)
        for library in libraries:
            lm.uninstall(library)


@cli.command("update", short_help="Update installed libraries")
@click.argument("libraries", required=False, nargs=-1, metavar="[LIBRARY...]")
@click.option(
    "-c",
    "--only-check",
    is_flag=True,
    help="DEPRECATED. Please use `--dry-run` instead")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Do not update, only check for the new versions")
@click.option("--json-output", is_flag=True)
@click.pass_obj
def lib_update(storage_dirs, libraries, only_check, dry_run, json_output):
    only_check = dry_run or only_check
    json_result = {}
    for storage_dir in storage_dirs:
        if not json_output:
            print_storage_header(storage_dirs, storage_dir)
        lm = LibraryManager(storage_dir)

        _libraries = libraries
        if not _libraries:
            _libraries = [
                manifest['__pkg_dir'] for manifest in lm.get_installed()
            ]

        if only_check and json_output:
            result = []
            for library in _libraries:
                pkg_dir = library if isdir(library) else None
                requirements = None
                url = None
                if not pkg_dir:
                    name, requirements, url = lm.parse_pkg_uri(library)
                    pkg_dir = lm.get_package_dir(name, requirements, url)
                if not pkg_dir:
                    continue
                latest = lm.outdated(pkg_dir, requirements)
                if not latest:
                    continue
                manifest = lm.load_manifest(pkg_dir)
                manifest['versionLatest'] = latest
                result.append(manifest)
            json_result[storage_dir] = result
        else:
            for library in _libraries:
                lm.update(library, only_check=only_check)

    if json_output:
        return click.echo(
            json.dumps(json_result[storage_dirs[0]] if len(storage_dirs) ==
                       1 else json_result))

    return True


@cli.command("list", short_help="List installed libraries")
@click.option("--json-output", is_flag=True)
@click.pass_obj
def lib_list(storage_dirs, json_output):
    json_result = {}
    for storage_dir in storage_dirs:
        if not json_output:
            print_storage_header(storage_dirs, storage_dir)
        lm = LibraryManager(storage_dir)
        items = lm.get_installed()
        if json_output:
            json_result[storage_dir] = items
        else:
            for item in sorted(items, key=lambda i: i['name']):
                print_lib_item(item)

    if json_output:
        return click.echo(
            json.dumps(json_result[storage_dirs[0]] if len(storage_dirs) ==
                       1 else json_result))

    return True


@cli.command("search", short_help="Search for a library")
@click.argument("query", required=False, nargs=-1)
@click.option("--json-output", is_flag=True)
@click.option("--page", type=click.INT, default=1)
@click.option("--id", multiple=True)
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

    for key, values in filters.items():
        for value in values:
            query.append('%s:"%s"' % (key, value))

    result = util.get_api_result(
        "/v2/lib/search",
        dict(query=" ".join(query), page=page),
        cache_valid="1d")

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
            "https://docs.platformio.org/page/userguide/lib/cmd_search.html\n",
            fg="cyan")
        return

    click.secho(
        "Found %d libraries:\n" % result['total'],
        fg="green" if result['total'] else "yellow")

    while True:
        for item in result['items']:
            print_lib_item(item)

        if (int(result['page']) * int(result['perpage']) >= int(
                result['total'])):
            break

        if noninteractive:
            click.echo()
            click.secho(
                "Loading next %d libraries... Press Ctrl+C to stop!" %
                result['perpage'],
                fg="yellow")
            click.echo()
            time.sleep(5)
        elif not click.confirm("Show next libraries?"):
            break
        result = util.get_api_result(
            "/v2/lib/search", {
                "query": " ".join(query),
                "page": int(result['page']) + 1
            },
            cache_valid="1d")


@cli.command("builtin", short_help="List built-in libraries")
@click.option("--storage", multiple=True)
@click.option("--json-output", is_flag=True)
def lib_builtin(storage, json_output):
    items = get_builtin_libs(storage)
    if json_output:
        return click.echo(json.dumps(items))

    for storage_ in items:
        if not storage_['items']:
            continue
        click.secho(storage_['name'], fg="green")
        click.echo("*" * len(storage_['name']))
        click.echo()

        for item in sorted(storage_['items'], key=lambda i: i['name']):
            print_lib_item(item)

    return True


@cli.command("show", short_help="Show detailed info about a library")
@click.argument("library", metavar="[LIBRARY]")
@click.option("--json-output", is_flag=True)
def lib_show(library, json_output):
    lm = LibraryManager()
    name, requirements, _ = lm.parse_pkg_uri(library)
    lib_id = lm.search_lib_id({
        "name": name,
        "requirements": requirements
    },
                              silent=json_output,
                              interactive=not json_output)
    lib = util.get_api_result("/lib/info/%d" % lib_id, cache_valid="1d")
    if json_output:
        return click.echo(json.dumps(lib))

    click.secho(lib['name'], fg="cyan")
    click.echo("=" * len(lib['name']))
    click.secho("#ID: %d" % lib['id'], bold=True)
    click.echo(lib['description'])
    click.echo()

    click.echo(
        "Version: %s, released %s" %
        (lib['version']['name'],
         time.strftime("%c", util.parse_date(lib['version']['released']))))
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
        "%s, released %s" %
        (v['name'], time.strftime("%c", util.parse_date(v['released'])))
        for v in lib['versions']
    ]))
    blocks.append(("Unique Downloads", [
        "Today: %s" % lib['dlstats']['day'],
        "Week: %s" % lib['dlstats']['week'],
        "Month: %s" % lib['dlstats']['month']
    ]))

    for (title, rows) in blocks:
        click.echo()
        click.secho(title, bold=True)
        click.echo("-" * len(title))
        for row in rows:
            click.echo(row)

    return True


@cli.command("register", short_help="Register a new library")
@click.argument("config_url")
def lib_register(config_url):
    if (not config_url.startswith("http://")
            and not config_url.startswith("https://")):
        raise exception.InvalidLibConfURL(config_url)

    result = util.get_api_result(
        "/lib/register", data=dict(config_url=config_url))
    if "message" in result and result['message']:
        click.secho(
            result['message'],
            fg="green"
            if "successed" in result and result['successed'] else "red")


@cli.command("stats", short_help="Library Registry Statistics")
@click.option("--json-output", is_flag=True)
def lib_stats(json_output):
    result = util.get_api_result("/lib/stats", cache_valid="1h")

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
        date = str(
            time.strftime("%c", util.parse_date(item['date'])) if "date" in
            item else "")
        url = click.style(
            "https://platformio.org/lib/show/%s/%s" % (item['id'],
                                                       quote(item['name'])),
            fg="blue")
        click.echo(
            (printitemdate_tpl if "date" in item else printitem_tpl).format(
                name=click.style(item['name'], fg="cyan"), date=date, url=url))

    def _print_tag_item(name):
        click.echo(
            printitem_tpl.format(
                name=click.style(name, fg="cyan"),
                url=click.style(
                    "https://platformio.org/lib/search?query=" + quote(
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

    for key, title in (("dlday", "Today"), ("dlweek", "Week"), ("dlmonth",
                                                                "Month")):
        _print_title("Featured: " + title)
        _print_header(with_date=False)
        for item in result.get(key, []):
            _print_lib_item(item)
        click.echo()

    return True


def print_storage_header(storage_dirs, storage_dir):
    if storage_dirs and storage_dirs[0] != storage_dir:
        click.echo("")
    click.echo(
        click.style("Library Storage: ", bold=True) +
        click.style(storage_dir, fg="blue"))


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

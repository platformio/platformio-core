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
import os
import time

import click
from tabulate import tabulate

from platformio import exception, fs, util
from platformio.commands import PlatformioCLI
from platformio.commands.lib.helpers import get_builtin_libs, save_project_libdeps
from platformio.package.exception import NotGlobalLibDir, UnknownPackageError
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.meta import PackageItem, PackageSpec
from platformio.proc import is_ci
from platformio.project.config import ProjectConfig
from platformio.project.helpers import get_project_dir, is_platformio_project

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

CTX_META_INPUT_DIRS_KEY = __name__ + ".input_dirs"
CTX_META_PROJECT_ENVIRONMENTS_KEY = __name__ + ".project_environments"
CTX_META_STORAGE_DIRS_KEY = __name__ + ".storage_dirs"
CTX_META_STORAGE_LIBDEPS_KEY = __name__ + ".storage_lib_deps"


def get_project_global_lib_dir():
    return ProjectConfig.get_instance().get_optional_dir("globallib")


@click.group(short_help="Library manager")
@click.option(
    "-d",
    "--storage-dir",
    multiple=True,
    default=None,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
    help="Manage custom library storage",
)
@click.option(
    "-g", "--global", is_flag=True, help="Manage global PlatformIO library storage"
)
@click.option(
    "-e",
    "--environment",
    multiple=True,
    help=(
        "Manage libraries for the specific project build environments "
        "declared in `platformio.ini`"
    ),
)
@click.pass_context
def cli(ctx, **options):
    storage_cmds = ("install", "uninstall", "update", "list")
    # skip commands that don't need storage folder
    if ctx.invoked_subcommand not in storage_cmds or (
        len(ctx.args) == 2 and ctx.args[1] in ("-h", "--help")
    ):
        return
    storage_dirs = list(options["storage_dir"])
    if options["global"]:
        storage_dirs.append(get_project_global_lib_dir())
    if not storage_dirs:
        if is_platformio_project():
            storage_dirs = [get_project_dir()]
        elif is_ci():
            storage_dirs = [get_project_global_lib_dir()]
            click.secho(
                "Warning! Global library storage is used automatically. "
                "Please use `platformio lib --global %s` command to remove "
                "this warning." % ctx.invoked_subcommand,
                fg="yellow",
            )

    if not storage_dirs:
        raise NotGlobalLibDir(
            get_project_dir(), get_project_global_lib_dir(), ctx.invoked_subcommand
        )

    in_silence = PlatformioCLI.in_silence()
    ctx.meta[CTX_META_PROJECT_ENVIRONMENTS_KEY] = options["environment"]
    ctx.meta[CTX_META_INPUT_DIRS_KEY] = storage_dirs
    ctx.meta[CTX_META_STORAGE_DIRS_KEY] = []
    ctx.meta[CTX_META_STORAGE_LIBDEPS_KEY] = {}
    for storage_dir in storage_dirs:
        if not is_platformio_project(storage_dir):
            ctx.meta[CTX_META_STORAGE_DIRS_KEY].append(storage_dir)
            continue
        with fs.cd(storage_dir):
            config = ProjectConfig.get_instance(
                os.path.join(storage_dir, "platformio.ini")
            )
            config.validate(options["environment"], silent=in_silence)
            libdeps_dir = config.get_optional_dir("libdeps")
            for env in config.envs():
                if options["environment"] and env not in options["environment"]:
                    continue
                storage_dir = os.path.join(libdeps_dir, env)
                ctx.meta[CTX_META_STORAGE_DIRS_KEY].append(storage_dir)
                ctx.meta[CTX_META_STORAGE_LIBDEPS_KEY][storage_dir] = config.get(
                    "env:" + env, "lib_deps", []
                )


@cli.command("install", short_help="Install library")
@click.argument("libraries", required=False, nargs=-1, metavar="[LIBRARY...]")
@click.option(
    "--save/--no-save",
    is_flag=True,
    default=True,
    help="Save installed libraries into the `platformio.ini` dependency list"
    " (enabled by default)",
)
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
@click.option(
    "--interactive",
    is_flag=True,
    help="Deprecated! Please use a strict dependency specification (owner/libname)",
)
@click.option(
    "-f", "--force", is_flag=True, help="Reinstall/redownload library if exists"
)
@click.pass_context
def lib_install(  # pylint: disable=too-many-arguments,unused-argument
    ctx, libraries, save, silent, interactive, force
):
    storage_dirs = ctx.meta[CTX_META_STORAGE_DIRS_KEY]
    storage_libdeps = ctx.meta.get(CTX_META_STORAGE_LIBDEPS_KEY, [])

    installed_pkgs = {}
    for storage_dir in storage_dirs:
        if not silent and (libraries or storage_dir in storage_libdeps):
            print_storage_header(storage_dirs, storage_dir)
        lm = LibraryPackageManager(storage_dir)

        if libraries:
            installed_pkgs = {
                library: lm.install(library, silent=silent, force=force)
                for library in libraries
            }

        elif storage_dir in storage_libdeps:
            for library in storage_libdeps[storage_dir]:
                lm.install(library, silent=silent, force=force)

    if save and installed_pkgs:
        _save_deps(ctx, installed_pkgs)


def _save_deps(ctx, pkgs, action="add"):
    specs = []
    for library, pkg in pkgs.items():
        spec = PackageSpec(library)
        if spec.external:
            specs.append(spec)
        else:
            specs.append(
                PackageSpec(
                    owner=pkg.metadata.spec.owner,
                    name=pkg.metadata.spec.name,
                    requirements=spec.requirements
                    or (
                        ("^%s" % pkg.metadata.version)
                        if not pkg.metadata.version.build
                        else pkg.metadata.version
                    ),
                )
            )

    input_dirs = ctx.meta.get(CTX_META_INPUT_DIRS_KEY, [])
    project_environments = ctx.meta[CTX_META_PROJECT_ENVIRONMENTS_KEY]
    for input_dir in input_dirs:
        if not is_platformio_project(input_dir):
            continue
        save_project_libdeps(input_dir, specs, project_environments, action=action)


@cli.command("uninstall", short_help="Remove libraries")
@click.argument("libraries", nargs=-1, metavar="[LIBRARY...]")
@click.option(
    "--save/--no-save",
    is_flag=True,
    default=True,
    help="Remove libraries from the `platformio.ini` dependency list and save changes"
    " (enabled by default)",
)
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
@click.pass_context
def lib_uninstall(ctx, libraries, save, silent):
    storage_dirs = ctx.meta[CTX_META_STORAGE_DIRS_KEY]
    uninstalled_pkgs = {}
    for storage_dir in storage_dirs:
        print_storage_header(storage_dirs, storage_dir)
        lm = LibraryPackageManager(storage_dir)
        uninstalled_pkgs = {
            library: lm.uninstall(library, silent=silent) for library in libraries
        }

    if save and uninstalled_pkgs:
        _save_deps(ctx, uninstalled_pkgs, action="remove")


@cli.command("update", short_help="Update installed libraries")
@click.argument("libraries", required=False, nargs=-1, metavar="[LIBRARY...]")
@click.option(
    "-c",
    "--only-check",
    is_flag=True,
    help="DEPRECATED. Please use `--dry-run` instead",
)
@click.option(
    "--dry-run", is_flag=True, help="Do not update, only check for the new versions"
)
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
@click.option("--json-output", is_flag=True)
@click.pass_context
def lib_update(  # pylint: disable=too-many-arguments
    ctx, libraries, only_check, dry_run, silent, json_output
):
    storage_dirs = ctx.meta[CTX_META_STORAGE_DIRS_KEY]
    only_check = dry_run or only_check
    json_result = {}
    for storage_dir in storage_dirs:
        if not json_output:
            print_storage_header(storage_dirs, storage_dir)
        lib_deps = ctx.meta.get(CTX_META_STORAGE_LIBDEPS_KEY, {}).get(storage_dir, [])
        lm = LibraryPackageManager(storage_dir)
        _libraries = libraries or lib_deps or lm.get_installed()

        if only_check and json_output:
            result = []
            for library in _libraries:
                spec = None
                pkg = None
                if isinstance(library, PackageItem):
                    pkg = library
                else:
                    spec = PackageSpec(library)
                    pkg = lm.get_package(spec)
                if not pkg:
                    continue
                outdated = lm.outdated(pkg, spec)
                if not outdated.is_outdated(allow_incompatible=True):
                    continue
                manifest = lm.legacy_load_manifest(pkg)
                manifest["versionWanted"] = (
                    str(outdated.wanted) if outdated.wanted else None
                )
                manifest["versionLatest"] = (
                    str(outdated.latest) if outdated.latest else None
                )
                result.append(manifest)
            json_result[storage_dir] = result
        else:
            for library in _libraries:
                to_spec = (
                    None if isinstance(library, PackageItem) else PackageSpec(library)
                )
                try:
                    lm.update(
                        library, to_spec=to_spec, only_check=only_check, silent=silent
                    )
                except UnknownPackageError as e:
                    if library not in lib_deps:
                        raise e

    if json_output:
        return click.echo(
            json.dumps(
                json_result[storage_dirs[0]] if len(storage_dirs) == 1 else json_result
            )
        )

    return True


@cli.command("list", short_help="List installed libraries")
@click.option("--json-output", is_flag=True)
@click.pass_context
def lib_list(ctx, json_output):
    storage_dirs = ctx.meta[CTX_META_STORAGE_DIRS_KEY]
    json_result = {}
    for storage_dir in storage_dirs:
        if not json_output:
            print_storage_header(storage_dirs, storage_dir)
        lm = LibraryPackageManager(storage_dir)
        items = lm.legacy_get_installed()
        if json_output:
            json_result[storage_dir] = items
        elif items:
            for item in sorted(items, key=lambda i: i["name"]):
                print_lib_item(item)
        else:
            click.echo("No items found")

    if json_output:
        return click.echo(
            json.dumps(
                json_result[storage_dirs[0]] if len(storage_dirs) == 1 else json_result
            )
        )

    return True


@cli.command("search", short_help="Search for a library")
@click.argument("query", required=False, nargs=-1)
@click.option("--json-output", is_flag=True)
@click.option("--page", type=click.INT, default=1)
@click.option("--id", multiple=True)
@click.option("-o", "--owner", multiple=True)
@click.option("-n", "--name", multiple=True)
@click.option("-a", "--author", multiple=True)
@click.option("-k", "--keyword", multiple=True)
@click.option("-f", "--framework", multiple=True)
@click.option("-p", "--platform", multiple=True)
@click.option("-i", "--header", multiple=True)
@click.option(
    "--noninteractive",
    is_flag=True,
    help="Do not prompt, automatically paginate with delay",
)
def lib_search(query, json_output, page, noninteractive, **filters):
    regclient = LibraryPackageManager().get_registry_client_instance()
    if not query:
        query = []
    if not isinstance(query, list):
        query = list(query)

    for key, values in filters.items():
        for value in values:
            query.append('%s:"%s"' % (key, value))

    result = regclient.fetch_json_data(
        "get",
        "/v2/lib/search",
        params=dict(query=" ".join(query), page=page),
        cache_valid="1d",
    )

    if json_output:
        click.echo(json.dumps(result))
        return

    if result["total"] == 0:
        click.secho(
            "Nothing has been found by your request\n"
            "Try a less-specific search or use truncation (or wildcard) "
            "operator",
            fg="yellow",
            nl=False,
        )
        click.secho(" *", fg="green")
        click.secho("For example: DS*, PCA*, DHT* and etc.\n", fg="yellow")
        click.echo(
            "For more examples and advanced search syntax, please use documentation:"
        )
        click.secho(
            "https://docs.platformio.org/page/userguide/lib/cmd_search.html\n",
            fg="cyan",
        )
        return

    click.secho(
        "Found %d libraries:\n" % result["total"],
        fg="green" if result["total"] else "yellow",
    )

    while True:
        for item in result["items"]:
            print_lib_item(item)

        if int(result["page"]) * int(result["perpage"]) >= int(result["total"]):
            break

        if noninteractive:
            click.echo()
            click.secho(
                "Loading next %d libraries... Press Ctrl+C to stop!"
                % result["perpage"],
                fg="yellow",
            )
            click.echo()
            time.sleep(5)
        elif not click.confirm("Show next libraries?"):
            break
        result = regclient.fetch_json_data(
            "get",
            "/v2/lib/search",
            params=dict(query=" ".join(query), page=int(result["page"]) + 1),
            cache_valid="1d",
        )


@cli.command("builtin", short_help="List built-in libraries")
@click.option("--storage", multiple=True)
@click.option("--json-output", is_flag=True)
def lib_builtin(storage, json_output):
    items = get_builtin_libs(storage)
    if json_output:
        return click.echo(json.dumps(items))

    for storage_ in items:
        if not storage_["items"]:
            continue
        click.secho(storage_["name"], fg="green")
        click.echo("*" * len(storage_["name"]))
        click.echo()

        for item in sorted(storage_["items"], key=lambda i: i["name"]):
            print_lib_item(item)

    return True


@cli.command("show", short_help="Show detailed info about a library")
@click.argument("library", metavar="[LIBRARY]")
@click.option("--json-output", is_flag=True)
def lib_show(library, json_output):
    lm = LibraryPackageManager()
    lib_id = lm.reveal_registry_package_id(library, silent=json_output)
    regclient = lm.get_registry_client_instance()
    lib = regclient.fetch_json_data("get", "/v2/lib/info/%d" % lib_id, cache_valid="1h")
    if json_output:
        return click.echo(json.dumps(lib))

    title = "{ownername}/{name}".format(**lib)
    click.secho(title, fg="cyan")
    click.echo("=" * len(title))
    click.echo(lib["description"])
    click.echo()

    click.secho("ID: %d" % lib["id"])
    click.echo(
        "Version: %s, released %s"
        % (
            lib["version"]["name"],
            time.strftime("%c", util.parse_date(lib["version"]["released"])),
        )
    )
    click.echo("Manifest: %s" % lib["confurl"])
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
            if not author.get(key):
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

    blocks.append(("Keywords", lib["keywords"]))
    for key in ("frameworks", "platforms"):
        if key not in lib or not lib[key]:
            continue
        blocks.append(("Compatible %s" % key, [i["title"] for i in lib[key]]))
    blocks.append(("Headers", lib["headers"]))
    blocks.append(("Examples", lib["examples"]))
    blocks.append(
        (
            "Versions",
            [
                "%s, released %s"
                % (v["name"], time.strftime("%c", util.parse_date(v["released"])))
                for v in lib["versions"]
            ],
        )
    )
    blocks.append(
        (
            "Unique Downloads",
            [
                "Today: %s" % lib["dlstats"]["day"],
                "Week: %s" % lib["dlstats"]["week"],
                "Month: %s" % lib["dlstats"]["month"],
            ],
        )
    )

    for (title, rows) in blocks:
        click.echo()
        click.secho(title, bold=True)
        click.echo("-" * len(title))
        for row in rows:
            click.echo(row)

    return True


@cli.command("register", short_help="Deprecated")
@click.argument("config_url")
def lib_register(config_url):  # pylint: disable=unused-argument
    raise exception.UserSideException(
        "This command is deprecated. Please use `pio package publish` command."
    )


@cli.command("stats", short_help="Library Registry Statistics")
@click.option("--json-output", is_flag=True)
def lib_stats(json_output):
    regclient = LibraryPackageManager().get_registry_client_instance()
    result = regclient.fetch_json_data("get", "/v2/lib/stats", cache_valid="1h")

    if json_output:
        return click.echo(json.dumps(result))

    for key in ("updated", "added"):
        tabular_data = [
            (
                click.style(item["name"], fg="cyan"),
                time.strftime("%c", util.parse_date(item["date"])),
                "https://platformio.org/lib/show/%s/%s"
                % (item["id"], quote(item["name"])),
            )
            for item in result.get(key, [])
        ]
        table = tabulate(
            tabular_data,
            headers=[click.style("RECENTLY " + key.upper(), bold=True), "Date", "URL"],
        )
        click.echo(table)
        click.echo()

    for key in ("lastkeywords", "topkeywords"):
        tabular_data = [
            (
                click.style(name, fg="cyan"),
                "https://platformio.org/lib/search?query=" + quote("keyword:%s" % name),
            )
            for name in result.get(key, [])
        ]
        table = tabulate(
            tabular_data,
            headers=[
                click.style(
                    ("RECENT" if key == "lastkeywords" else "POPULAR") + " KEYWORDS",
                    bold=True,
                ),
                "URL",
            ],
        )
        click.echo(table)
        click.echo()

    for key, title in (("dlday", "Today"), ("dlweek", "Week"), ("dlmonth", "Month")):
        tabular_data = [
            (
                click.style(item["name"], fg="cyan"),
                "https://platformio.org/lib/show/%s/%s"
                % (item["id"], quote(item["name"])),
            )
            for item in result.get(key, [])
        ]
        table = tabulate(
            tabular_data,
            headers=[click.style("FEATURED: " + title.upper(), bold=True), "URL"],
        )
        click.echo(table)
        click.echo()

    return True


def print_storage_header(storage_dirs, storage_dir):
    if storage_dirs and storage_dirs[0] != storage_dir:
        click.echo("")
    click.echo(
        click.style("Library Storage: ", bold=True)
        + click.style(storage_dir, fg="blue")
    )


def print_lib_item(item):
    click.secho(item["name"], fg="cyan")
    click.echo("=" * len(item["name"]))
    if "id" in item:
        click.secho("#ID: %d" % item["id"], bold=True)
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
        click.echo(
            "Compatible %s: %s"
            % (
                key,
                ", ".join(
                    [i["title"] if isinstance(i, dict) else i for i in item[key]]
                ),
            )
        )

    if "authors" in item or "authornames" in item:
        click.echo(
            "Authors: %s"
            % ", ".join(
                item.get(
                    "authornames", [a.get("name", "") for a in item.get("authors", [])]
                )
            )
        )

    if "__src_url" in item:
        click.secho("Source: %s" % item["__src_url"])
    click.echo()

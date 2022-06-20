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
import logging
import os

import click

from platformio import exception, fs
from platformio.cli import PlatformioCLI
from platformio.package.commands.install import package_install_cmd
from platformio.package.commands.list import package_list_cmd
from platformio.package.commands.search import package_search_cmd
from platformio.package.commands.show import package_show_cmd
from platformio.package.commands.uninstall import package_uninstall_cmd
from platformio.package.commands.update import package_update_cmd
from platformio.package.exception import NotGlobalLibDir
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.meta import PackageItem, PackageSpec
from platformio.proc import is_ci
from platformio.project.config import ProjectConfig
from platformio.project.helpers import get_project_dir, is_platformio_project

CTX_META_INPUT_DIRS_KEY = __name__ + ".input_dirs"
CTX_META_PROJECT_ENVIRONMENTS_KEY = __name__ + ".project_environments"
CTX_META_STORAGE_DIRS_KEY = __name__ + ".storage_dirs"
CTX_META_STORAGE_LIBDEPS_KEY = __name__ + ".storage_lib_deps"


def get_project_global_lib_dir():
    return ProjectConfig.get_instance().get("platformio", "globallib_dir")


def invoke_command(ctx, cmd, **kwargs):
    input_dirs = ctx.meta.get(CTX_META_INPUT_DIRS_KEY, [])
    project_environments = ctx.meta[CTX_META_PROJECT_ENVIRONMENTS_KEY]
    for input_dir in input_dirs:
        cmd_kwargs = kwargs.copy()
        if is_platformio_project(input_dir):
            cmd_kwargs["project_dir"] = input_dir
            cmd_kwargs["environments"] = project_environments
        else:
            cmd_kwargs["global"] = True
            cmd_kwargs["storage_dir"] = input_dir
        ctx.invoke(cmd, **cmd_kwargs)


@click.group(short_help="Library manager", hidden=True)
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
    in_silence = PlatformioCLI.in_silence()
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
            libdeps_dir = config.get("platformio", "libdeps_dir")
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
    click.secho(
        "\nWARNING: This command is deprecated and will be removed in "
        "the next releases. \nPlease use `pio pkg install` instead.\n",
        fg="yellow",
    )
    return invoke_command(
        ctx,
        package_install_cmd,
        libraries=libraries,
        no_save=not save,
        force=force,
        silent=silent,
    )


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
    click.secho(
        "\nWARNING: This command is deprecated and will be removed in "
        "the next releases. \nPlease use `pio pkg uninstall` instead.\n",
        fg="yellow",
    )
    invoke_command(
        ctx,
        package_uninstall_cmd,
        libraries=libraries,
        no_save=not save,
        silent=silent,
    )


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
    only_check = dry_run or only_check
    if only_check and not json_output:
        raise exception.UserSideException(
            "This command is deprecated, please use `pio pkg outdated` instead"
        )

    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg update` instead.\n",
            fg="yellow",
        )
        return invoke_command(
            ctx,
            package_update_cmd,
            libraries=libraries,
            silent=silent,
        )

    storage_dirs = ctx.meta[CTX_META_STORAGE_DIRS_KEY]
    json_result = {}
    for storage_dir in storage_dirs:
        lib_deps = ctx.meta.get(CTX_META_STORAGE_LIBDEPS_KEY, {}).get(storage_dir, [])
        lm = LibraryPackageManager(storage_dir)
        lm.set_log_level(logging.WARN if silent else logging.DEBUG)
        _libraries = libraries or lib_deps or lm.get_installed()

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

    return click.echo(
        json.dumps(
            json_result[storage_dirs[0]] if len(storage_dirs) == 1 else json_result
        )
    )


@cli.command("list", short_help="List installed libraries")
@click.option("--json-output", is_flag=True)
@click.pass_context
def lib_list(ctx, json_output):
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg list` instead.\n",
            fg="yellow",
        )
        return invoke_command(ctx, package_list_cmd, only_libraries=True)

    storage_dirs = ctx.meta[CTX_META_STORAGE_DIRS_KEY]
    json_result = {}
    for storage_dir in storage_dirs:
        lm = LibraryPackageManager(storage_dir)
        json_result[storage_dir] = lm.legacy_get_installed()
    return click.echo(
        json.dumps(
            json_result[storage_dirs[0]] if len(storage_dirs) == 1 else json_result
        )
    )


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
@click.pass_context
def lib_search(  # pylint: disable=unused-argument
    ctx, query, json_output, page, noninteractive, **filters
):
    if not query:
        query = []
    if not isinstance(query, list):
        query = list(query)

    for key, values in filters.items():
        for value in values:
            query.append('%s:"%s"' % (key, value))

    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg search` instead.\n",
            fg="yellow",
        )
        query.append("type:library")
        return ctx.invoke(package_search_cmd, query=" ".join(query), page=page)

    regclient = LibraryPackageManager().get_registry_client_instance()
    result = regclient.fetch_json_data(
        "get",
        "/v2/lib/search",
        params=dict(query=" ".join(query), page=page),
        x_cache_valid="1d",
    )
    return click.echo(json.dumps(result))


@cli.command("builtin", short_help="List built-in libraries")
@click.option("--storage", multiple=True)
@click.option("--json-output", is_flag=True)
def lib_builtin(storage, json_output):
    items = LibraryPackageManager.get_builtin_libs(storage)
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
@click.pass_context
def lib_show(ctx, library, json_output):
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg show` instead.\n",
            fg="yellow",
        )
        return ctx.invoke(package_show_cmd, pkg_type="library", spec=library)

    lm = LibraryPackageManager()
    lm.set_log_level(logging.ERROR if json_output else logging.DEBUG)
    lib_id = lm.reveal_registry_package_id(library)
    regclient = lm.get_registry_client_instance()
    lib = regclient.fetch_json_data(
        "get", "/v2/lib/info/%d" % lib_id, x_cache_valid="1h"
    )
    return click.echo(json.dumps(lib))


@cli.command("register", short_help="Deprecated")
@click.argument("config_url")
def lib_register(config_url):  # pylint: disable=unused-argument
    raise exception.UserSideException(
        "This command is deprecated. Please use `pio pkg publish` command."
    )


@cli.command("stats", short_help="Library Registry Statistics")
@click.option("--json-output", is_flag=True)
def lib_stats(json_output):
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease visit "
            "https://registry.platformio.org\n",
            fg="yellow",
        )
        return None

    regclient = LibraryPackageManager().get_registry_client_instance()
    result = regclient.fetch_json_data("get", "/v2/lib/stats", x_cache_valid="1h")
    return click.echo(json.dumps(result))


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
            click.echo("%s: %s" % (key.capitalize(), ", ".join(item[key])))
        else:
            click.echo("%s: %s" % (key.capitalize(), item[key]))

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

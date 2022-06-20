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

import json
import logging
import os

import click

from platformio.exception import UserSideException
from platformio.package.commands.install import package_install_cmd
from platformio.package.commands.list import package_list_cmd
from platformio.package.commands.search import package_search_cmd
from platformio.package.commands.show import package_show_cmd
from platformio.package.commands.uninstall import package_uninstall_cmd
from platformio.package.commands.update import package_update_cmd
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.meta import PackageItem, PackageSpec
from platformio.package.version import get_original_version
from platformio.platform.exception import UnknownPlatform
from platformio.platform.factory import PlatformFactory


@click.group(short_help="Platform manager", hidden=True)
def cli():
    pass


@cli.command("search", short_help="Search for development platform")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
@click.pass_context
def platform_search(ctx, query, json_output):
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg search` instead.\n",
            fg="yellow",
        )
        query = query or ""
        return ctx.invoke(package_search_cmd, query=f"type:platform {query}".strip())

    platforms = []
    for platform in _get_registry_platforms():
        if query == "all":
            query = ""
        search_data = json.dumps(platform)
        if query and query.lower() not in search_data.lower():
            continue
        platforms.append(
            _get_registry_platform_data(
                platform["name"], with_boards=False, expose_packages=False
            )
        )
    click.echo(json.dumps(platforms))
    return None


@cli.command("frameworks", short_help="List supported frameworks, SDKs")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def platform_frameworks(query, json_output):
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease visit https://docs.platformio.org"
            "/en/latest/frameworks/index.html\n",
            fg="yellow",
        )
        return

    regclient = PlatformPackageManager().get_registry_client_instance()
    frameworks = []
    for framework in regclient.fetch_json_data(
        "get", "/v2/frameworks", x_cache_valid="1d"
    ):
        if query == "all":
            query = ""
        search_data = json.dumps(framework)
        if query and query.lower() not in search_data.lower():
            continue
        framework["homepage"] = "https://platformio.org/frameworks/" + framework["name"]
        framework["platforms"] = [
            platform["name"]
            for platform in _get_registry_platforms()
            if framework["name"] in platform["frameworks"]
        ]
        frameworks.append(framework)

    frameworks = sorted(frameworks, key=lambda manifest: manifest["name"])
    click.echo(json.dumps(frameworks))


@cli.command("list", short_help="List installed development platforms")
@click.option("--json-output", is_flag=True)
@click.pass_context
def platform_list(ctx, json_output):
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg list` instead.\n",
            fg="yellow",
        )
        return ctx.invoke(package_list_cmd, **{"global": True, "only_platforms": True})

    platforms = []
    pm = PlatformPackageManager()
    for pkg in pm.get_installed():
        platforms.append(
            _get_installed_platform_data(pkg, with_boards=False, expose_packages=False)
        )

    platforms = sorted(platforms, key=lambda manifest: manifest["name"])
    click.echo(json.dumps(platforms))
    return None


@cli.command("show", short_help="Show details about development platform")
@click.argument("platform")
@click.option("--json-output", is_flag=True)
@click.pass_context
def platform_show(ctx, platform, json_output):  # pylint: disable=too-many-branches
    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg show` instead.\n",
            fg="yellow",
        )
        return ctx.invoke(package_show_cmd, pkg_type="platform", spec=platform)

    data = _get_platform_data(platform)
    if not data:
        raise UnknownPlatform(platform)
    return click.echo(json.dumps(data))


@cli.command("install", short_help="Install new development platform")
@click.argument("platforms", nargs=-1, required=True, metavar="[PLATFORM...]")
@click.option("--with-package", multiple=True)
@click.option("--without-package", multiple=True)
@click.option("--skip-default-package", is_flag=True)
@click.option("--with-all-packages", is_flag=True)
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Reinstall/redownload dev/platform and its packages if exist",
)
@click.pass_context
def platform_install(  # pylint: disable=too-many-arguments
    ctx,
    platforms,
    with_package,
    without_package,
    skip_default_package,
    with_all_packages,
    silent,
    force,
):
    click.secho(
        "\nWARNING: This command is deprecated and will be removed in "
        "the next releases. \nPlease use `pio pkg install` instead.\n",
        fg="yellow",
    )
    ctx.invoke(
        package_install_cmd,
        **{
            "global": True,
            "platforms": platforms,
            "skip_dependencies": (
                not with_all_packages
                and (with_package or without_package or skip_default_package)
            ),
            "silent": silent,
            "force": force,
        },
    )


@cli.command("uninstall", short_help="Uninstall development platform")
@click.argument("platforms", nargs=-1, required=True, metavar="[PLATFORM...]")
@click.pass_context
def platform_uninstall(ctx, platforms):
    click.secho(
        "\nWARNING: This command is deprecated and will be removed in "
        "the next releases. \nPlease use `pio pkg uninstall` instead.\n",
        fg="yellow",
    )
    ctx.invoke(
        package_uninstall_cmd,
        **{
            "global": True,
            "platforms": platforms,
        },
    )


@cli.command("update", short_help="Update installed development platforms")
@click.argument("platforms", nargs=-1, required=False, metavar="[PLATFORM...]")
@click.option(
    "-p", "--only-packages", is_flag=True, help="Update only the platform packages"
)
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
def platform_update(  # pylint: disable=too-many-locals, too-many-arguments
    ctx, platforms, only_check, dry_run, silent, json_output, **_
):
    only_check = dry_run or only_check

    if only_check and not json_output:
        raise UserSideException(
            "This command is deprecated, please use `pio pkg outdated` instead"
        )

    if not json_output:
        click.secho(
            "\nWARNING: This command is deprecated and will be removed in "
            "the next releases. \nPlease use `pio pkg update` instead.\n",
            fg="yellow",
        )
        return ctx.invoke(
            package_update_cmd,
            **{
                "global": True,
                "platforms": platforms,
                "silent": silent,
            },
        )

    pm = PlatformPackageManager()
    pm.set_log_level(logging.WARN if silent else logging.DEBUG)
    platforms = platforms or pm.get_installed()
    result = []
    for platform in platforms:
        spec = None
        pkg = None
        if isinstance(platform, PackageItem):
            pkg = platform
        else:
            spec = PackageSpec(platform)
            pkg = pm.get_package(spec)
        if not pkg:
            continue
        outdated = pm.outdated(pkg, spec)
        if (
            not outdated.is_outdated(allow_incompatible=True)
            and not PlatformFactory.new(pkg).are_outdated_packages()
        ):
            continue
        data = _get_installed_platform_data(
            pkg, with_boards=False, expose_packages=False
        )
        if outdated.is_outdated(allow_incompatible=True):
            data["versionLatest"] = str(outdated.latest) if outdated.latest else None
        result.append(data)
    click.echo(json.dumps(result))
    return True


#
# Helpers
#


def _get_registry_platforms():
    regclient = PlatformPackageManager().get_registry_client_instance()
    return regclient.fetch_json_data("get", "/v2/platforms", x_cache_valid="1d")


def _get_platform_data(*args, **kwargs):
    try:
        return _get_installed_platform_data(*args, **kwargs)
    except UnknownPlatform:
        return _get_registry_platform_data(*args, **kwargs)


def _get_installed_platform_data(platform, with_boards=True, expose_packages=True):
    p = PlatformFactory.new(platform)
    data = dict(
        name=p.name,
        title=p.title,
        description=p.description,
        version=p.version,
        homepage=p.homepage,
        url=p.homepage,
        repository=p.repository_url,
        license=p.license,
        forDesktop=not p.is_embedded(),
        frameworks=sorted(list(p.frameworks) if p.frameworks else []),
        packages=list(p.packages) if p.packages else [],
    )

    # if dump to API
    # del data['version']
    # return data

    # overwrite VCS version and add extra fields
    manifest = PlatformPackageManager().legacy_load_manifest(
        os.path.dirname(p.manifest_path)
    )
    assert manifest
    for key in manifest:
        if key == "version" or key.startswith("__"):
            data[key] = manifest[key]

    if with_boards:
        data["boards"] = [c.get_brief_data() for c in p.get_boards().values()]

    if not data["packages"] or not expose_packages:
        return data

    data["packages"] = []
    installed_pkgs = {
        pkg.metadata.name: p.pm.load_manifest(pkg) for pkg in p.get_installed_packages()
    }
    for name, options in p.packages.items():
        item = dict(
            name=name,
            type=p.get_package_type(name),
            requirements=options.get("version"),
            optional=options.get("optional") is True,
        )
        if name in installed_pkgs:
            for key, value in installed_pkgs[name].items():
                if key not in ("url", "version", "description"):
                    continue
                item[key] = value
                if key == "version":
                    item["originalVersion"] = get_original_version(value)
        data["packages"].append(item)

    return data


def _get_registry_platform_data(  # pylint: disable=unused-argument
    platform, with_boards=True, expose_packages=True
):
    _data = None
    for p in _get_registry_platforms():
        if p["name"] == platform:
            _data = p
            break

    if not _data:
        return None

    data = dict(
        ownername=_data.get("ownername"),
        name=_data["name"],
        title=_data["title"],
        description=_data["description"],
        homepage=_data["homepage"],
        repository=_data["repository"],
        url=_data["url"],
        license=_data["license"],
        forDesktop=_data["forDesktop"],
        frameworks=_data["frameworks"],
        packages=_data["packages"],
        versions=_data.get("versions"),
    )

    if with_boards:
        data["boards"] = [
            board
            for board in PlatformPackageManager().get_registered_boards()
            if board["platform"] == _data["name"]
        ]

    return data

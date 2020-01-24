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

from os.path import dirname, isdir

import click

from platformio import app, exception, util
from platformio.commands.boards import print_boards
from platformio.compat import dump_json_to_unicode
from platformio.managers.platform import PlatformFactory, PlatformManager
from platformio.package.pack import PackagePacker


@click.group(short_help="Platform Manager")
def cli():
    pass


def _print_platforms(platforms):
    for platform in platforms:
        click.echo(
            "{name} ~ {title}".format(
                name=click.style(platform["name"], fg="cyan"), title=platform["title"]
            )
        )
        click.echo("=" * (3 + len(platform["name"] + platform["title"])))
        click.echo(platform["description"])
        click.echo()
        if "homepage" in platform:
            click.echo("Home: %s" % platform["homepage"])
        if "frameworks" in platform and platform["frameworks"]:
            click.echo("Frameworks: %s" % ", ".join(platform["frameworks"]))
        if "packages" in platform:
            click.echo("Packages: %s" % ", ".join(platform["packages"]))
        if "version" in platform:
            if "__src_url" in platform:
                click.echo(
                    "Version: #%s (%s)" % (platform["version"], platform["__src_url"])
                )
            else:
                click.echo("Version: " + platform["version"])
        click.echo()


def _get_registry_platforms():
    platforms = util.get_api_result("/platforms", cache_valid="7d")
    pm = PlatformManager()
    for platform in platforms or []:
        platform["versions"] = pm.get_all_repo_versions(platform["name"])
    return platforms


def _get_platform_data(*args, **kwargs):
    try:
        return _get_installed_platform_data(*args, **kwargs)
    except exception.UnknownPlatform:
        return _get_registry_platform_data(*args, **kwargs)


def _get_installed_platform_data(platform, with_boards=True, expose_packages=True):
    p = PlatformFactory.newPlatform(platform)
    data = dict(
        name=p.name,
        title=p.title,
        description=p.description,
        version=p.version,
        homepage=p.homepage,
        repository=p.repository_url,
        url=p.vendor_url,
        docs=p.docs_url,
        license=p.license,
        forDesktop=not p.is_embedded(),
        frameworks=sorted(list(p.frameworks) if p.frameworks else []),
        packages=list(p.packages) if p.packages else [],
    )

    # if dump to API
    # del data['version']
    # return data

    # overwrite VCS version and add extra fields
    manifest = PlatformManager().load_manifest(dirname(p.manifest_path))
    assert manifest
    for key in manifest:
        if key == "version" or key.startswith("__"):
            data[key] = manifest[key]

    if with_boards:
        data["boards"] = [c.get_brief_data() for c in p.get_boards().values()]

    if not data["packages"] or not expose_packages:
        return data

    data["packages"] = []
    installed_pkgs = p.get_installed_packages()
    for name, opts in p.packages.items():
        item = dict(
            name=name,
            type=p.get_package_type(name),
            requirements=opts.get("version"),
            optional=opts.get("optional") is True,
        )
        if name in installed_pkgs:
            for key, value in installed_pkgs[name].items():
                if key not in ("url", "version", "description"):
                    continue
                item[key] = value
                if key == "version":
                    item["originalVersion"] = util.get_original_version(value)
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
        versions=_data["versions"],
    )

    if with_boards:
        data["boards"] = [
            board
            for board in PlatformManager().get_registered_boards()
            if board["platform"] == _data["name"]
        ]

    return data


@cli.command("search", short_help="Search for development platform")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def platform_search(query, json_output):
    platforms = []
    for platform in _get_registry_platforms():
        if query == "all":
            query = ""
        search_data = dump_json_to_unicode(platform)
        if query and query.lower() not in search_data.lower():
            continue
        platforms.append(
            _get_registry_platform_data(
                platform["name"], with_boards=False, expose_packages=False
            )
        )

    if json_output:
        click.echo(dump_json_to_unicode(platforms))
    else:
        _print_platforms(platforms)


@cli.command("frameworks", short_help="List supported frameworks, SDKs")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def platform_frameworks(query, json_output):
    frameworks = []
    for framework in util.get_api_result("/frameworks", cache_valid="7d"):
        if query == "all":
            query = ""
        search_data = dump_json_to_unicode(framework)
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
    if json_output:
        click.echo(dump_json_to_unicode(frameworks))
    else:
        _print_platforms(frameworks)


@cli.command("list", short_help="List installed development platforms")
@click.option("--json-output", is_flag=True)
def platform_list(json_output):
    platforms = []
    pm = PlatformManager()
    for manifest in pm.get_installed():
        platforms.append(
            _get_installed_platform_data(
                manifest["__pkg_dir"], with_boards=False, expose_packages=False
            )
        )

    platforms = sorted(platforms, key=lambda manifest: manifest["name"])
    if json_output:
        click.echo(dump_json_to_unicode(platforms))
    else:
        _print_platforms(platforms)


@cli.command("show", short_help="Show details about development platform")
@click.argument("platform")
@click.option("--json-output", is_flag=True)
def platform_show(platform, json_output):  # pylint: disable=too-many-branches
    data = _get_platform_data(platform)
    if not data:
        raise exception.UnknownPlatform(platform)
    if json_output:
        return click.echo(dump_json_to_unicode(data))

    click.echo(
        "{name} ~ {title}".format(
            name=click.style(data["name"], fg="cyan"), title=data["title"]
        )
    )
    click.echo("=" * (3 + len(data["name"] + data["title"])))
    click.echo(data["description"])
    click.echo()
    if "version" in data:
        click.echo("Version: %s" % data["version"])
    if data["homepage"]:
        click.echo("Home: %s" % data["homepage"])
    if data["repository"]:
        click.echo("Repository: %s" % data["repository"])
    if data["url"]:
        click.echo("Vendor: %s" % data["url"])
    if data["license"]:
        click.echo("License: %s" % data["license"])
    if data["frameworks"]:
        click.echo("Frameworks: %s" % ", ".join(data["frameworks"]))

    if not data["packages"]:
        return None

    if not isinstance(data["packages"][0], dict):
        click.echo("Packages: %s" % ", ".join(data["packages"]))
    else:
        click.echo()
        click.secho("Packages", bold=True)
        click.echo("--------")
        for item in data["packages"]:
            click.echo()
            click.echo("Package %s" % click.style(item["name"], fg="yellow"))
            click.echo("-" * (8 + len(item["name"])))
            if item["type"]:
                click.echo("Type: %s" % item["type"])
            click.echo("Requirements: %s" % item["requirements"])
            click.echo(
                "Installed: %s" % ("Yes" if item.get("version") else "No (optional)")
            )
            if "version" in item:
                click.echo("Version: %s" % item["version"])
            if "originalVersion" in item:
                click.echo("Original version: %s" % item["originalVersion"])
            if "description" in item:
                click.echo("Description: %s" % item["description"])

    if data["boards"]:
        click.echo()
        click.secho("Boards", bold=True)
        click.echo("------")
        print_boards(data["boards"])

    return True


@cli.command("install", short_help="Install new development platform")
@click.argument("platforms", nargs=-1, required=True, metavar="[PLATFORM...]")
@click.option("--with-package", multiple=True)
@click.option("--without-package", multiple=True)
@click.option("--skip-default-package", is_flag=True)
@click.option("--with-all-packages", is_flag=True)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Reinstall/redownload dev/platform and its packages if exist",
)
def platform_install(  # pylint: disable=too-many-arguments
    platforms,
    with_package,
    without_package,
    skip_default_package,
    with_all_packages,
    force,
):
    pm = PlatformManager()
    for platform in platforms:
        if pm.install(
            name=platform,
            with_packages=with_package,
            without_packages=without_package,
            skip_default_package=skip_default_package,
            with_all_packages=with_all_packages,
            force=force,
        ):
            click.secho(
                "The platform '%s' has been successfully installed!\n"
                "The rest of packages will be installed automatically "
                "depending on your build environment." % platform,
                fg="green",
            )


@cli.command("uninstall", short_help="Uninstall development platform")
@click.argument("platforms", nargs=-1, required=True, metavar="[PLATFORM...]")
def platform_uninstall(platforms):
    pm = PlatformManager()
    for platform in platforms:
        if pm.uninstall(platform):
            click.secho(
                "The platform '%s' has been successfully uninstalled!" % platform,
                fg="green",
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
@click.option("--json-output", is_flag=True)
def platform_update(  # pylint: disable=too-many-locals
    platforms, only_packages, only_check, dry_run, json_output
):
    pm = PlatformManager()
    pkg_dir_to_name = {}
    if not platforms:
        platforms = []
        for manifest in pm.get_installed():
            platforms.append(manifest["__pkg_dir"])
            pkg_dir_to_name[manifest["__pkg_dir"]] = manifest.get(
                "title", manifest["name"]
            )

    only_check = dry_run or only_check

    if only_check and json_output:
        result = []
        for platform in platforms:
            pkg_dir = platform if isdir(platform) else None
            requirements = None
            url = None
            if not pkg_dir:
                name, requirements, url = pm.parse_pkg_uri(platform)
                pkg_dir = pm.get_package_dir(name, requirements, url)
            if not pkg_dir:
                continue
            latest = pm.outdated(pkg_dir, requirements)
            if (
                not latest
                and not PlatformFactory.newPlatform(pkg_dir).are_outdated_packages()
            ):
                continue
            data = _get_installed_platform_data(
                pkg_dir, with_boards=False, expose_packages=False
            )
            if latest:
                data["versionLatest"] = latest
            result.append(data)
        return click.echo(dump_json_to_unicode(result))

    # cleanup cached board and platform lists
    app.clean_cache()
    for platform in platforms:
        click.echo(
            "Platform %s"
            % click.style(pkg_dir_to_name.get(platform, platform), fg="cyan")
        )
        click.echo("--------")
        pm.update(platform, only_packages=only_packages, only_check=only_check)
        click.echo()

    return True


@cli.command(
    "pack", short_help="Create a tarball from development platform/tool package"
)
@click.argument("package", required=True, metavar="[source directory, tar.gz or zip]")
def platform_pack(package):
    p = PackagePacker(package)
    tarball_path = p.pack()
    click.secho('Wrote a tarball to "%s"' % tarball_path, fg="green")

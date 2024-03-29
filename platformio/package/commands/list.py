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
import os

import click

from platformio import fs
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageInfo, PackageItem, PackageSpec
from platformio.platform.exception import UnknownPlatform
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig


@click.command("list", short_help="List project packages")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option("-p", "--platform", "platforms", metavar="SPECIFICATION", multiple=True)
@click.option("-t", "--tool", "tools", metavar="SPECIFICATION", multiple=True)
@click.option("-l", "--library", "libraries", metavar="SPECIFICATION", multiple=True)
@click.option("-g", "--global", is_flag=True, help="List globally installed packages")
@click.option(
    "--storage-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Custom Package Manager storage for global packages",
)
@click.option("--only-platforms", is_flag=True, help="List only platform packages")
@click.option("--only-tools", is_flag=True, help="List only tool packages")
@click.option("--only-libraries", is_flag=True, help="List only library packages")
@click.option("--json-output", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
def package_list_cmd(**options):
    data = (
        list_global_packages(options)
        if options.get("global")
        else list_project_packages(options)
    )

    if options.get("json_output"):
        return click.echo(_dump_to_json(data, options))

    def _print_items(typex, items):
        click.secho(typex.capitalize(), bold=True)
        print_dependency_tree(items, verbose=options.get("verbose"))
        click.echo()

    if options.get("global"):
        for typex, items in data.items():
            _print_items(typex, items)
    else:
        for env, env_data in data.items():
            click.echo("Resolving %s dependencies..." % click.style(env, fg="cyan"))
            for typex, items in env_data.items():
                _print_items(typex, items)

    return None


def _dump_to_json(data, options):
    result = {}

    if options.get("global"):
        for typex, items in data.items():
            result[typex] = [info.as_dict(with_manifest=True) for info in items]
    else:
        for env, env_data in data.items():
            result[env] = {}
            for typex, items in env_data.items():
                result[env][typex] = [
                    info.as_dict(with_manifest=True) for info in items
                ]
    return json.dumps(result)


def build_package_info(pm, specs=None, filter_specs=None, resolve_dependencies=True):
    filtered_pkgs = [
        pm.get_package(spec) for spec in filter_specs if pm.get_package(spec)
    ]
    candidates = []
    if specs:
        for spec in specs:
            candidates.append(
                PackageInfo(
                    spec if isinstance(spec, PackageSpec) else PackageSpec(spec),
                    pm.get_package(spec),
                )
            )
    else:
        candidates = [PackageInfo(pkg.metadata.spec, pkg) for pkg in pm.get_installed()]
    if not candidates:
        return []

    candidates = sorted(
        candidates,
        key=lambda info: info.item.metadata.name if info.item else info.spec.humanize(),
    )

    result = []
    for info in candidates:
        if filter_specs and (
            not info.item or not _pkg_tree_contains(pm, info.item, filtered_pkgs)
        ):
            continue
        if not info.item:
            if not info.spec.external and not info.spec.owner:  # built-in library?
                continue
            result.append(info)
            continue

        visited_pkgs = pm.memcache_get("__visited_pkgs", [])
        if visited_pkgs and info.item.path in visited_pkgs:
            continue
        visited_pkgs.append(info.item.path)
        pm.memcache_set("__visited_pkgs", visited_pkgs)

        result.append(
            PackageInfo(
                info.spec,
                info.item,
                (
                    build_package_info(
                        pm,
                        specs=[
                            pm.dependency_to_spec(item)
                            for item in pm.get_pkg_dependencies(info.item)
                        ],
                        filter_specs=filter_specs,
                        resolve_dependencies=True,
                    )
                    if resolve_dependencies and pm.get_pkg_dependencies(info.item)
                    else []
                ),
            )
        )

    return result


def _pkg_tree_contains(pm, root: PackageItem, children: list[PackageItem]):
    if root in children:
        return True
    for dependency in pm.get_pkg_dependencies(root) or []:
        pkg = pm.get_package(pm.dependency_to_spec(dependency))
        if pkg and _pkg_tree_contains(pm, pkg, children):
            return True
    return False


def list_global_packages(options):
    data = [
        ("platforms", PlatformPackageManager(options.get("storage_dir"))),
        ("tools", ToolPackageManager(options.get("storage_dir"))),
        ("libraries", LibraryPackageManager(options.get("storage_dir"))),
    ]
    only_packages = any(
        options.get(typex) or options.get(f"only_{typex}") for (typex, _) in data
    )
    result = {}
    for typex, pm in data:
        skip_conds = [
            only_packages
            and not options.get(typex)
            and not options.get(f"only_{typex}"),
            not pm.get_installed(),
        ]
        if any(skip_conds):
            continue
        result[typex] = build_package_info(pm, filter_specs=options.get(typex))

    return result


def list_project_packages(options):
    environments = options["environments"]
    only_filtered_packages = any(
        options.get(typex) or options.get(f"only_{typex}")
        for typex in ("platforms", "tools", "libraries")
    )
    only_platform_package = options.get("platforms") or options.get("only_platforms")
    only_tool_packages = options.get("tools") or options.get("only_tools")
    only_library_packages = options.get("libraries") or options.get("only_libraries")

    result = {}
    with fs.cd(options["project_dir"]):
        config = ProjectConfig.get_instance()
        config.validate(environments)
        for env in config.envs():
            if environments and env not in environments:
                continue
            result[env] = {}
            if not only_filtered_packages or only_platform_package:
                result[env]["platforms"] = list_project_env_platform_package(
                    env, options
                )
            if not only_filtered_packages or only_tool_packages:
                result[env]["tools"] = list_project_env_tool_packages(env, options)
            if not only_filtered_packages or only_library_packages:
                result[env]["libraries"] = list_project_env_library_packages(
                    env, options
                )

    return result


def list_project_env_platform_package(project_env, options):
    pm = PlatformPackageManager()
    return build_package_info(
        pm,
        specs=[PackageSpec(pm.config.get(f"env:{project_env}", "platform"))],
        filter_specs=options.get("platforms"),
        resolve_dependencies=False,
    )


def list_project_env_tool_packages(project_env, options):
    try:
        p = PlatformFactory.from_env(project_env, targets=["upload"])
    except UnknownPlatform:
        return []

    return build_package_info(
        p.pm,
        specs=[
            p.get_package_spec(name)
            for name, options in p.packages.items()
            if not options.get("optional")
        ],
        filter_specs=options.get("tools"),
    )


def list_project_env_library_packages(project_env, options):
    config = ProjectConfig.get_instance()
    lib_deps = config.get(f"env:{project_env}", "lib_deps")
    lm = LibraryPackageManager(
        os.path.join(config.get("platformio", "libdeps_dir"), project_env)
    )
    return build_package_info(
        lm,
        lib_deps,
        filter_specs=options.get("libraries"),
    )


def humanize_package(info, verbose=False):
    data = (
        [
            click.style(info.item.metadata.name, fg="cyan"),
            click.style(f"@ {str(info.item.metadata.version)}", bold=True),
        ]
        if info.item
        else ["Not installed"]
    )
    extra_data = ["required: %s" % (info.spec.humanize() if info.spec else "Any")]
    if verbose and info.item:
        extra_data.append(info.item.path)
    data.append("(%s)" % ", ".join(extra_data))
    return " ".join(data)


def print_dependency_tree(items, verbose=False, level=0):
    for index, info in enumerate(items):
        click.echo(
            "%s%s %s"
            % (
                "│   " * level,
                "├──" if index < len(items) - 1 else "└──",
                humanize_package(
                    info,
                    verbose=verbose,
                ),
            )
        )
        if info.dependencies:
            print_dependency_tree(
                info.dependencies,
                verbose=verbose,
                level=level + 1,
            )

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

import os
from typing import List

import click

from platformio import fs
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageItem, PackageSpec
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig


@click.command("list", short_help="List installed packages")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option("-p", "--platform", "platforms", metavar="SPECIFICATION", multiple=True)
@click.option("-t", "--tool", "tools", metavar="SPECIFICATION", multiple=True)
@click.option("-l", "--library", "libraries", metavar="SPECIFICATION", multiple=True)
@click.option("-g", "--global", is_flag=True, help="List globally installed packages")
@click.option(
    "--storage-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Custom Package Manager storage for global packages",
)
@click.option("--only-platforms", is_flag=True, help="List only platform packages")
@click.option("--only-tools", is_flag=True, help="List only tool packages")
@click.option("--only-libraries", is_flag=True, help="List only library packages")
@click.option("-v", "--verbose", is_flag=True)
def package_list_cmd(**options):
    if options.get("global"):
        list_global_packages(options)
    else:
        list_project_packages(options)


def humanize_package(pkg, spec=None, verbose=False):
    if spec and not isinstance(spec, PackageSpec):
        spec = PackageSpec(spec)
    data = [
        click.style("{name} @ {version}".format(**pkg.metadata.as_dict()), fg="cyan")
    ]
    extra_data = ["required: %s" % (spec.humanize() if spec else "Any")]
    if verbose:
        extra_data.append(pkg.path)
    data.append("(%s)" % ", ".join(extra_data))
    return " ".join(data)


def print_dependency_tree(pm, specs=None, filter_specs=None, level=0, verbose=False):
    filtered_pkgs = [
        pm.get_package(spec) for spec in filter_specs or [] if pm.get_package(spec)
    ]
    candidates = {}
    if specs:
        for spec in specs:
            pkg = pm.get_package(spec)
            if not pkg:
                continue
            candidates[pkg.path] = (pkg, spec)
    else:
        candidates = {pkg.path: (pkg, pkg.metadata.spec) for pkg in pm.get_installed()}
    if not candidates:
        return
    candidates = sorted(candidates.values(), key=lambda item: item[0].metadata.name)

    for index, (pkg, spec) in enumerate(candidates):
        if filtered_pkgs and not _pkg_tree_contains(pm, pkg, filtered_pkgs):
            continue
        printed_pkgs = pm.memcache_get("__printed_pkgs", [])
        if printed_pkgs and pkg.path in printed_pkgs:
            continue
        printed_pkgs.append(pkg.path)
        pm.memcache_set("__printed_pkgs", printed_pkgs)

        click.echo(
            "%s%s %s"
            % (
                "│   " * level,
                "├──" if index < len(candidates) - 1 else "└──",
                humanize_package(
                    pkg,
                    spec=spec,
                    verbose=verbose,
                ),
            )
        )

        dependencies = pm.get_pkg_dependencies(pkg)
        if dependencies:
            print_dependency_tree(
                pm,
                specs=[pm.dependency_to_spec(item) for item in dependencies],
                filter_specs=filter_specs,
                level=level + 1,
                verbose=verbose,
            )


def _pkg_tree_contains(pm, root: PackageItem, children: List[PackageItem]):
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
        options.get(type_) or options.get(f"only_{type_}") for (type_, _) in data
    )
    for (type_, pm) in data:
        skip_conds = [
            only_packages
            and not options.get(type_)
            and not options.get(f"only_{type_}"),
            not pm.get_installed(),
        ]
        if any(skip_conds):
            continue
        click.secho(type_.capitalize(), bold=True)
        print_dependency_tree(
            pm, filter_specs=options.get(type_), verbose=options.get("verbose")
        )
        click.echo()


def list_project_packages(options):
    environments = options["environments"]
    only_packages = any(
        options.get(type_) or options.get(f"only_{type_}")
        for type_ in ("platforms", "tools", "libraries")
    )
    only_platform_packages = any(
        options.get(type_) or options.get(f"only_{type_}")
        for type_ in ("platforms", "tools")
    )
    only_library_packages = options.get("libraries") or options.get("only_libraries")

    with fs.cd(options["project_dir"]):
        config = ProjectConfig.get_instance()
        config.validate(environments)
        for env in config.envs():
            if environments and env not in environments:
                continue
            click.echo("Resolving %s dependencies..." % click.style(env, fg="cyan"))
            found = False
            if not only_packages or only_platform_packages:
                _found = print_project_env_platform_packages(env, options)
                found = found or _found
            if not only_packages or only_library_packages:
                _found = print_project_env_library_packages(env, options)
                found = found or _found
            if not found:
                click.echo("No packages")
            if (not environments and len(config.envs()) > 1) or len(environments) > 1:
                click.echo()


def print_project_env_platform_packages(project_env, options):
    config = ProjectConfig.get_instance()
    platform = config.get(f"env:{project_env}", "platform")
    if not platform:
        return None
    pkg = PlatformPackageManager().get_package(platform)
    if not pkg:
        return None
    click.echo(
        "Platform %s"
        % (humanize_package(pkg, platform, verbose=options.get("verbose")))
    )
    p = PlatformFactory.new(pkg)
    if project_env:
        p.configure_project_packages(project_env)
    print_dependency_tree(
        p.pm,
        specs=[p.get_package_spec(name) for name in p.packages],
        filter_specs=options.get("tools"),
    )
    click.echo()
    return True


def print_project_env_library_packages(project_env, options):
    config = ProjectConfig.get_instance()
    lib_deps = config.get(f"env:{project_env}", "lib_deps")
    lm = LibraryPackageManager(
        os.path.join(config.get("platformio", "libdeps_dir"), project_env)
    )
    if not lib_deps or not lm.get_installed():
        return None
    click.echo("Libraries")
    print_dependency_tree(
        lm,
        lib_deps,
        filter_specs=options.get("libraries"),
        verbose=options.get("verbose"),
    )
    return True

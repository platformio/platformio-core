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

import logging
import os

import click

from platformio import fs
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.project.config import ProjectConfig
from platformio.project.savedeps import save_project_dependencies


@click.command(
    "install", short_help="Install the project dependencies or custom packages"
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option("-p", "--platform", "platforms", multiple=True)
@click.option("-t", "--tool", "tools", multiple=True)
@click.option("-l", "--library", "libraries", multiple=True)
@click.option(
    "--no-save",
    is_flag=True,
    help="Prevent saving specified packages to `platformio.ini`",
)
@click.option("--skip-dependencies", is_flag=True, help="Skip package dependencies")
@click.option("-g", "--global", is_flag=True, help="Install package globally")
@click.option(
    "--storage-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Custom Package Manager storage for global packages",
)
@click.option("-f", "--force", is_flag=True, help="Reinstall package if it exists")
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
def package_install_cmd(**options):
    if options.get("global"):
        install_global_dependencies(options)
    else:
        install_project_dependencies(options)


def install_global_dependencies(options):
    pm = PlatformPackageManager(options.get("storage_dir"))
    tm = ToolPackageManager(options.get("storage_dir"))
    lm = LibraryPackageManager(options.get("storage_dir"))
    for obj in (pm, tm, lm):
        obj.set_log_level(logging.WARN if options.get("silent") else logging.DEBUG)
    for spec in options.get("platforms"):
        pm.install(
            spec,
            skip_default_package=options.get("skip_dependencies"),
            force=options.get("force"),
        )
    for spec in options.get("tools"):
        tm.install(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
            force=options.get("force"),
        )
    for spec in options.get("libraries", []):
        lm.install(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
            force=options.get("force"),
        )


def install_project_dependencies(options):
    environments = options["environments"]
    with fs.cd(options["project_dir"]):
        config = ProjectConfig.get_instance()
        config.validate(environments)
        for env in config.envs():
            if environments and env not in environments:
                continue
            if not options["silent"]:
                click.echo(
                    "Resolving %s environment packages..." % click.style(env, fg="cyan")
                )
            already_up_to_date = install_project_env_dependencies(env, options)
            if not options["silent"] and already_up_to_date:
                click.secho("Already up-to-date.", fg="green")


def install_project_env_dependencies(project_env, options=None):
    """Used in `pio run` -> Processor"""
    options = options or {}
    return any(
        [
            _install_project_env_platform(project_env, options),
            _install_project_env_libraries(project_env, options),
        ]
    )


def _install_project_env_platform(project_env, options):
    already_up_to_date = not options.get("force")
    config = ProjectConfig.get_instance()
    pm = PlatformPackageManager()
    if options.get("silent"):
        pm.set_log_level(logging.WARN)

    if options.get("platforms") or options.get("tools"):
        already_up_to_date = False
        tm = ToolPackageManager()
        if not options.get("silent"):
            pm.set_log_level(logging.DEBUG)
            tm.set_log_level(logging.DEBUG)
        for platform in options.get("platforms"):
            pm.install(
                platform,
                project_env=project_env,
                project_targets=options.get("project_targets"),
                skip_default_package=options.get("skip_dependencies"),
                force=options.get("force"),
            )
        for spec in options.get("tools"):
            tm.install(
                spec,
                skip_dependencies=options.get("skip_dependencies"),
                force=options.get("force"),
            )
        return not already_up_to_date

    if options.get("libraries"):
        return False

    # if not custom libraries, install declared platform
    platform = config.get(f"env:{project_env}", "platform")
    if platform:
        if not pm.get_package(platform):
            already_up_to_date = False
        PlatformPackageManager().install(
            platform,
            project_env=project_env,
            project_targets=options.get("project_targets"),
            skip_default_package=options.get("skip_dependencies"),
            force=options.get("force"),
        )
    return not already_up_to_date


def _install_project_env_libraries(project_env, options):
    already_up_to_date = not options.get("force")
    config = ProjectConfig.get_instance()
    lm = LibraryPackageManager(
        os.path.join(config.get("platformio", "libdeps_dir"), project_env)
    )
    if options.get("silent"):
        lm.set_log_level(logging.WARN)

    # custom libraries
    if options.get("libraries"):
        if not options.get("silent"):
            lm.set_log_level(logging.DEBUG)
        specs_to_save = []
        for library in options.get("libraries", []):
            spec = PackageSpec(library)
            pkg = lm.install(
                spec,
                skip_dependencies=options.get("skip_dependencies"),
                force=options.get("force"),
            )
            specs_to_save.append(_pkg_to_save_spec(pkg, spec))
        if not options.get("no_save") and specs_to_save:
            save_project_dependencies(
                os.getcwd(),
                specs_to_save,
                scope="lib_deps",
                action="add",
                environments=[project_env],
            )
        return not already_up_to_date

    if options.get("platforms") or options.get("tools"):
        return False

    # if not custom platforms/tools, install declared libraries
    for library in config.get(f"env:{project_env}", "lib_deps"):
        spec = PackageSpec(library)
        # skip built-in dependencies
        if not spec.external and not spec.owner:
            continue
        if not lm.get_package(spec):
            already_up_to_date = False
        lm.install(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
            force=options.get("force"),
        )
    return not already_up_to_date


def _pkg_to_save_spec(pkg, user_spec):
    assert isinstance(user_spec, PackageSpec)
    if user_spec.external:
        return user_spec
    return PackageSpec(
        owner=pkg.metadata.spec.owner,
        name=pkg.metadata.spec.name,
        requirements=user_spec.requirements
        or (
            ("^%s" % pkg.metadata.version)
            if not pkg.metadata.version.build
            else pkg.metadata.version
        ),
    )

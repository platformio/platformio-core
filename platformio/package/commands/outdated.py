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

import click
from tabulate import tabulate

from platformio import fs
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.meta import PackageSpec
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig


class OutdatedCandidate:
    def __init__(self, pm, pkg, spec, envs=None):
        self.pm = pm
        self.pkg = pkg
        self.spec = spec
        self.envs = envs or []
        self.outdated = None
        if not isinstance(self.envs, list):
            self.envs = [self.envs]

    def __eq__(self, other):
        return all(
            [
                self.pm.package_dir == other.pm.package_dir,
                self.pkg == other.pkg,
                self.spec == other.spec,
            ]
        )

    def check(self):
        self.outdated = self.pm.outdated(self.pkg, self.spec)

    def is_outdated(self):
        if not self.outdated:
            self.check()
        return self.outdated.is_outdated(allow_incompatible=self.pm.pkg_type != "tool")


@click.command("outdated", short_help="Check for outdated packages")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option("-e", "--environment", "environments", multiple=True)
def package_outdated_cmd(project_dir, environments):
    candidates = fetch_outdated_candidates(
        project_dir, environments, with_progress=True
    )
    print_outdated_candidates(candidates)


def print_outdated_candidates(candidates):
    if not candidates:
        click.secho("Everything is up-to-date!", fg="green")
        return
    tabulate_data = [
        (
            click.style(
                candidate.pkg.metadata.name,
                fg=get_candidate_update_color(candidate.outdated),
            ),
            candidate.outdated.current,
            candidate.outdated.wanted,
            click.style(candidate.outdated.latest, fg="cyan"),
            candidate.pm.pkg_type.capitalize(),
            ", ".join(set(candidate.envs)),
        )
        for candidate in candidates
    ]
    click.echo()
    click.secho("Semantic Versioning color legend:", bold=True)
    click.echo(
        tabulate(
            [
                (
                    click.style("<Major Update>", fg="red"),
                    "backward-incompatible updates",
                ),
                (
                    click.style("<Minor Update>", fg="yellow"),
                    "backward-compatible features",
                ),
                (
                    click.style("<Patch Update>", fg="green"),
                    "backward-compatible bug fixes",
                ),
            ],
            tablefmt="plain",
        )
    )
    click.echo()
    click.echo(
        tabulate(
            tabulate_data,
            headers=["Package", "Current", "Wanted", "Latest", "Type", "Environments"],
        )
    )


def get_candidate_update_color(outdated):
    if outdated.update_increment_type == outdated.UPDATE_INCREMENT_MAJOR:
        return "red"
    if outdated.update_increment_type == outdated.UPDATE_INCREMENT_MINOR:
        return "yellow"
    if outdated.update_increment_type == outdated.UPDATE_INCREMENT_PATCH:
        return "green"
    return None


def fetch_outdated_candidates(project_dir, environments, with_progress=False):
    candidates = []

    def _add_candidate(data):
        new_candidate = OutdatedCandidate(
            data["pm"], data["pkg"], data["spec"], data["env"]
        )
        for candidate in candidates:
            if candidate == new_candidate:
                candidate.envs.append(data["env"])
                return
        candidates.append(new_candidate)

    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
        config.validate(environments)

        # platforms
        for item in find_platform_candidates(config, environments):
            _add_candidate(item)
            # platform package dependencies
            for dep_item in find_platform_dependency_candidates(item):
                _add_candidate(dep_item)

        # libraries
        for item in find_library_candidates(config, environments):
            _add_candidate(item)

    result = []
    if not with_progress:
        for candidate in candidates:
            if candidate.is_outdated():
                result.append(candidate)
        return result

    with click.progressbar(candidates, label="Checking") as pb:
        for candidate in pb:
            if candidate.is_outdated():
                result.append(candidate)
    return result


def find_platform_candidates(config, environments):
    result = []
    pm = PlatformPackageManager()
    for env in config.envs():
        platform = config.get(f"env:{env}", "platform")
        if not platform or (environments and env not in environments):
            continue
        spec = PackageSpec(platform)
        pkg = pm.get_package(spec)
        if not pkg:
            continue
        result.append(dict(env=env, pm=pm, pkg=pkg, spec=spec))
    return result


def find_platform_dependency_candidates(platform_candidate):
    result = []
    p = PlatformFactory.new(platform_candidate["spec"])
    p.configure_project_packages(platform_candidate["env"])
    for pkg in p.get_installed_packages():
        result.append(
            dict(
                env=platform_candidate["env"],
                pm=p.pm,
                pkg=pkg,
                spec=p.get_package_spec(pkg.metadata.name),
            )
        )
    return sorted(result, key=lambda item: item["pkg"].metadata.name)


def find_library_candidates(config, environments):
    result = []
    for env in config.envs():
        if environments and env not in environments:
            continue
        package_dir = os.path.join(config.get("platformio", "libdeps_dir") or "", env)
        lib_deps = [
            item for item in config.get(f"env:{env}", "lib_deps", []) if "/" in item
        ]
        if not os.path.isdir(package_dir) or not lib_deps:
            continue
        pm = LibraryPackageManager(package_dir)
        for lib in lib_deps:
            spec = PackageSpec(lib)
            pkg = pm.get_package(spec)
            if not pkg:
                continue
            result.append(dict(env=env, pm=pm, pkg=pkg, spec=spec))
    return sorted(result, key=lambda item: item["pkg"].metadata.name)

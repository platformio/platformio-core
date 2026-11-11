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

from platformio import fs
from platformio.package.graph import iter_package_dependencies
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.meta import PackageSpec
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig


def _package_edges(manager, specs, parent=None):
    pending = [(parent, spec, manager.get_package(spec)) for spec in specs]
    visited = set()
    while pending:
        next_edges = []
        for source, spec, target in pending:
            yield source, manager.pkg_type, spec, target
            if target is None or target in visited:
                continue
            visited.add(target)
            next_edges.extend(
                (target, child_spec, child)
                for child_spec, child in iter_package_dependencies(manager, target)
            )
        pending = next_edges


def _environment_edges(config, env):
    section = f"env:{env}"
    platform_spec = config.get(section, "platform", None)
    if platform_spec:
        manager = PlatformPackageManager()
        spec = PackageSpec(platform_spec)
        package = manager.get_package(spec)
        yield None, manager.pkg_type, spec, package
        if package is not None:
            platform = PlatformFactory.from_env(env)
            required = [
                platform.get_package_spec(name)
                for name, options in platform.packages.items()
                if not options.get("optional")
            ]
            yield from _package_edges(platform.pm, required, parent=package)

    lib_deps = config.get(section, "lib_deps", [])
    if lib_deps:
        manager = LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), env)
        )
        yield from _package_edges(manager, map(PackageSpec, lib_deps))


def _environment_inventory(config, env):
    packages = {}
    dependencies = []
    for parent, kind, spec, package in _environment_edges(config, env):
        if package is not None and package not in packages:
            metadata = package.metadata
            packages[package] = {
                "id": len(packages) + 1,
                "type": kind,
                "name": metadata.name,
                "owner": metadata.spec.owner,
                "registry_id": metadata.spec.id,
                "version": str(metadata.version),
            }
        requested = spec.as_dict()
        # External sources can contain credentials or machine-specific paths.
        requested.pop("uri")
        if spec.external and not spec.has_custom_name():
            requested["name"] = None
        requested["external"] = spec.external
        dependencies.append(
            {
                "from": packages[parent]["id"] if parent is not None else None,
                "to": packages[package]["id"] if package is not None else None,
                "type": kind,
                "requested": requested,
            }
        )
    return {"packages": list(packages.values()), "dependencies": dependencies}


def collect_project_inventory(project_dir, environments):
    """Snapshot declared project packages using local installation state."""
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
        config.validate(environments, silent=True)
        return {
            env: _environment_inventory(config, env)
            for env in config.envs()
            if not environments or env in environments
        }

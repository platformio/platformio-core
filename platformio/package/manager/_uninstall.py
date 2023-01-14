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
import shutil

import click

from platformio import fs
from platformio.package.exception import UnknownPackageError
from platformio.package.meta import PackageItem, PackageSpec


class PackageManagerUninstallMixin:
    def uninstall(self, spec, skip_dependencies=False):
        try:
            self.lock()
            return self._uninstall(spec, skip_dependencies)
        finally:
            self.unlock()

    def _uninstall(self, spec, skip_dependencies=False):
        pkg = self.get_package(spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(spec)

        uninstalled_pkgs = self.memcache_get("__uninstalled_pkgs", [])
        if uninstalled_pkgs and pkg.path in uninstalled_pkgs:
            return pkg
        uninstalled_pkgs.append(pkg.path)
        self.memcache_set("__uninstalled_pkgs", uninstalled_pkgs)

        self.log.info(
            "Removing %s @ %s"
            % (click.style(pkg.metadata.name, fg="cyan"), pkg.metadata.version)
        )

        self.call_pkg_script(pkg, "preuninstall")

        # firstly, remove dependencies
        if not skip_dependencies:
            self.uninstall_dependencies(pkg)

        if pkg.metadata.spec.symlink:
            self.uninstall_symlink(pkg.metadata.spec)
        elif os.path.islink(pkg.path):
            os.unlink(pkg.path)
        else:
            fs.rmtree(pkg.path)
        self.memcache_reset()

        # unfix detached-package with the same name
        detached_pkg = self.get_package(PackageSpec(name=pkg.metadata.name))
        if (
            detached_pkg
            and "@" in detached_pkg.path
            and not os.path.isdir(
                os.path.join(self.package_dir, detached_pkg.get_safe_dirname())
            )
        ):
            shutil.move(
                detached_pkg.path,
                os.path.join(self.package_dir, detached_pkg.get_safe_dirname()),
            )
            self.memcache_reset()

        self.log.info(
            click.style(
                "{name}@{version} has been removed!".format(**pkg.metadata.as_dict()),
                fg="green",
            )
        )

        return pkg

    def uninstall_dependencies(self, pkg):
        assert isinstance(pkg, PackageItem)
        dependencies = self.get_pkg_dependencies(pkg)
        if not dependencies:
            return
        self.log.info("Removing dependencies...")
        for dependency in dependencies:
            pkg = self.get_package(self.dependency_to_spec(dependency))
            if not pkg:
                continue
            self._uninstall(pkg)

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
from platformio.package.meta import PackageSourceItem, PackageSpec


class PackageManagerUninstallMixin(object):
    def uninstall(self, pkg, silent=False, skip_dependencies=False):
        try:
            self.lock()
            return self._uninstall(pkg, silent, skip_dependencies)
        finally:
            self.unlock()

    def _uninstall(self, pkg, silent=False, skip_dependencies=False):
        if not isinstance(pkg, PackageSourceItem):
            pkg = (
                PackageSourceItem(pkg) if os.path.isdir(pkg) else self.get_package(pkg)
            )
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(pkg)

        if not silent:
            self.print_message(
                "Removing %s @ %s: \t"
                % (click.style(pkg.metadata.name, fg="cyan"), pkg.metadata.version),
                nl=False,
            )

        # firstly, remove dependencies
        if not skip_dependencies:
            self._uninstall_dependencies(pkg, silent)

        if os.path.islink(pkg.path):
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

        if not silent:
            click.echo("[%s]" % click.style("OK", fg="green"))

        return True

    def _uninstall_dependencies(self, pkg, silent=False):
        assert isinstance(pkg, PackageSourceItem)
        manifest = self.load_manifest(pkg)
        if not manifest.get("dependencies"):
            return
        if not silent:
            self.print_message(click.style("Removing dependencies...", fg="yellow"))
        for dependency in manifest.get("dependencies"):
            pkg = self.get_package(
                PackageSpec(
                    name=dependency.get("name"), requirements=dependency.get("version")
                )
            )
            if not pkg:
                continue
            self._uninstall(pkg, silent=silent)

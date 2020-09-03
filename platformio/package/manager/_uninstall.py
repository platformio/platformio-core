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
from platformio.package.meta import PackageSpec


class PackageManagerUninstallMixin(object):
    def uninstall(self, spec, silent=False, skip_dependencies=False):
        try:
            self.lock()
            return self._uninstall(spec, silent, skip_dependencies)
        finally:
            self.unlock()

    def _uninstall(self, spec, silent=False, skip_dependencies=False):
        pkg = self.get_package(spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(spec)

        if not silent:
            self.print_message(
                "Removing %s @ %s"
                % (click.style(pkg.metadata.name, fg="cyan"), pkg.metadata.version),
            )

        # firstly, remove dependencies
        if not skip_dependencies:
            self.uninstall_dependencies(pkg, silent)

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
            self.print_message(
                "{name} @ {version} has been removed!".format(**pkg.metadata.as_dict()),
                fg="green",
            )

        return pkg

    def uninstall_dependencies(self, pkg, silent=False):
        pass

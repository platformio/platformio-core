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

from platformio.package.exception import (
    MissingPackageManifestError,
    UnknownPackageError,
)
from platformio.package.manager.base import BasePackageManager
from platformio.package.meta import PackageItem, PackageSpec, PackageType
from platformio.project.helpers import get_project_global_lib_dir


class LibraryPackageManager(BasePackageManager):  # pylint: disable=too-many-ancestors
    def __init__(self, package_dir=None):
        super(LibraryPackageManager, self).__init__(
            PackageType.LIBRARY, package_dir or get_project_global_lib_dir()
        )

    @property
    def manifest_names(self):
        return PackageType.get_manifest_map()[PackageType.LIBRARY]

    def find_pkg_root(self, path, spec):
        try:
            return super(LibraryPackageManager, self).find_pkg_root(path, spec)
        except MissingPackageManifestError:
            pass
        assert isinstance(spec, PackageSpec)

        root_dir = self.find_library_root(path)

        # automatically generate library manifest
        with open(
            os.path.join(root_dir, "library.json"), mode="w", encoding="utf8"
        ) as fp:
            json.dump(
                dict(
                    name=spec.name,
                    version=self.generate_rand_version(),
                ),
                fp,
                indent=2,
            )

        return root_dir

    @staticmethod
    def find_library_root(path):
        root_dir_signs = set(["include", "Include", "src", "Src"])
        root_file_signs = set(
            [
                "conanfile.py",  # Conan-based library
                "CMakeLists.txt",  # CMake-based library
            ]
        )
        for root, dirs, files in os.walk(path):
            if not files and len(dirs) == 1:
                continue
            if set(root_dir_signs) & set(dirs):
                return root
            if set(root_file_signs) & set(files):
                return root
            for fname in files:
                if fname.endswith((".c", ".cpp", ".h", ".hpp", ".S")):
                    return root
        return path

    def _install(  # pylint: disable=too-many-arguments
        self,
        spec,
        search_filters=None,
        silent=False,
        skip_dependencies=False,
        force=False,
    ):
        try:
            return super(LibraryPackageManager, self)._install(
                spec,
                search_filters=search_filters,
                silent=silent,
                skip_dependencies=skip_dependencies,
                force=force,
            )
        except UnknownPackageError as e:
            # pylint: disable=import-outside-toplevel
            from platformio.commands.lib.helpers import is_builtin_lib

            spec = self.ensure_spec(spec)
            if is_builtin_lib(spec.name):
                self.print_message("Already installed, built-in library", fg="yellow")
                return True

            raise e

    def install_dependencies(self, pkg, silent=False):
        assert isinstance(pkg, PackageItem)
        manifest = self.load_manifest(pkg)
        if not manifest.get("dependencies"):
            return
        if not silent:
            self.print_message("Installing dependencies...")
        for dependency in manifest.get("dependencies"):
            if not self._install_dependency(dependency, silent) and not silent:
                self.print_message(
                    "Warning! Could not install dependency %s for package '%s'"
                    % (dependency, pkg.metadata.name),
                    fg="yellow",
                )

    def _install_dependency(self, dependency, silent=False):
        spec = PackageSpec(
            owner=dependency.get("owner"),
            name=dependency.get("name"),
            requirements=dependency.get("version"),
        )
        search_filters = {
            key: value
            for key, value in dependency.items()
            if key in ("authors", "platforms", "frameworks")
        }
        try:
            return self._install(
                spec, search_filters=search_filters or None, silent=silent
            )
        except UnknownPackageError:
            pass
        return None

    def uninstall_dependencies(self, pkg, silent=False):
        assert isinstance(pkg, PackageItem)
        manifest = self.load_manifest(pkg)
        if not manifest.get("dependencies"):
            return
        if not silent:
            self.print_message("Removing dependencies...", fg="yellow")
        for dependency in manifest.get("dependencies"):
            spec = PackageSpec(
                owner=dependency.get("owner"),
                name=dependency.get("name"),
                requirements=dependency.get("version"),
            )
            pkg = self.get_package(spec)
            if not pkg:
                continue
            self._uninstall(pkg, silent=silent)

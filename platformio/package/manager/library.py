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

from platformio.commands.lib.helpers import is_builtin_lib
from platformio.package.exception import MissingPackageManifestError
from platformio.package.manager.base import BasePackageManager
from platformio.package.meta import PackageSpec, PackageType
from platformio.project.config import ProjectConfig


class LibraryPackageManager(BasePackageManager):  # pylint: disable=too-many-ancestors
    def __init__(self, package_dir=None):
        super().__init__(
            PackageType.LIBRARY,
            package_dir
            or ProjectConfig.get_instance().get("platformio", "globallib_dir"),
        )

    @property
    def manifest_names(self):
        return PackageType.get_manifest_map()[PackageType.LIBRARY]

    def find_pkg_root(self, path, spec):
        try:
            return super().find_pkg_root(path, spec)
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
        root_dir_signs = set(["include", "Include", "inc", "Inc", "src", "Src"])
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

    def install_dependency(self, dependency):
        spec = self.dependency_to_spec(dependency)
        # skip built-in dependencies
        not_builtin_conds = [spec.external, spec.owner]
        if not any(not_builtin_conds):
            not_builtin_conds.append(not is_builtin_lib(spec.name))
        if any(not_builtin_conds):
            return super().install_dependency(dependency)
        return None

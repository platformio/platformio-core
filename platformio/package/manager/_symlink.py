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

from platformio import fs
from platformio.package.exception import PackageException
from platformio.package.meta import PackageItem, PackageSpec


class PackageManagerSymlinkMixin:
    @staticmethod
    def is_symlink(path):
        return path and path.endswith(".pio-link") and os.path.isfile(path)

    @classmethod
    def resolve_symlink(cls, path):
        assert cls.is_symlink(path)
        data = fs.load_json(path)
        spec = PackageSpec(**data["spec"])
        assert spec.symlink
        pkg_dir = spec.uri[10:]
        if not os.path.isabs(pkg_dir):
            pkg_dir = os.path.normpath(os.path.join(data["cwd"], pkg_dir))
        return (pkg_dir if os.path.isdir(pkg_dir) else None, spec)

    def get_symlinked_package(self, path):
        pkg_dir, spec = self.resolve_symlink(path)
        if not pkg_dir:
            return None
        pkg = PackageItem(os.path.realpath(pkg_dir))
        if not pkg.metadata:
            pkg.metadata = self.build_metadata(pkg.path, spec)
        return pkg

    def install_symlink(self, spec):
        assert spec.symlink
        pkg_dir = spec.uri[10:]
        if not os.path.isdir(pkg_dir):
            raise PackageException(
                f"Can not create a symbolic link for `{pkg_dir}`, not a directory"
            )
        link_path = os.path.join(
            self.package_dir,
            "%s.pio-link" % (spec.name or os.path.basename(os.path.abspath(pkg_dir))),
        )
        with open(link_path, mode="w", encoding="utf-8") as fp:
            json.dump(dict(cwd=os.getcwd(), spec=spec.as_dict()), fp)
        return self.get_symlinked_package(link_path)

    def uninstall_symlink(self, spec):
        assert spec.symlink
        for name in os.listdir(self.package_dir):
            path = os.path.join(self.package_dir, name)
            if not self.is_symlink(path):
                continue
            pkg = self.get_symlinked_package(path)
            if pkg.metadata.spec.uri == spec.uri:
                os.remove(path)

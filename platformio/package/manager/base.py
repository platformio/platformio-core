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
from datetime import datetime

import click
import semantic_version

from platformio import util
from platformio.commands import PlatformioCLI
from platformio.compat import ci_strings_are_equal
from platformio.package.exception import ManifestException, MissingPackageManifestError
from platformio.package.lockfile import LockFile
from platformio.package.manager._download import PackageManagerDownloadMixin
from platformio.package.manager._install import PackageManagerInstallMixin
from platformio.package.manager._legacy import PackageManagerLegacyMixin
from platformio.package.manager._registry import PackageManageRegistryMixin
from platformio.package.manager._uninstall import PackageManagerUninstallMixin
from platformio.package.manager._update import PackageManagerUpdateMixin
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.meta import (
    PackageItem,
    PackageMetaData,
    PackageSpec,
    PackageType,
)
from platformio.project.helpers import get_project_cache_dir


class BasePackageManager(  # pylint: disable=too-many-public-methods
    PackageManagerDownloadMixin,
    PackageManageRegistryMixin,
    PackageManagerInstallMixin,
    PackageManagerUninstallMixin,
    PackageManagerUpdateMixin,
    PackageManagerLegacyMixin,
):
    _MEMORY_CACHE = {}

    def __init__(self, pkg_type, package_dir):
        self.pkg_type = pkg_type
        self.package_dir = package_dir
        self._MEMORY_CACHE = {}

        self._lockfile = None
        self._download_dir = None
        self._tmp_dir = None
        self._registry_client = None

    def lock(self):
        if self._lockfile:
            return
        self.ensure_dir_exists(os.path.dirname(self.package_dir))
        self._lockfile = LockFile(self.package_dir)
        self.ensure_dir_exists(self.package_dir)
        self._lockfile.acquire()

    def unlock(self):
        if hasattr(self, "_lockfile") and self._lockfile:
            self._lockfile.release()
            self._lockfile = None

    def __del__(self):
        self.unlock()

    def memcache_get(self, key, default=None):
        return self._MEMORY_CACHE.get(key, default)

    def memcache_set(self, key, value):
        self._MEMORY_CACHE[key] = value

    def memcache_reset(self):
        self._MEMORY_CACHE.clear()

    @staticmethod
    def is_system_compatible(value):
        if not value or "*" in value:
            return True
        return util.items_in_list(value, util.get_systype())

    @staticmethod
    def ensure_dir_exists(path):
        if not os.path.isdir(path):
            os.makedirs(path)
        assert os.path.isdir(path)
        return path

    @staticmethod
    def ensure_spec(spec):
        return spec if isinstance(spec, PackageSpec) else PackageSpec(spec)

    @property
    def manifest_names(self):
        raise NotImplementedError

    def print_message(self, message, **kwargs):
        click.echo(
            "%s: " % str(self.__class__.__name__).replace("Package", " "), nl=False
        )
        click.secho(message, **kwargs)

    def get_download_dir(self):
        if not self._download_dir:
            self._download_dir = self.ensure_dir_exists(
                os.path.join(get_project_cache_dir(), "downloads")
            )
        return self._download_dir

    def get_tmp_dir(self):
        if not self._tmp_dir:
            self._tmp_dir = self.ensure_dir_exists(
                os.path.join(get_project_cache_dir(), "tmp")
            )
        return self._tmp_dir

    def find_pkg_root(self, path, spec):  # pylint: disable=unused-argument
        if self.manifest_exists(path):
            return path
        for root, _, _ in os.walk(path):
            if self.manifest_exists(root):
                return root
        raise MissingPackageManifestError(", ".join(self.manifest_names))

    def get_manifest_path(self, pkg_dir):
        if not os.path.isdir(pkg_dir):
            return None
        for name in self.manifest_names:
            manifest_path = os.path.join(pkg_dir, name)
            if os.path.isfile(manifest_path):
                return manifest_path
        return None

    def manifest_exists(self, pkg_dir):
        return self.get_manifest_path(pkg_dir)

    def load_manifest(self, src):
        path = src.path if isinstance(src, PackageItem) else src
        cache_key = "load_manifest-%s" % path
        result = self.memcache_get(cache_key)
        if result:
            return result
        candidates = (
            [os.path.join(path, name) for name in self.manifest_names]
            if os.path.isdir(path)
            else [path]
        )
        for item in candidates:
            if not os.path.isfile(item):
                continue
            try:
                result = ManifestParserFactory.new_from_file(item).as_dict()
                self.memcache_set(cache_key, result)
                return result
            except ManifestException as e:
                if not PlatformioCLI.in_silence():
                    self.print_message(str(e), fg="yellow")
        raise MissingPackageManifestError(", ".join(self.manifest_names))

    @staticmethod
    def generate_rand_version():
        return datetime.now().strftime("0.0.0+%Y%m%d%H%M%S")

    def build_metadata(self, pkg_dir, spec, vcs_revision=None):
        manifest = self.load_manifest(pkg_dir)
        metadata = PackageMetaData(
            type=self.pkg_type,
            name=manifest.get("name"),
            version=manifest.get("version"),
            spec=spec,
        )
        if not metadata.name or spec.has_custom_name():
            metadata.name = spec.name
        if vcs_revision:
            metadata.version = "%s+sha.%s" % (
                metadata.version if metadata.version else "0.0.0",
                vcs_revision,
            )
        if not metadata.version:
            metadata.version = self.generate_rand_version()
        return metadata

    def get_installed(self):
        if not os.path.isdir(self.package_dir):
            return []

        cache_key = "get_installed"
        if self.memcache_get(cache_key):
            return self.memcache_get(cache_key)

        result = []
        for name in sorted(os.listdir(self.package_dir)):
            if name.startswith("_tmp_installing"):  # legacy tmp folder
                continue
            pkg_dir = os.path.join(self.package_dir, name)
            if not os.path.isdir(pkg_dir):
                continue
            pkg = PackageItem(pkg_dir)
            if not pkg.metadata:
                try:
                    spec = self.build_legacy_spec(pkg_dir)
                    pkg.metadata = self.build_metadata(pkg_dir, spec)
                except MissingPackageManifestError:
                    pass
            if not pkg.metadata:
                continue
            if self.pkg_type == PackageType.TOOL:
                try:
                    if not self.is_system_compatible(
                        self.load_manifest(pkg).get("system")
                    ):
                        continue
                except MissingPackageManifestError:
                    pass
            result.append(pkg)

        self.memcache_set(cache_key, result)
        return result

    def get_package(self, spec):
        if isinstance(spec, PackageItem):
            return spec
        spec = self.ensure_spec(spec)
        best = None
        for pkg in self.get_installed():
            if not self.test_pkg_spec(pkg, spec):
                continue
            assert isinstance(pkg.metadata.version, semantic_version.Version)
            if spec.requirements and pkg.metadata.version not in spec.requirements:
                continue
            if not best or (pkg.metadata.version > best.metadata.version):
                best = pkg
        return best

    @staticmethod
    def test_pkg_spec(pkg, spec):
        # "id" mismatch
        if spec.id and spec.id != pkg.metadata.spec.id:
            return False

        # external "URL" mismatch
        if spec.external:
            # local folder mismatch
            if os.path.realpath(spec.url) == os.path.realpath(pkg.path) or (
                spec.url.startswith("file://")
                and os.path.realpath(pkg.path) == os.path.realpath(spec.url[7:])
            ):
                return True
            if spec.url != pkg.metadata.spec.url:
                return False

        # "owner" mismatch
        elif spec.owner and not ci_strings_are_equal(
            spec.owner, pkg.metadata.spec.owner
        ):
            return False

        # "name" mismatch
        elif not spec.id and not ci_strings_are_equal(spec.name, pkg.metadata.name):
            return False

        return True

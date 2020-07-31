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

from platformio import fs, util
from platformio.commands import PlatformioCLI
from platformio.package.exception import ManifestException, MissingPackageManifestError
from platformio.package.manager._download import PackageManagerDownloadMixin
from platformio.package.manager._install import PackageManagerInstallMixin
from platformio.package.manager._registry import PackageManageRegistryMixin
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.meta import (
    PackageMetaData,
    PackageSourceItem,
    PackageSpec,
    PackageType,
)
from platformio.project.helpers import get_project_cache_dir


class BasePackageManager(
    PackageManagerDownloadMixin, PackageManageRegistryMixin, PackageManagerInstallMixin
):
    MEMORY_CACHE = {}

    def __init__(self, pkg_type, package_dir):
        self.pkg_type = pkg_type
        self.package_dir = self.ensure_dir_exists(package_dir)
        self.MEMORY_CACHE = {}
        self._download_dir = None
        self._tmp_dir = None
        self._registry_client = None

    def memcache_get(self, key, default=None):
        return self.MEMORY_CACHE.get(key, default)

    def memcache_set(self, key, value):
        self.MEMORY_CACHE[key] = value

    def memcache_reset(self):
        self.MEMORY_CACHE.clear()

    @staticmethod
    def is_system_compatible(value):
        if not value or "*" in value:
            return True
        return util.items_in_list(value, util.get_systype())

    @staticmethod
    def generate_rand_version():
        return datetime.now().strftime("0.0.0+%Y%m%d%H%M%S")

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

    def print_message(self, message, nl=True):
        click.echo("%s: %s" % (self.__class__.__name__, message), nl=nl)

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
        path = src.path if isinstance(src, PackageSourceItem) else src
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
                    click.secho(str(e), fg="yellow")
        raise MissingPackageManifestError(", ".join(self.manifest_names))

    def build_legacy_spec(self, pkg_dir):
        # find src manifest
        src_manifest_name = ".piopkgmanager.json"
        src_manifest_path = None
        for name in os.listdir(pkg_dir):
            if not os.path.isfile(os.path.join(pkg_dir, name, src_manifest_name)):
                continue
            src_manifest_path = os.path.join(pkg_dir, name, src_manifest_name)
            break

        if src_manifest_path:
            src_manifest = fs.load_json(src_manifest_path)
            return PackageSpec(
                name=src_manifest.get("name"),
                url=src_manifest.get("url"),
                requirements=src_manifest.get("requirements"),
            )

        # fall back to a package manifest
        manifest = self.load_manifest(pkg_dir)
        return PackageSpec(name=manifest.get("name"))

    def build_metadata(self, pkg_dir, spec, vcs_revision=None):
        manifest = self.load_manifest(pkg_dir)
        metadata = PackageMetaData(
            type=self.pkg_type,
            name=manifest.get("name"),
            version=manifest.get("version"),
            spec=spec,
        )
        if not metadata.name or spec.is_custom_name():
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
        result = []
        for name in os.listdir(self.package_dir):
            pkg_dir = os.path.join(self.package_dir, name)
            if not os.path.isdir(pkg_dir):
                continue
            pkg = PackageSourceItem(pkg_dir)
            if not pkg.metadata:
                try:
                    spec = self.build_legacy_spec(pkg_dir)
                    pkg.metadata = self.build_metadata(pkg_dir, spec)
                except MissingPackageManifestError:
                    pass
            if pkg.metadata:
                result.append(pkg)
        return result

    def get_package(self, spec):
        def _ci_strings_are_equal(a, b):
            if a == b:
                return True
            if not a or not b:
                return False
            return a.strip().lower() == b.strip().lower()

        spec = self.ensure_spec(spec)
        best = None
        for pkg in self.get_installed():
            skip_conditions = [
                spec.owner
                and not _ci_strings_are_equal(spec.owner, pkg.metadata.spec.owner),
                spec.url and spec.url != pkg.metadata.spec.url,
                spec.id and spec.id != pkg.metadata.spec.id,
                not spec.id
                and not spec.url
                and not _ci_strings_are_equal(spec.name, pkg.metadata.name),
            ]
            if any(skip_conditions):
                continue
            if self.pkg_type == PackageType.TOOL:
                # TODO: check "system" for pkg
                pass

            assert isinstance(pkg.metadata.version, semantic_version.Version)
            if spec.requirements and pkg.metadata.version not in spec.requirements:
                continue
            if not best or (pkg.metadata.version > best.metadata.version):
                best = pkg
        return best

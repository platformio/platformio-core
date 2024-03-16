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

import logging
import os
import subprocess
from datetime import datetime

import click
import semantic_version

from platformio import fs, util
from platformio.cli import PlatformioCLI
from platformio.compat import ci_strings_are_equal
from platformio.package.exception import ManifestException, MissingPackageManifestError
from platformio.package.lockfile import LockFile
from platformio.package.manager._download import PackageManagerDownloadMixin
from platformio.package.manager._install import PackageManagerInstallMixin
from platformio.package.manager._legacy import PackageManagerLegacyMixin
from platformio.package.manager._registry import PackageManagerRegistryMixin
from platformio.package.manager._symlink import PackageManagerSymlinkMixin
from platformio.package.manager._uninstall import PackageManagerUninstallMixin
from platformio.package.manager._update import PackageManagerUpdateMixin
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.meta import (
    PackageItem,
    PackageMetadata,
    PackageSpec,
    PackageType,
)
from platformio.proc import get_pythonexe_path
from platformio.project.helpers import get_project_cache_dir


class ClickLoggingHandler(logging.Handler):
    def emit(self, record):
        click.echo(self.format(record))


class BasePackageManager(  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    PackageManagerDownloadMixin,
    PackageManagerRegistryMixin,
    PackageManagerSymlinkMixin,
    PackageManagerInstallMixin,
    PackageManagerUninstallMixin,
    PackageManagerUpdateMixin,
    PackageManagerLegacyMixin,
):
    _MEMORY_CACHE = {}

    def __init__(self, pkg_type, package_dir, compatibility=None):
        self.pkg_type = pkg_type
        self.package_dir = package_dir
        self.compatibility = compatibility
        self.log = self._setup_logger()

        self._MEMORY_CACHE = {}
        self._lockfile = None
        self._download_dir = None
        self._tmp_dir = None
        self._registry_client = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__} <type={self.pkg_type} "
            f"package_dir={self.package_dir}>"
        )

    def _setup_logger(self):
        logger = logging.getLogger(str(self.__class__.__name__).replace("Package", " "))
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(name)s: %(message)s")
        sh = ClickLoggingHandler()
        sh.setFormatter(formatter)
        logger.handlers.clear()
        logger.addHandler(sh)
        return logger

    def set_log_level(self, level):
        self.log.setLevel(level)

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
    def is_system_compatible(value, custom_system=None):
        if not value or "*" in value:
            return True
        return util.items_in_list(value, custom_system or util.get_systype())

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
            except ManifestException as exc:
                if not PlatformioCLI.in_silence():
                    self.log.warning(click.style(str(exc), fg="yellow"))
        raise MissingPackageManifestError(", ".join(self.manifest_names))

    @staticmethod
    def generate_rand_version():
        return datetime.now().strftime("0.0.0+%Y%m%d%H%M%S")

    def build_metadata(self, pkg_dir, spec, vcs_revision=None):
        manifest = self.load_manifest(pkg_dir)
        metadata = PackageMetadata(
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

    def get_installed(self):  # pylint: disable=too-many-branches
        if not os.path.isdir(self.package_dir):
            return []

        cache_key = "get_installed"
        if self.memcache_get(cache_key):
            return self.memcache_get(cache_key)

        result = []
        for name in sorted(os.listdir(self.package_dir)):
            if name.startswith("_tmp_installing"):  # legacy tmp folder
                continue
            pkg = None
            path = os.path.join(self.package_dir, name)
            if os.path.isdir(path):
                pkg = PackageItem(path)
            elif self.is_symlink(path):
                pkg = self.get_symlinked_package(path)
            if not pkg:
                continue
            if not pkg.metadata:
                try:
                    spec = self.build_legacy_spec(pkg.path)
                    pkg.metadata = self.build_metadata(pkg.path, spec)
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
            # local/symlinked folder mismatch
            check_conds = [
                os.path.abspath(spec.uri) == os.path.abspath(pkg.path),
                spec.uri.startswith("file://")
                and os.path.abspath(pkg.path) == os.path.abspath(spec.uri[7:]),
                spec.uri.startswith("symlink://")
                and os.path.abspath(pkg.path) == os.path.abspath(spec.uri[10:]),
            ]
            if any(check_conds):
                return True
            if spec.uri != pkg.metadata.spec.uri:
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

    def get_pkg_dependencies(self, pkg):
        return self.load_manifest(pkg).get("dependencies")

    @staticmethod
    def dependency_to_spec(dependency):
        return PackageSpec(
            owner=dependency.get("owner"),
            name=dependency.get("name"),
            requirements=dependency.get("version"),
        )

    def call_pkg_script(self, pkg, event):
        manifest = None
        try:
            manifest = self.load_manifest(pkg)
        except MissingPackageManifestError:
            pass
        scripts = (manifest or {}).get("scripts")
        if not scripts or not isinstance(scripts, dict):
            return
        cmd = scripts.get(event)
        if not cmd:
            return
        shell = False
        if not isinstance(cmd, list):
            shell = True
            cmd = [cmd]
        os.environ["PIO_PYTHON_EXE"] = get_pythonexe_path()
        with fs.cd(pkg.path):
            if os.path.isfile(cmd[0]) and cmd[0].endswith(".py"):
                cmd = [os.environ["PIO_PYTHON_EXE"]] + cmd
            subprocess.run(
                " ".join(cmd) if shell else cmd,
                cwd=pkg.path,
                shell=shell,
                env=os.environ,
                check=True,
            )

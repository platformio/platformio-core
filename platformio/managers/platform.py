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

# pylint: disable=too-many-public-methods, too-many-instance-attributes


from os.path import isdir, isfile, join

from platformio import app, exception, util
from platformio.managers.package import BasePkgManager, PackageManager
from platformio.platform.base import PlatformBase  # pylint: disable=unused-import
from platformio.platform.exception import UnknownBoard, UnknownPlatform
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig


class PlatformManager(BasePkgManager):
    def __init__(self, package_dir=None, repositories=None):
        if not repositories:
            repositories = [
                "https://dl.bintray.com/platformio/dl-platforms/manifest.json",
                "{0}://dl.platformio.org/platforms/manifest.json".format(
                    "https" if app.get_setting("strict_ssl") else "http"
                ),
            ]
        self.config = ProjectConfig.get_instance()
        BasePkgManager.__init__(
            self, package_dir or self.config.get_optional_dir("platforms"), repositories
        )

    @property
    def manifest_names(self):
        return ["platform.json"]

    def get_manifest_path(self, pkg_dir):
        if not isdir(pkg_dir):
            return None
        for name in self.manifest_names:
            manifest_path = join(pkg_dir, name)
            if isfile(manifest_path):
                return manifest_path
        return None

    def install(
        self,
        name,
        requirements=None,
        with_packages=None,
        without_packages=None,
        skip_default_package=False,
        with_all_packages=False,
        after_update=False,
        silent=False,
        force=False,
        **_
    ):  # pylint: disable=too-many-arguments, arguments-differ
        platform_dir = BasePkgManager.install(
            self, name, requirements, silent=silent, force=force
        )
        p = PlatformFactory.new(platform_dir)

        if with_all_packages:
            with_packages = list(p.packages.keys())

        # don't cleanup packages or install them after update
        # we check packages for updates in def update()
        if after_update:
            p.install_python_packages()
            p.on_installed()
            return True

        p.install_packages(
            with_packages,
            without_packages,
            skip_default_package,
            silent=silent,
            force=force,
        )
        p.install_python_packages()
        p.on_installed()
        return self.cleanup_packages(list(p.packages))

    def uninstall(self, package, requirements=None, after_update=False):
        if isdir(package):
            pkg_dir = package
        else:
            name, requirements, url = self.parse_pkg_uri(package, requirements)
            pkg_dir = self.get_package_dir(name, requirements, url)

        if not pkg_dir:
            raise UnknownPlatform(package)

        p = PlatformFactory.new(pkg_dir)
        BasePkgManager.uninstall(self, pkg_dir, requirements)
        p.uninstall_python_packages()
        p.on_uninstalled()

        # don't cleanup packages or install them after update
        # we check packages for updates in def update()
        if after_update:
            return True

        return self.cleanup_packages(list(p.packages))

    def update(  # pylint: disable=arguments-differ
        self, package, requirements=None, only_check=False, only_packages=False
    ):
        if isdir(package):
            pkg_dir = package
        else:
            name, requirements, url = self.parse_pkg_uri(package, requirements)
            pkg_dir = self.get_package_dir(name, requirements, url)

        if not pkg_dir:
            raise UnknownPlatform(package)

        p = PlatformFactory.new(pkg_dir)
        pkgs_before = list(p.get_installed_packages())

        missed_pkgs = set()
        if not only_packages:
            BasePkgManager.update(self, pkg_dir, requirements, only_check)
            p = PlatformFactory.new(pkg_dir)
            missed_pkgs = set(pkgs_before) & set(p.packages)
            missed_pkgs -= set(p.get_installed_packages())

        p.update_packages(only_check)
        self.cleanup_packages(list(p.packages))

        if missed_pkgs:
            p.install_packages(
                with_packages=list(missed_pkgs), skip_default_package=True
            )

        return True

    def cleanup_packages(self, names):
        self.cache_reset()
        deppkgs = {}
        for manifest in PlatformManager().get_installed():
            p = PlatformFactory.new(manifest["__pkg_dir"])
            for pkgname, pkgmanifest in p.get_installed_packages().items():
                if pkgname not in deppkgs:
                    deppkgs[pkgname] = set()
                deppkgs[pkgname].add(pkgmanifest["version"])

        pm = PackageManager(self.config.get_optional_dir("packages"))
        for manifest in pm.get_installed():
            if manifest["name"] not in names:
                continue
            if (
                manifest["name"] not in deppkgs
                or manifest["version"] not in deppkgs[manifest["name"]]
            ):
                try:
                    pm.uninstall(manifest["__pkg_dir"], after_update=True)
                except exception.UnknownPackage:
                    pass

        self.cache_reset()
        return True

    @util.memoized(expire="5s")
    def get_installed_boards(self):
        boards = []
        for manifest in self.get_installed():
            p = PlatformFactory.new(manifest["__pkg_dir"])
            for config in p.get_boards().values():
                board = config.get_brief_data()
                if board not in boards:
                    boards.append(board)
        return boards

    @staticmethod
    def get_registered_boards():
        return util.get_api_result("/boards", cache_valid="7d")

    def get_all_boards(self):
        boards = self.get_installed_boards()
        know_boards = ["%s:%s" % (b["platform"], b["id"]) for b in boards]
        try:
            for board in self.get_registered_boards():
                key = "%s:%s" % (board["platform"], board["id"])
                if key not in know_boards:
                    boards.append(board)
        except (exception.APIRequestError, exception.InternetIsOffline):
            pass
        return sorted(boards, key=lambda b: b["name"])

    def board_config(self, id_, platform=None):
        for manifest in self.get_installed_boards():
            if manifest["id"] == id_ and (
                not platform or manifest["platform"] == platform
            ):
                return manifest
        for manifest in self.get_registered_boards():
            if manifest["id"] == id_ and (
                not platform or manifest["platform"] == platform
            ):
                return manifest
        raise UnknownBoard(id_)

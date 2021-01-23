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

from platformio import util
from platformio.clients.http import HTTPClientError, InternetIsOffline
from platformio.package.exception import UnknownPackageError
from platformio.package.manager.base import BasePackageManager
from platformio.package.manager.core import get_installed_core_packages
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageType
from platformio.platform.exception import IncompatiblePlatform, UnknownBoard
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig


class PlatformPackageManager(BasePackageManager):  # pylint: disable=too-many-ancestors
    def __init__(self, package_dir=None):
        self.config = ProjectConfig.get_instance()
        super(PlatformPackageManager, self).__init__(
            PackageType.PLATFORM,
            package_dir or self.config.get_optional_dir("platforms"),
        )

    @property
    def manifest_names(self):
        return PackageType.get_manifest_map()[PackageType.PLATFORM]

    def install(  # pylint: disable=arguments-differ, too-many-arguments
        self,
        spec,
        with_packages=None,
        without_packages=None,
        skip_default_package=False,
        with_all_packages=False,
        silent=False,
        force=False,
    ):
        pkg = super(PlatformPackageManager, self).install(
            spec, silent=silent, force=force, skip_dependencies=True
        )
        try:
            p = PlatformFactory.new(pkg)
            p.ensure_engine_compatible()
        except IncompatiblePlatform as e:
            super(PlatformPackageManager, self).uninstall(
                pkg, silent=silent, skip_dependencies=True
            )
            raise e

        if with_all_packages:
            with_packages = list(p.packages)

        p.install_packages(
            with_packages,
            without_packages,
            skip_default_package,
            silent=silent,
            force=force,
        )
        p.install_python_packages()
        p.on_installed()
        return pkg

    def uninstall(self, spec, silent=False, skip_dependencies=False):
        pkg = self.get_package(spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(spec)
        p = PlatformFactory.new(pkg)
        assert super(PlatformPackageManager, self).uninstall(
            pkg, silent=silent, skip_dependencies=True
        )
        if not skip_dependencies:
            p.uninstall_python_packages()
            p.on_uninstalled()
        return pkg

    def update(  # pylint: disable=arguments-differ, too-many-arguments
        self,
        from_spec,
        to_spec=None,
        only_check=False,
        silent=False,
        show_incompatible=True,
        only_packages=False,
    ):
        pkg = self.get_package(from_spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(from_spec)
        p = PlatformFactory.new(pkg)
        pkgs_before = [item.metadata.name for item in p.get_installed_packages()]

        new_pkg = None
        missed_pkgs = set()
        if not only_packages:
            new_pkg = super(PlatformPackageManager, self).update(
                from_spec,
                to_spec,
                only_check=only_check,
                silent=silent,
                show_incompatible=show_incompatible,
            )
            p = PlatformFactory.new(new_pkg)
            missed_pkgs = set(pkgs_before) & set(p.packages)
            missed_pkgs -= set(
                item.metadata.name for item in p.get_installed_packages()
            )

        p.update_packages(only_check)

        if missed_pkgs:
            p.install_packages(
                with_packages=list(missed_pkgs), skip_default_package=True
            )

        return new_pkg or pkg

    @util.memoized(expire="5s")
    def get_installed_boards(self):
        boards = []
        for pkg in self.get_installed():
            p = PlatformFactory.new(pkg)
            for config in p.get_boards().values():
                board = config.get_brief_data()
                if board not in boards:
                    boards.append(board)
        return boards

    def get_registered_boards(self):
        return self.get_registry_client_instance().fetch_json_data(
            "get", "/v2/boards", cache_valid="1d"
        )

    def get_all_boards(self):
        boards = self.get_installed_boards()
        know_boards = ["%s:%s" % (b["platform"], b["id"]) for b in boards]
        try:
            for board in self.get_registered_boards():
                key = "%s:%s" % (board["platform"], board["id"])
                if key not in know_boards:
                    boards.append(board)
        except (HTTPClientError, InternetIsOffline):
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


#
# Helpers
#


def remove_unnecessary_platform_packages(dry_run=False):
    candidates = []
    required = set()
    core_packages = get_installed_core_packages()
    for platform in PlatformPackageManager().get_installed():
        p = PlatformFactory.new(platform)
        for pkg in p.get_installed_packages(with_optional=True):
            required.add(pkg)

    pm = ToolPackageManager()
    for pkg in pm.get_installed():
        skip_conds = [
            pkg.metadata.spec.url,
            os.path.isfile(os.path.join(pkg.path, ".piokeep")),
            pkg in required,
            pkg in core_packages,
        ]
        if not any(skip_conds):
            candidates.append(pkg)

    if dry_run:
        return candidates

    for pkg in candidates:
        pm.uninstall(pkg)

    return candidates

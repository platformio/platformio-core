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
from platformio.http import HTTPClientError, InternetIsOffline
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
        super().__init__(
            PackageType.PLATFORM,
            package_dir or self.config.get("platformio", "platforms_dir"),
        )

    @property
    def manifest_names(self):
        return PackageType.get_manifest_map()[PackageType.PLATFORM]

    def install(  # pylint: disable=arguments-differ,too-many-arguments
        self,
        spec,
        skip_dependencies=False,
        force=False,
        project_env=None,
        project_targets=None,
    ):
        already_installed = self.get_package(spec)
        pkg = super().install(spec, force=force, skip_dependencies=True)
        try:
            p = PlatformFactory.new(pkg)
            # set logging level for underlying tool manager
            p.pm.set_log_level(self.log.getEffectiveLevel())
            p.ensure_engine_compatible()
        except IncompatiblePlatform as exc:
            super().uninstall(pkg, skip_dependencies=True)
            raise exc
        if project_env:
            p.configure_project_packages(project_env, project_targets)
        if not skip_dependencies:
            p.install_required_packages(force=force)
        if not already_installed:
            p.on_installed()
        return pkg

    def uninstall(  # pylint: disable=arguments-differ
        self, spec, skip_dependencies=False, project_env=None
    ):
        pkg = self.get_package(spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(spec)
        p = PlatformFactory.new(pkg)
        # set logging level for underlying tool manager
        p.pm.set_log_level(self.log.getEffectiveLevel())
        if project_env:
            p.configure_project_packages(project_env)
        if not skip_dependencies:
            p.uninstall_packages()
        assert super().uninstall(pkg, skip_dependencies=True)
        p.on_uninstalled()
        return pkg

    def update(  # pylint: disable=arguments-differ
        self,
        from_spec,
        to_spec=None,
        skip_dependencies=False,
        project_env=None,
    ):
        pkg = self.get_package(from_spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(from_spec)
        pkg = super().update(
            from_spec,
            to_spec,
        )
        p = PlatformFactory.new(pkg)
        # set logging level for underlying tool manager
        p.pm.set_log_level(self.log.getEffectiveLevel())
        if project_env:
            p.configure_project_packages(project_env)
        if not skip_dependencies:
            p.update_packages()
        return pkg

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
            "get", "/v2/boards", x_cache_valid="1d"
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
        for pkg in p.get_installed_packages(with_optional_versions=True):
            required.add(pkg)

    pm = ToolPackageManager()
    for pkg in pm.get_installed():
        skip_conds = [
            pkg.metadata.spec.uri,
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

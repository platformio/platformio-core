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

import click

from platformio.package.exception import UnknownPackageError
from platformio.package.meta import PackageItem, PackageOutdatedResult, PackageSpec
from platformio.package.vcsclient import VCSBaseException, VCSClientFactory


class PackageManagerUpdateMixin:
    def outdated(self, pkg, spec=None):
        assert isinstance(pkg, PackageItem)
        assert pkg.metadata

        if spec and not isinstance(spec, PackageSpec):
            spec = PackageSpec(spec)

        if not os.path.isdir(pkg.path):
            return PackageOutdatedResult(current=pkg.metadata.version)

        # skip detached package to a specific version
        detached_conditions = [
            "@" in pkg.path,
            pkg.metadata.spec and not pkg.metadata.spec.external,
            not spec,
        ]
        if all(detached_conditions):
            return PackageOutdatedResult(current=pkg.metadata.version, detached=True)

        latest = None
        wanted = None
        if pkg.metadata.spec.external:
            latest = self._fetch_vcs_latest_version(pkg)
        else:
            try:
                reg_pkg = self.fetch_registry_package(pkg.metadata.spec)
                latest = (
                    self.pick_best_registry_version(reg_pkg["versions"]) or {}
                ).get("name")
                if spec:
                    wanted = (
                        self.pick_best_registry_version(reg_pkg["versions"], spec) or {}
                    ).get("name")
                    if not wanted:  # wrong library
                        latest = None
            except UnknownPackageError:
                pass

        return PackageOutdatedResult(
            current=pkg.metadata.version, latest=latest, wanted=wanted
        )

    def _fetch_vcs_latest_version(self, pkg):
        vcs = None
        try:
            vcs = VCSClientFactory.new(pkg.path, pkg.metadata.spec.uri, silent=True)
        except VCSBaseException:
            return None
        if not vcs.can_be_updated:
            return None

        vcs_revision = vcs.get_latest_revision()
        if not vcs_revision:
            return None

        return str(
            self.build_metadata(
                pkg.path, pkg.metadata.spec, vcs_revision=vcs_revision
            ).version
        )

    def update(
        self,
        from_spec,
        to_spec=None,
        skip_dependencies=False,
    ):
        pkg = self.get_package(from_spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(from_spec)

        outdated = self.outdated(pkg, to_spec)
        if not outdated.is_outdated(allow_incompatible=False):
            self.log.debug(
                click.style(
                    "{name}@{version} is already up-to-date".format(
                        **pkg.metadata.as_dict()
                    ),
                    fg="yellow",
                )
            )
            return pkg

        self.log.info(
            "Updating %s @ %s"
            % (click.style(pkg.metadata.name, fg="cyan"), pkg.metadata.version)
        )
        try:
            self.lock()
            return self._update(pkg, outdated, skip_dependencies)
        finally:
            self.unlock()

    def _update(self, pkg, outdated, skip_dependencies=False):
        if pkg.metadata.spec.external:
            vcs = VCSClientFactory.new(pkg.path, pkg.metadata.spec.uri)
            assert vcs.update()
            pkg.metadata.version = self._fetch_vcs_latest_version(pkg)
            pkg.dump_meta()
            return pkg

        # uninstall existing version
        self.uninstall(pkg, skip_dependencies=True)

        return self.install(
            PackageSpec(
                id=pkg.metadata.spec.id,
                owner=pkg.metadata.spec.owner,
                name=pkg.metadata.spec.name,
                requirements=outdated.wanted or outdated.latest,
            ),
            skip_dependencies=skip_dependencies,
        )

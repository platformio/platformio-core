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

from platformio.clients.http import ensure_internet_on
from platformio.package.exception import UnknownPackageError
from platformio.package.meta import PackageItem, PackageOutdatedResult, PackageSpec
from platformio.package.vcsclient import VCSBaseException, VCSClientFactory


class PackageManagerUpdateMixin(object):
    def outdated(self, pkg, spec=None):
        assert isinstance(pkg, PackageItem)
        assert not spec or isinstance(spec, PackageSpec)
        assert pkg.metadata

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
            vcs = VCSClientFactory.new(pkg.path, pkg.metadata.spec.url, silent=True)
        except VCSBaseException:
            return None
        if not vcs.can_be_updated:
            return None
        return str(
            self.build_metadata(
                pkg.path, pkg.metadata.spec, vcs_revision=vcs.get_latest_revision()
            ).version
        )

    def update(  # pylint: disable=too-many-arguments
        self,
        from_spec,
        to_spec=None,
        only_check=False,
        silent=False,
        show_incompatible=True,
    ):
        pkg = self.get_package(from_spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(from_spec)

        if not silent:
            click.echo(
                "{} {:<45} {:<35}".format(
                    "Checking" if only_check else "Updating",
                    click.style(pkg.metadata.spec.humanize(), fg="cyan"),
                    "%s @ %s" % (pkg.metadata.version, to_spec.requirements)
                    if to_spec and to_spec.requirements
                    else str(pkg.metadata.version),
                ),
                nl=False,
            )
        if not ensure_internet_on():
            if not silent:
                click.echo("[%s]" % (click.style("Off-line", fg="yellow")))
            return pkg

        outdated = self.outdated(pkg, to_spec)
        if not silent:
            self.print_outdated_state(outdated, only_check, show_incompatible)

        if only_check or not outdated.is_outdated(allow_incompatible=False):
            return pkg

        try:
            self.lock()
            return self._update(pkg, outdated, silent=silent)
        finally:
            self.unlock()

    @staticmethod
    def print_outdated_state(outdated, only_check, show_incompatible):
        if outdated.detached:
            return click.echo("[%s]" % (click.style("Detached", fg="yellow")))

        if (
            not outdated.latest
            or outdated.current == outdated.latest
            or (not show_incompatible and outdated.current == outdated.wanted)
        ):
            return click.echo("[%s]" % (click.style("Up-to-date", fg="green")))

        if outdated.wanted and outdated.current == outdated.wanted:
            return click.echo(
                "[%s]" % (click.style("Incompatible %s" % outdated.latest, fg="yellow"))
            )

        if only_check:
            return click.echo(
                "[%s]"
                % (
                    click.style(
                        "Outdated %s" % str(outdated.wanted or outdated.latest),
                        fg="red",
                    )
                )
            )

        return click.echo(
            "[%s]"
            % (
                click.style(
                    "Updating to %s" % str(outdated.wanted or outdated.latest),
                    fg="green",
                )
            )
        )

    def _update(self, pkg, outdated, silent=False):
        if pkg.metadata.spec.external:
            vcs = VCSClientFactory.new(pkg.path, pkg.metadata.spec.url)
            assert vcs.update()
            pkg.metadata.version = self._fetch_vcs_latest_version(pkg)
            pkg.dump_meta()
            return pkg

        new_pkg = self.install(
            PackageSpec(
                id=pkg.metadata.spec.id,
                owner=pkg.metadata.spec.owner,
                name=pkg.metadata.spec.name,
                requirements=outdated.wanted or outdated.latest,
            ),
            silent=silent,
        )
        if new_pkg:
            old_pkg = self.get_package(
                PackageSpec(
                    id=pkg.metadata.spec.id,
                    owner=pkg.metadata.spec.owner,
                    name=pkg.metadata.name,
                    requirements=pkg.metadata.version,
                )
            )
            if old_pkg:
                self.uninstall(old_pkg, silent=silent, skip_dependencies=True)
        return new_pkg

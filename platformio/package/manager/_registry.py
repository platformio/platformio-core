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

import time
from typing import Optional

import click

from platformio import util
from platformio.package.download import ArtifactVerificationError
from platformio.package.exception import IncompatiblePackageError, UnknownPackageError
from platformio.package.manager._download import TrustedArtifact
from platformio.package.meta import PackageItem, PackageSpec, PackageType
from platformio.package.version import cast_version_to_semver
from platformio.registry.client import RegistryClient
from platformio.registry.mirror import RegistryFileMirrorIterator


class PackageManagerRegistryMixin:
    def install_from_registry(self, spec, search_qualifiers=None):
        package = version = None
        if spec.owner and spec.name and not search_qualifiers:
            package = self.fetch_registry_package(spec)
            if not package:
                raise UnknownPackageError(spec.humanize())
            version = self.pick_best_registry_version(package["versions"], spec)
        elif spec.id or spec.name:
            packages = self.search_registry_packages(spec, search_qualifiers)
            if not packages:
                raise UnknownPackageError(spec.humanize())
            if len(packages) > 1:
                self.print_multi_package_issue(self.log.warning, packages, spec)
            package, version = self.find_best_registry_version(packages, spec)

        if not package or not version:
            raise UnknownPackageError(spec.humanize())

        pkgfile = self.pick_compatible_pkg_file(version["files"]) if version else None
        if not pkgfile:
            if self.pkg_type == PackageType.TOOL:
                raise IncompatiblePackageError(spec.humanize(), util.get_systype())
            raise UnknownPackageError(spec.humanize())

        # the registry API's SHA256 is the canonical artifact identity
        try:
            artifact = TrustedArtifact(
                pkgfile["checksum"]["sha256"], pkgfile.get("size")
            )
        except (KeyError, TypeError, ValueError) as exc:
            self.log.warning(
                click.style(
                    "Warning! Invalid registry checksum metadata: %s" % exc,
                    fg="yellow",
                )
            )
            return None
        pkg_spec = PackageSpec(
            owner=package["owner"]["username"], id=package["id"], name=package["name"]
        )
        pkg, resumed_failures = self._install_from_mirrors(pkgfile, pkg_spec, artifact)
        if pkg is not None:
            return pkg
        # a mirror that failed verification on resumed partial data never had a
        # clean attempt; give each such mirror exactly one. Interrupted mirrors
        # are not retried: the partial is kept for the next install.
        for url in resumed_failures:
            self.log.warning(
                click.style("Retrying %s without partial data..." % url, fg="yellow")
            )
            try:
                return self.install_from_uri(
                    url, pkg_spec, artifact, resume_partial=False
                )
            except Exception as exc:  # pylint: disable=broad-except
                self._log_mirror_failure(exc)
        return None

    def _install_from_mirrors(
        self, pkgfile: dict, spec: PackageSpec, artifact: TrustedArtifact
    ) -> tuple[Optional[PackageItem], list[str]]:
        """A single pass over the approved mirrors.

        Return the installed package (or None) and the URLs of mirrors that
        failed verification on resumed partial data.
        """
        resumed_failures: list[str] = []
        for url, checksum in RegistryFileMirrorIterator(pkgfile["download_url"]):
            if checksum and checksum.lower() != artifact.sha256:
                self.log.warning(
                    click.style(
                        "Warning! Package Mirror: skipping %s, its SHA256 "
                        "does not match the registry" % url,
                        fg="yellow",
                    )
                )
                continue
            try:
                return self.install_from_uri(url, spec, artifact), resumed_failures
            except ArtifactVerificationError as exc:
                if exc.resumed:
                    resumed_failures.append(url)
                self._log_mirror_failure(exc)
            except Exception as exc:  # pylint: disable=broad-except
                self._log_mirror_failure(exc)
        return None, resumed_failures

    def _log_mirror_failure(self, exc: Exception) -> None:
        self.log.warning(click.style("Warning! Package Mirror: %s" % exc, fg="yellow"))
        self.log.warning(click.style("Looking for another mirror...", fg="yellow"))

    def get_registry_client_instance(self):
        if not self._registry_client:
            self._registry_client = RegistryClient()
        return self._registry_client

    def search_registry_packages(self, spec, qualifiers=None):
        assert isinstance(spec, PackageSpec)
        qualifiers = qualifiers or {}
        if spec.id:
            qualifiers["ids"] = str(spec.id)
        else:
            qualifiers["types"] = self.pkg_type
            qualifiers["names"] = spec.name.lower()
            if spec.owner:
                qualifiers["owners"] = spec.owner.lower()
        return self.get_registry_client_instance().list_packages(qualifiers=qualifiers)[
            "items"
        ]

    def fetch_registry_package(self, spec):
        assert isinstance(spec, PackageSpec)
        result = None
        regclient = self.get_registry_client_instance()
        if spec.owner and spec.name:
            result = regclient.get_package(self.pkg_type, spec.owner, spec.name)
        if not result and (spec.id or (spec.name and not spec.owner)):
            packages = self.search_registry_packages(spec)
            if packages:
                result = regclient.get_package(
                    self.pkg_type, packages[0]["owner"]["username"], packages[0]["name"]
                )
        if not result:
            raise UnknownPackageError(spec.humanize())
        return result

    def reveal_registry_package_id(self, spec):
        spec = self.ensure_spec(spec)
        if spec.id:
            return spec.id
        packages = self.search_registry_packages(spec)
        if not packages:
            raise UnknownPackageError(spec.humanize())
        if len(packages) > 1:
            self.print_multi_package_issue(self.log.warning, packages, spec)
            self.log.info("")
        return packages[0]["id"]

    @staticmethod
    def print_multi_package_issue(print_func, packages, spec):
        print_func(
            click.style(
                "Warning! More than one package has been found by ", fg="yellow"
            )
            + click.style(spec.humanize(), fg="cyan")
            + click.style(" requirements:", fg="yellow")
        )

        for item in packages:
            print_func(
                " - {owner}/{name}@{version}".format(
                    owner=click.style(item["owner"]["username"], fg="cyan"),
                    name=item["name"],
                    version=item["version"]["name"],
                )
            )
        print_func(
            click.style(
                "Please specify detailed REQUIREMENTS using package owner and version "
                "(shown above) to avoid name conflicts",
                fg="yellow",
            )
        )

    def find_best_registry_version(self, packages, spec):
        for package in packages:
            # find compatible version within the latest package versions
            version = self.pick_best_registry_version([package["version"]], spec)
            if version:
                return (package, version)

            # if the custom version requirements, check ALL package versions
            version = self.pick_best_registry_version(
                self.fetch_registry_package(
                    PackageSpec(
                        id=package["id"],
                        owner=package["owner"]["username"],
                        name=package["name"],
                    )
                ).get("versions"),
                spec,
            )
            if version:
                return (package, version)
            time.sleep(1)
        return (None, None)

    def get_compatible_registry_versions(self, versions, spec=None, custom_system=None):
        assert not spec or isinstance(spec, PackageSpec)
        result = []
        for version in versions:
            semver = cast_version_to_semver(version["name"])
            if spec and spec.requirements and semver not in spec.requirements:
                continue
            if not any(
                self.is_system_compatible(f.get("system"), custom_system=custom_system)
                for f in version["files"]
            ):
                continue
            result.append(version)
        return result

    def pick_best_registry_version(self, versions, spec=None, custom_system=None):
        best = None
        for version in self.get_compatible_registry_versions(
            versions, spec, custom_system
        ):
            semver = cast_version_to_semver(version["name"])
            if not best or (semver > cast_version_to_semver(best["name"])):
                best = version
        return best

    def pick_compatible_pkg_file(self, version_files, custom_system=None):
        for item in version_files:
            if self.is_system_compatible(
                item.get("system"), custom_system=custom_system
            ):
                return item
        return None

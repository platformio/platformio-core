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

import click

from platformio.clients.http import HTTPClient
from platformio.clients.registry import RegistryClient
from platformio.package.exception import UnknownPackageError
from platformio.package.meta import PackageSpec
from platformio.package.version import cast_version_to_semver

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class RegistryFileMirrorIterator(object):

    HTTP_CLIENT_INSTANCES = {}

    def __init__(self, download_url):
        self.download_url = download_url
        self._url_parts = urlparse(download_url)
        self._mirror = "%s://%s" % (self._url_parts.scheme, self._url_parts.netloc)
        self._visited_mirrors = []

    def __iter__(self):  # pylint: disable=non-iterator-returned
        return self

    def next(self):
        """For Python 2 compatibility"""
        return self.__next__()

    def __next__(self):
        http = self.get_http_client()
        response = http.send_request(
            "head",
            self._url_parts.path,
            allow_redirects=False,
            params=dict(bypass=",".join(self._visited_mirrors))
            if self._visited_mirrors
            else None,
        )
        stop_conditions = [
            response.status_code not in (302, 307),
            not response.headers.get("Location"),
            not response.headers.get("X-PIO-Mirror"),
            response.headers.get("X-PIO-Mirror") in self._visited_mirrors,
        ]
        if any(stop_conditions):
            raise StopIteration
        self._visited_mirrors.append(response.headers.get("X-PIO-Mirror"))
        return (
            response.headers.get("Location"),
            response.headers.get("X-PIO-Content-SHA256"),
        )

    def get_http_client(self):
        if self._mirror not in RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES:
            RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES[self._mirror] = HTTPClient(
                self._mirror
            )
        return RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES[self._mirror]


class PackageManageRegistryMixin(object):
    def install_from_registry(self, spec, search_filters=None, silent=False):
        if spec.owner and spec.name and not search_filters:
            package = self.fetch_registry_package(spec)
            if not package:
                raise UnknownPackageError(spec.humanize())
            version = self.pick_best_registry_version(package["versions"], spec)
        else:
            packages = self.search_registry_packages(spec, search_filters)
            if not packages:
                raise UnknownPackageError(spec.humanize())
            if len(packages) > 1 and not silent:
                self.print_multi_package_issue(packages, spec)
            package, version = self.find_best_registry_version(packages, spec)

        if not package or not version:
            raise UnknownPackageError(spec.humanize())

        pkgfile = self._pick_compatible_pkg_file(version["files"]) if version else None
        if not pkgfile:
            raise UnknownPackageError(spec.humanize())

        for url, checksum in RegistryFileMirrorIterator(pkgfile["download_url"]):
            try:
                return self.install_from_url(
                    url,
                    PackageSpec(
                        owner=package["owner"]["username"],
                        id=package["id"],
                        name=package["name"],
                    ),
                    checksum or pkgfile["checksum"]["sha256"],
                    silent=silent,
                )
            except Exception as e:  # pylint: disable=broad-except
                self.print_message("Warning! Package Mirror: %s" % e, fg="yellow")
                self.print_message("Looking for another mirror...", fg="yellow")

        return None

    def get_registry_client_instance(self):
        if not self._registry_client:
            self._registry_client = RegistryClient()
        return self._registry_client

    def search_registry_packages(self, spec, filters=None):
        assert isinstance(spec, PackageSpec)
        filters = filters or {}
        if spec.id:
            filters["ids"] = str(spec.id)
        else:
            filters["types"] = self.pkg_type
            filters["names"] = spec.name.lower()
            if spec.owner:
                filters["owners"] = spec.owner.lower()
        return self.get_registry_client_instance().list_packages(filters=filters)[
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

    def reveal_registry_package_id(self, spec, silent=False):
        spec = self.ensure_spec(spec)
        if spec.id:
            return spec.id
        packages = self.search_registry_packages(spec)
        if not packages:
            raise UnknownPackageError(spec.humanize())
        if len(packages) > 1 and not silent:
            self.print_multi_package_issue(packages, spec)
            click.echo("")
        return packages[0]["id"]

    def print_multi_package_issue(self, packages, spec):
        self.print_message(
            "Warning! More than one package has been found by ", fg="yellow", nl=False
        )
        click.secho(spec.humanize(), fg="cyan", nl=False)
        click.secho(" requirements:", fg="yellow")
        for item in packages:
            click.echo(
                " - {owner}/{name} @ {version}".format(
                    owner=click.style(item["owner"]["username"], fg="cyan"),
                    name=item["name"],
                    version=item["version"]["name"],
                )
            )
        self.print_message(
            "Please specify detailed REQUIREMENTS using package owner and version "
            "(showed above) to avoid name conflicts",
            fg="yellow",
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

    def filter_incompatible_registry_versions(self, versions, spec=None):
        assert not spec or isinstance(spec, PackageSpec)
        result = []
        for version in versions:
            semver = cast_version_to_semver(version["name"])
            if spec and spec.requirements and semver not in spec.requirements:
                continue
            if not any(
                self.is_system_compatible(f.get("system")) for f in version["files"]
            ):
                continue
            result.append(version)
        return result

    def pick_best_registry_version(self, versions, spec=None):
        best = None
        for version in self.filter_incompatible_registry_versions(versions, spec):
            semver = cast_version_to_semver(version["name"])
            if not best or (semver > cast_version_to_semver(best["name"])):
                best = version
        return best

    def _pick_compatible_pkg_file(self, version_files):
        for item in version_files:
            if self.is_system_compatible(item.get("system")):
                return item
        return None

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
from platformio.package.meta import PackageMetaData, PackageSpec

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class RegistryFileMirrorsIterator(object):

    HTTP_CLIENT_INSTANCES = {}

    def __init__(self, download_url):
        self.download_url = download_url
        self._url_parts = urlparse(download_url)
        self._base_url = "%s://%s" % (self._url_parts.scheme, self._url_parts.netloc)
        self._visited_mirrors = []

    def __iter__(self):  # pylint: disable=non-iterator-returned
        return self

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
        if self._base_url not in RegistryFileMirrorsIterator.HTTP_CLIENT_INSTANCES:
            RegistryFileMirrorsIterator.HTTP_CLIENT_INSTANCES[
                self._base_url
            ] = HTTPClient(self._base_url)
        return RegistryFileMirrorsIterator.HTTP_CLIENT_INSTANCES[self._base_url]


class PackageManageRegistryMixin(object):
    def install_from_registry(self, spec, search_filters=None, silent=False):
        packages = self.search_registry_packages(spec, search_filters)
        if not packages:
            raise UnknownPackageError(spec.humanize())
        if len(packages) > 1 and not silent:
            self.print_multi_package_issue(packages, spec)
        package, version = self.find_best_registry_version(packages, spec)
        pkgfile = self._pick_compatible_pkg_file(version["files"]) if version else None
        if not pkgfile:
            raise UnknownPackageError(spec.humanize())

        for url, checksum in RegistryFileMirrorsIterator(pkgfile["download_url"]):
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
                click.secho("Warning! Package Mirror: %s" % e, fg="yellow")
                click.secho("Looking for another mirror...", fg="yellow")

        return None

    def get_registry_client_instance(self):
        if not self._registry_client:
            self._registry_client = RegistryClient()
        return self._registry_client

    def search_registry_packages(self, spec, filters=None):
        filters = filters or {}
        if spec.id:
            filters["ids"] = str(spec.id)
        else:
            filters["types"] = self.pkg_type
            filters["names"] = '"%s"' % spec.name.lower()
            if spec.owner:
                filters["owners"] = spec.owner.lower()
        return self.get_registry_client_instance().list_packages(filters=filters)[
            "items"
        ]

    def fetch_registry_package_versions(self, owner, name):
        return self.get_registry_client_instance().get_package(
            self.pkg_type, owner, name
        )["versions"]

    @staticmethod
    def print_multi_package_issue(packages, spec):
        click.secho(
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
        click.secho(
            "Please specify detailed REQUIREMENTS using package owner and version "
            "(showed above) to avoid project compatibility issues.",
            fg="yellow",
        )

    def find_best_registry_version(self, packages, spec):
        # find compatible version within the latest package versions
        for package in packages:
            version = self._pick_best_pkg_version([package["version"]], spec)
            if version:
                return (package, version)

        if not spec.requirements:
            return None

        # if the custom version requirements, check ALL package versions
        for package in packages:
            version = self._pick_best_pkg_version(
                self.fetch_registry_package_versions(
                    package["owner"]["username"], package["name"]
                ),
                spec,
            )
            if version:
                return (package, version)
            time.sleep(1)
        return None

    def _pick_best_pkg_version(self, versions, spec):
        best = None
        for version in versions:
            semver = PackageMetaData.to_semver(version["name"])
            if spec.requirements and semver not in spec.requirements:
                continue
            if not any(
                self.is_system_compatible(f.get("system")) for f in version["files"]
            ):
                continue
            if not best or (semver > PackageMetaData.to_semver(best["name"])):
                best = version
        return best

    def _pick_compatible_pkg_file(self, version_files):
        for item in version_files:
            if self.is_system_compatible(item.get("system")):
                return item
        return None

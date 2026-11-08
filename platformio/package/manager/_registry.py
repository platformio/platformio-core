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

import itertools
import time
from typing import Iterator, Optional

import click

from platformio import proc, telemetry, util
from platformio.compat import is_proxy_set
from platformio.package.download import (
    ArtifactVerificationError,
    ResponseValidationError,
    TransferInterruptedError,
)
from platformio.package.exception import IncompatiblePackageError, UnknownPackageError
from platformio.package.manager._download import DownloadAttempt, TrustedArtifact
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
        attempts = itertools.count(1)
        pkg, resumed_failures = self._install_from_mirrors(
            pkgfile, pkg_spec, artifact, attempts
        )
        if pkg is not None:
            return pkg
        # a mirror that failed verification on resumed partial data never had a
        # clean attempt; give each such mirror exactly one. Interrupted mirrors
        # are not retried: the partial is kept for the next install.
        for url, mirror in resumed_failures:
            self.log.warning(
                click.style("Retrying %s without partial data..." % url, fg="yellow")
            )
            try:
                return self._install_from_mirror(
                    url,
                    pkg_spec,
                    artifact,
                    {"mirror": mirror, "pass": "clean", "attempt": next(attempts)},
                    resume_partial=False,
                )
            except Exception as exc:  # pylint: disable=broad-except
                self._log_mirror_failure(exc)
        return None

    def _install_from_mirrors(
        self,
        pkgfile: dict,
        spec: PackageSpec,
        artifact: TrustedArtifact,
        attempts: Iterator[int],
    ) -> tuple[Optional[PackageItem], list[tuple[str, str]]]:
        """A single pass over the approved mirrors.

        Return the installed package (or None) and the (URL, mirror id) of
        mirrors that failed verification on resumed partial data.
        """
        resumed_failures: list[tuple[str, str]] = []
        mirrors = RegistryFileMirrorIterator(
            pkgfile["download_url"],
            get_resume_offset=lambda: self.get_resume_offset(artifact),
        )
        for url, checksum in mirrors:
            context = {
                "mirror": mirrors.mirror or "",
                "pass": "main",
                "attempt": next(attempts),
            }
            if checksum and checksum.lower() != artifact.sha256:
                self.log.warning(
                    click.style(
                        "Warning! Package Mirror: skipping %s, its SHA256 "
                        "does not match the registry" % url,
                        fg="yellow",
                    )
                )
                self._log_download_event(
                    "skipped", artifact, DownloadAttempt(), context
                )
                continue
            try:
                return (
                    self._install_from_mirror(url, spec, artifact, context),
                    resumed_failures,
                )
            except ArtifactVerificationError as exc:
                if exc.resumed:
                    resumed_failures.append((url, context["mirror"]))
                self._log_mirror_failure(exc)
            except Exception as exc:  # pylint: disable=broad-except
                self._log_mirror_failure(exc)
        return None, resumed_failures

    def _install_from_mirror(  # pylint: disable=too-many-arguments
        self,
        url: str,
        spec: PackageSpec,
        artifact: TrustedArtifact,
        context: dict,
        resume_partial: bool = True,
    ) -> Optional[PackageItem]:
        """One mirror attempt, reported as a ``pkg_download`` event."""
        attempt = DownloadAttempt()
        try:
            pkg = self.install_from_uri(
                url, spec, artifact, resume_partial=resume_partial, attempt=attempt
            )
        except BaseException as exc:
            if attempt.transferred:  # nothing to report for a cache hit
                self._log_download_event(
                    _download_outcome(attempt, exc), artifact, attempt, context, exc
                )
            raise
        if attempt.transferred:
            self._log_download_event("completed", artifact, attempt, context)
        return pkg

    def _log_download_event(  # pylint: disable=too-many-arguments
        self,
        outcome: str,
        artifact: TrustedArtifact,
        attempt: DownloadAttempt,
        context: dict,
        exc: Optional[BaseException] = None,
    ) -> None:
        if outcome == "completed":
            exc = None  # e.g. unpacking failed after the download completed
        cause = exc.__cause__ if exc is not None else None
        params = {
            "outcome": outcome,
            "sha256": artifact.sha256,
            "total": artifact.size or 0,
            "mirror": context["mirror"],
            "host": attempt.host,
            "pass": context["pass"],
            "attempt": context["attempt"],
            "range_sent": attempt.range_sent,
            "status": attempt.status,
            "offset": attempt.offset,
            "received": attempt.received,
            "ttfb": round(attempt.ttfb, 2),
            "transfer_time": round(attempt.transfer_time, 2),
            "speed": (
                int(attempt.received / attempt.transfer_time)
                if attempt.transfer_time > 0
                else 0
            ),
            "duration": round(attempt.duration, 2),
            "error": type(exc).__name__ if exc is not None else "",
            "error_cause": type(cause).__name__ if cause is not None else "",
            "proxy": is_proxy_set(),
            "ci": proc.is_ci(),
        }
        try:
            telemetry.log_event("pkg_download", params)
        except Exception:  # pylint: disable=broad-except
            pass  # telemetry must never change the install

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


def _download_outcome(attempt: DownloadAttempt, exc: BaseException) -> str:
    if attempt.completed:
        return "completed"
    for cls, outcome in (
        (TransferInterruptedError, "interrupted"),
        (ResponseValidationError, "rejected"),
        (ArtifactVerificationError, "verification_failed"),
        (KeyboardInterrupt, "cancelled"),
    ):
        if isinstance(exc, cls):
            return outcome
    return "error"

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

from platformio.package.exception import UnknownPackageError
from platformio.package.meta import PackageSpec


class PlatformPackagesMixin(object):
    def get_package_spec(self, name, version=None):
        return PackageSpec(
            owner=self.packages[name].get("owner"),
            name=name,
            requirements=version or self.packages[name].get("version"),
        )

    def get_package(self, name, spec=None):
        if not name:
            return None
        return self.pm.get_package(spec or self.get_package_spec(name))

    def get_package_dir(self, name):
        pkg = self.get_package(name)
        return pkg.path if pkg else None

    def get_package_version(self, name):
        pkg = self.get_package(name)
        return str(pkg.metadata.version) if pkg else None

    def get_installed_packages(self, with_optional=False):
        result = []
        for name, options in self.packages.items():
            versions = [options.get("version")]
            if with_optional:
                versions.extend(options.get("optionalVersions", []))
            for version in versions:
                if not version:
                    continue
                pkg = self.get_package(name, self.get_package_spec(name, version))
                if pkg:
                    result.append(pkg)
        return result

    def dump_used_packages(self):
        result = []
        for name, options in self.packages.items():
            if options.get("optional"):
                continue
            pkg = self.get_package(name)
            if not pkg or not pkg.metadata:
                continue
            item = {"name": pkg.metadata.name, "version": str(pkg.metadata.version)}
            if pkg.metadata.spec.external:
                item["src_url"] = pkg.metadata.spec.url
            result.append(item)
        return result

    def autoinstall_runtime_packages(self):
        for name, options in self.packages.items():
            if options.get("optional", False):
                continue
            if self.get_package(name):
                continue
            self.pm.install(self.get_package_spec(name))
        return True

    def install_packages(  # pylint: disable=too-many-arguments
        self,
        with_packages=None,
        without_packages=None,
        skip_default_package=False,
        silent=False,
        force=False,
    ):
        with_packages = set(self._find_pkg_names(with_packages or []))
        without_packages = set(self._find_pkg_names(without_packages or []))

        upkgs = with_packages | without_packages
        ppkgs = set(self.packages)
        if not upkgs.issubset(ppkgs):
            raise UnknownPackageError(", ".join(upkgs - ppkgs))

        for name, options in self.packages.items():
            if name in without_packages:
                continue
            if name in with_packages or not (
                skip_default_package or options.get("optional", False)
            ):
                self.pm.install(self.get_package_spec(name), silent=silent, force=force)

        return True

    def _find_pkg_names(self, candidates):
        result = []
        for candidate in candidates:
            found = False

            # lookup by package types
            for _name, _opts in self.packages.items():
                if _opts.get("type") == candidate:
                    result.append(_name)
                    found = True

            if (
                self.frameworks
                and candidate.startswith("framework-")
                and candidate[10:] in self.frameworks
            ):
                result.append(self.frameworks[candidate[10:]]["package"])
                found = True

            if not found:
                result.append(candidate)

        return result

    def update_packages(self, only_check=False):
        for pkg in self.get_installed_packages():
            self.pm.update(
                pkg,
                to_spec=self.get_package_spec(pkg.metadata.name),
                only_check=only_check,
                show_incompatible=False,
            )

    def are_outdated_packages(self):
        for pkg in self.get_installed_packages():
            if self.pm.outdated(
                pkg, self.get_package_spec(pkg.metadata.name)
            ).is_outdated(allow_incompatible=False):
                return True
        return False

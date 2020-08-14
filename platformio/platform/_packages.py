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


class PlatformPackagesMixin(object):
    def install_packages(  # pylint: disable=too-many-arguments
        self,
        with_packages=None,
        without_packages=None,
        skip_default_package=False,
        silent=False,
        force=False,
    ):
        with_packages = set(self.find_pkg_names(with_packages or []))
        without_packages = set(self.find_pkg_names(without_packages or []))

        upkgs = with_packages | without_packages
        ppkgs = set(self.packages)
        if not upkgs.issubset(ppkgs):
            raise UnknownPackageError(", ".join(upkgs - ppkgs))

        for name, opts in self.packages.items():
            version = opts.get("version", "")
            if name in without_packages:
                continue
            if name in with_packages or not (
                skip_default_package or opts.get("optional", False)
            ):
                if ":" in version:
                    self.pm.install(
                        "%s=%s" % (name, version), silent=silent, force=force
                    )
                else:
                    self.pm.install(name, version, silent=silent, force=force)

        return True

    def find_pkg_names(self, candidates):
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
        for name, manifest in self.get_installed_packages().items():
            requirements = self.packages[name].get("version", "")
            if ":" in requirements:
                _, requirements, __ = self.pm.parse_pkg_uri(requirements)
            self.pm.update(manifest["__pkg_dir"], requirements, only_check)

    def get_installed_packages(self):
        items = {}
        for name in self.packages:
            pkg_dir = self.get_package_dir(name)
            if pkg_dir:
                items[name] = self.pm.load_manifest(pkg_dir)
        return items

    def are_outdated_packages(self):
        for name, manifest in self.get_installed_packages().items():
            requirements = self.packages[name].get("version", "")
            if ":" in requirements:
                _, requirements, __ = self.pm.parse_pkg_uri(requirements)
            if self.pm.outdated(manifest["__pkg_dir"], requirements):
                return True
        return False

    def get_package_dir(self, name):
        version = self.packages[name].get("version", "")
        if ":" in version:
            return self.pm.get_package_dir(
                *self.pm.parse_pkg_uri("%s=%s" % (name, version))
            )
        return self.pm.get_package_dir(name, version)

    def get_package_version(self, name):
        pkg_dir = self.get_package_dir(name)
        if not pkg_dir:
            return None
        return self.pm.load_manifest(pkg_dir).get("version")

    def dump_used_packages(self):
        result = []
        for name, options in self.packages.items():
            if options.get("optional"):
                continue
            pkg_dir = self.get_package_dir(name)
            if not pkg_dir:
                continue
            manifest = self.pm.load_manifest(pkg_dir)
            item = {"name": manifest["name"], "version": manifest["version"]}
            if manifest.get("__src_url"):
                item["src_url"] = manifest.get("__src_url")
            result.append(item)
        return result

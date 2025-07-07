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

from platformio.package.meta import PackageSpec


class PlatformPackagesMixin:
    def get_package_spec(self, name, version=None):
        return PackageSpec(
            owner=self.packages[name].get("owner"),  # type: ignore
            name=name,
            requirements=version or self.packages[name].get("version"),  # type: ignore
        )

    def get_package(self, name, spec=None):
        if not name:
            return None
        return self.pm.get_package(spec or self.get_package_spec(name))  # type: ignore

    def get_package_dir(self, name):
        pkg = self.get_package(name)
        return pkg.path if pkg else None

    def get_package_version(self, name):
        pkg = self.get_package(name)
        return str(pkg.metadata.version) if pkg else None

    def get_installed_packages(self, with_optional=True, with_optional_versions=False):
        result = []
        for name, options in dict(sorted(self.packages.items())).items():  # type: ignore
            if not with_optional and options.get("optional"):
                continue
            versions = [options.get("version")]
            if with_optional_versions:
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
        for name, options in self.packages.items():  # type: ignore
            if options.get("optional"):
                continue
            pkg = self.get_package(name)
            if not pkg or not pkg.metadata:
                continue
            item = {"name": pkg.metadata.name, "version": str(pkg.metadata.version)}
            if pkg.metadata.spec.external:
                item["src_url"] = pkg.metadata.spec.uri
            result.append(item)
        return result

    def install_package(self, name, spec=None, force=False):
        return self.pm.install(spec or self.get_package_spec(name), force=force)  # type: ignore

    def install_required_packages(self, force=False):
        assert self.pm is not None  # type: ignore
        for name, options in self.packages.items():  # type: ignore
            if options.get("optional"):
                continue
            self.install_package(name, force=force)

    def uninstall_packages(self):
        for pkg in self.get_installed_packages():  # type: ignore
            self.pm.uninstall(pkg)  # type: ignore

    def update_packages(self):
        for pkg in self.get_installed_packages():  # type: ignore
            self.pm.update(pkg, to_spec=self.get_package_spec(pkg.metadata.name))  # type: ignore

    def are_outdated_packages(self):
        for pkg in self.get_installed_packages():  # type: ignore
            if self.pm.outdated(  # type: ignore
                pkg, self.get_package_spec(pkg.metadata.name)  # type: ignore
            ).is_outdated(allow_incompatible=False):
                return True
        return False

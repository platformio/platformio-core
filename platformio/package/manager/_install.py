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

import hashlib
import os
import shutil
import tempfile

import click

from platformio import app, compat, fs, util
from platformio.package.exception import PackageException, UnknownPackageError
from platformio.package.meta import PackageCompatibility, PackageItem
from platformio.package.unpack import FileUnpacker
from platformio.package.vcsclient import VCSClientFactory


class PackageManagerInstallMixin:
    _INSTALL_HISTORY = None  # avoid circle dependencies

    @staticmethod
    def unpack(src, dst):
        with_progress = not app.is_disabled_progressbar()
        try:
            with FileUnpacker(src) as fu:
                return fu.unpack(dst, with_progress=with_progress)
        except IOError as exc:
            if not with_progress:
                raise exc
            with FileUnpacker(src) as fu:
                return fu.unpack(dst, with_progress=False)

    def install(self, spec, skip_dependencies=False, force=False):
        try:
            self.lock()
            pkg = self._install(spec, skip_dependencies=skip_dependencies, force=force)
            self.memcache_reset()
            self.cleanup_expired_downloads()
            return pkg
        finally:
            self.unlock()

    def _install(
        self,
        spec,
        skip_dependencies=False,
        force=False,
        compatibility: PackageCompatibility = None,
    ):
        spec = self.ensure_spec(spec)

        # avoid circle dependencies
        if not self._INSTALL_HISTORY:
            self._INSTALL_HISTORY = {}
        if not force and spec in self._INSTALL_HISTORY:
            return self._INSTALL_HISTORY[spec]

        # check if package is already installed
        pkg = self.get_package(spec)

        # if a forced installation
        if pkg and force:
            self.uninstall(pkg)
            pkg = None

        if pkg:
            # avoid RecursionError for circular_dependencies
            self._INSTALL_HISTORY[spec] = pkg

            self.log.debug(
                click.style(
                    "{name}@{version} is already installed".format(
                        **pkg.metadata.as_dict()
                    ),
                    fg="yellow",
                )
            )
            # ensure package dependencies are installed
            if not skip_dependencies:
                self.install_dependencies(pkg, print_header=False)
            return pkg

        self.log.info("Installing %s" % click.style(spec.humanize(), fg="cyan"))

        if spec.external:
            pkg = self.install_from_uri(spec.uri, spec)
        else:
            pkg = self.install_from_registry(
                spec,
                search_qualifiers=(
                    compatibility.to_search_qualifiers(
                        ["platforms", "frameworks", "authors"]
                    )
                    if compatibility
                    else None
                ),
            )

        if not pkg or not pkg.metadata:
            raise PackageException(
                "Could not install package '%s' for '%s' system"
                % (spec.humanize(), util.get_systype())
            )

        self.call_pkg_script(pkg, "postinstall")

        self.log.info(
            click.style(
                "{name}@{version} has been installed!".format(**pkg.metadata.as_dict()),
                fg="green",
            )
        )

        self.memcache_reset()
        # avoid RecursionError for circular_dependencies
        self._INSTALL_HISTORY[spec] = pkg

        if not skip_dependencies:
            self.install_dependencies(pkg)

        return pkg

    def install_dependencies(self, pkg, print_header=True):
        assert isinstance(pkg, PackageItem)
        dependencies = self.get_pkg_dependencies(pkg)
        if not dependencies:
            return
        if print_header:
            self.log.info("Resolving dependencies...")
        for dependency in dependencies:
            try:
                self.install_dependency(dependency)
            except UnknownPackageError:
                if dependency.get("owner"):
                    self.log.warning(
                        click.style(
                            "Warning! Could not install `%s` dependency "
                            "for the`%s` package" % (dependency, pkg.metadata.name),
                            fg="yellow",
                        )
                    )

    def install_dependency(self, dependency):
        dependency_compatibility = PackageCompatibility.from_dependency(dependency)
        if self.compatibility and not dependency_compatibility.is_compatible(
            self.compatibility
        ):
            self.log.debug(
                click.style(
                    "Skip incompatible `%s` dependency with `%s`"
                    % (dependency, self.compatibility),
                    fg="yellow",
                )
            )
            return None
        return self._install(
            spec=self.dependency_to_spec(dependency),
            compatibility=dependency_compatibility,
        )

    def install_from_uri(self, uri, spec, checksum=None):
        spec = self.ensure_spec(spec)

        if spec.symlink:
            return self.install_symlink(spec)

        tmp_dir = tempfile.mkdtemp(prefix="pkg-installing-", dir=self.get_tmp_dir())
        vcs = None
        try:
            if uri.startswith("file://"):
                _uri = uri[7:]
                if os.path.isfile(_uri):
                    self.unpack(_uri, tmp_dir)
                else:
                    fs.rmtree(tmp_dir)
                    shutil.copytree(_uri, tmp_dir, symlinks=True)
            elif uri.startswith(("http://", "https://")):
                dl_path = self.download(uri, checksum)
                assert os.path.isfile(dl_path)
                self.unpack(dl_path, tmp_dir)
            else:
                vcs = VCSClientFactory.new(tmp_dir, uri)
                assert vcs.export()

            root_dir = self.find_pkg_root(tmp_dir, spec)
            pkg_item = PackageItem(
                root_dir,
                self.build_metadata(
                    root_dir, spec, vcs.get_current_revision() if vcs else None
                ),
            )
            pkg_item.dump_meta()
            return self._install_tmp_pkg(pkg_item)
        finally:
            if os.path.isdir(tmp_dir):
                try:
                    fs.rmtree(tmp_dir)
                except:  # pylint: disable=bare-except
                    pass

    def _install_tmp_pkg(self, tmp_pkg):
        assert isinstance(tmp_pkg, PackageItem)
        # validate package version and declared requirements
        if (
            tmp_pkg.metadata.spec.requirements
            and tmp_pkg.metadata.version not in tmp_pkg.metadata.spec.requirements
        ):
            raise PackageException(
                "Package version %s doesn't satisfy requirements %s based on %s"
                % (
                    tmp_pkg.metadata.version,
                    tmp_pkg.metadata.spec.requirements,
                    tmp_pkg.metadata,
                )
            )
        dst_pkg = PackageItem(
            os.path.join(self.package_dir, tmp_pkg.get_safe_dirname())
        )

        # what to do with existing package?
        action = "overwrite"
        if tmp_pkg.metadata.spec.has_custom_name():
            action = "overwrite"
            dst_pkg = PackageItem(
                os.path.join(self.package_dir, tmp_pkg.metadata.spec.name)
            )
        elif dst_pkg.metadata:
            if dst_pkg.metadata.spec.external:
                if dst_pkg.metadata.spec.uri != tmp_pkg.metadata.spec.uri:
                    action = "detach-existing"
            elif (
                dst_pkg.metadata.version != tmp_pkg.metadata.version
                or dst_pkg.metadata.spec.owner != tmp_pkg.metadata.spec.owner
            ):
                action = (
                    "detach-existing"
                    if tmp_pkg.metadata.version > dst_pkg.metadata.version
                    else "detach-new"
                )

        def _cleanup_dir(path):
            if os.path.isdir(path):
                fs.rmtree(path)

        if action == "detach-existing":
            target_dirname = "%s@%s" % (
                tmp_pkg.get_safe_dirname(),
                dst_pkg.metadata.version,
            )
            if dst_pkg.metadata.spec.uri:
                target_dirname = "%s@src-%s" % (
                    tmp_pkg.get_safe_dirname(),
                    hashlib.md5(
                        compat.hashlib_encode_data(dst_pkg.metadata.spec.uri)
                    ).hexdigest(),
                )
            # move existing into the new place
            pkg_dir = os.path.join(self.package_dir, target_dirname)
            _cleanup_dir(pkg_dir)
            shutil.copytree(dst_pkg.path, pkg_dir, symlinks=True)
            # move new source to the destination location
            _cleanup_dir(dst_pkg.path)
            shutil.copytree(tmp_pkg.path, dst_pkg.path, symlinks=True)
            return PackageItem(dst_pkg.path)

        if action == "detach-new":
            target_dirname = "%s@%s" % (
                tmp_pkg.get_safe_dirname(),
                tmp_pkg.metadata.version,
            )
            if tmp_pkg.metadata.spec.external:
                target_dirname = "%s@src-%s" % (
                    tmp_pkg.get_safe_dirname(),
                    hashlib.md5(
                        compat.hashlib_encode_data(tmp_pkg.metadata.spec.uri)
                    ).hexdigest(),
                )
            pkg_dir = os.path.join(self.package_dir, target_dirname)
            _cleanup_dir(pkg_dir)
            shutil.copytree(tmp_pkg.path, pkg_dir, symlinks=True)
            return PackageItem(pkg_dir)

        # otherwise, overwrite existing
        _cleanup_dir(dst_pkg.path)
        shutil.copytree(tmp_pkg.path, dst_pkg.path, symlinks=True)
        return PackageItem(dst_pkg.path)

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
from platformio.package.exception import MissingPackageManifestError, PackageException
from platformio.package.meta import PackageSourceItem, PackageSpec
from platformio.package.unpack import FileUnpacker
from platformio.package.vcsclient import VCSClientFactory


class PackageManagerInstallMixin(object):

    _INSTALL_HISTORY = None  # avoid circle dependencies

    @staticmethod
    def unpack(src, dst):
        with_progress = not app.is_disabled_progressbar()
        try:
            with FileUnpacker(src) as fu:
                return fu.unpack(dst, with_progress=with_progress)
        except IOError as e:
            if not with_progress:
                raise e
            with FileUnpacker(src) as fu:
                return fu.unpack(dst, with_progress=False)

    def install(self, spec, silent=False, force=False):
        try:
            self.lock()
            pkg = self._install(spec, silent=silent, force=force)
            self.memcache_reset()
            self.cleanup_expired_downloads()
            return pkg
        finally:
            self.unlock()

    def _install(self, spec, search_filters=None, silent=False, force=False):
        spec = self.ensure_spec(spec)

        # avoid circle dependencies
        if not self._INSTALL_HISTORY:
            self._INSTALL_HISTORY = {}
        if spec in self._INSTALL_HISTORY:
            return self._INSTALL_HISTORY[spec]

        # check if package is already installed
        pkg = self.get_package(spec)

        # if a forced installation
        if pkg and force:
            self.uninstall(pkg, silent=silent)
            pkg = None

        if pkg:
            if not silent:
                click.secho(
                    "{name} @ {version} is already installed".format(
                        **pkg.metadata.as_dict()
                    ),
                    fg="yellow",
                )
            return pkg

        if not silent:
            msg = "Installing %s" % click.style(spec.humanize(), fg="cyan")
            self.print_message(msg)

        if spec.external:
            pkg = self.install_from_url(spec.url, spec, silent=silent)
        else:
            pkg = self.install_from_registry(spec, search_filters, silent=silent)

        if not pkg or not pkg.metadata:
            raise PackageException(
                "Could not install package '%s' for '%s' system"
                % (spec.humanize(), util.get_systype())
            )

        if not silent:
            self.print_message(
                click.style(
                    "{name} @ {version} has been successfully installed!".format(
                        **pkg.metadata.as_dict()
                    ),
                    fg="green",
                )
            )

        self.memcache_reset()
        self._install_dependencies(pkg, silent)
        self._INSTALL_HISTORY[spec] = pkg
        return pkg

    def _install_dependencies(self, pkg, silent=False):
        assert isinstance(pkg, PackageSourceItem)
        manifest = self.load_manifest(pkg)
        if not manifest.get("dependencies"):
            return
        if not silent:
            self.print_message(click.style("Installing dependencies...", fg="yellow"))
        for dependency in manifest.get("dependencies"):
            if not self._install_dependency(dependency, silent) and not silent:
                click.secho(
                    "Warning! Could not install dependency %s for package '%s'"
                    % (dependency, pkg.metadata.name),
                    fg="yellow",
                )

    def _install_dependency(self, dependency, silent=False):
        spec = PackageSpec(
            name=dependency.get("name"), requirements=dependency.get("version")
        )
        search_filters = {
            key: value
            for key, value in dependency.items()
            if key in ("authors", "platforms", "frameworks")
        }
        return self._install(spec, search_filters=search_filters or None, silent=silent)

    def install_from_url(self, url, spec, checksum=None, silent=False):
        spec = self.ensure_spec(spec)
        tmp_dir = tempfile.mkdtemp(prefix="pkg-installing-", dir=self.get_tmp_dir())
        vcs = None
        try:
            if url.startswith("file://"):
                _url = url[7:]
                if os.path.isfile(_url):
                    self.unpack(_url, tmp_dir)
                else:
                    fs.rmtree(tmp_dir)
                    shutil.copytree(_url, tmp_dir, symlinks=True)
            elif url.startswith(("http://", "https://")):
                dl_path = self.download(url, checksum, silent=silent)
                assert os.path.isfile(dl_path)
                self.unpack(dl_path, tmp_dir)
            else:
                vcs = VCSClientFactory.new(tmp_dir, url)
                assert vcs.export()

            root_dir = self.find_pkg_root(tmp_dir, spec)
            pkg_item = PackageSourceItem(
                root_dir,
                self.build_metadata(
                    root_dir, spec, vcs.get_current_revision() if vcs else None
                ),
            )
            pkg_item.dump_meta()
            return self._install_tmp_pkg(pkg_item)
        finally:
            if os.path.isdir(tmp_dir):
                fs.rmtree(tmp_dir)

    def _install_tmp_pkg(self, tmp_pkg):
        assert isinstance(tmp_pkg, PackageSourceItem)
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
        dst_pkg = PackageSourceItem(
            os.path.join(self.package_dir, tmp_pkg.get_safe_dirname())
        )

        # what to do with existing package?
        action = "overwrite"
        if tmp_pkg.metadata.spec.has_custom_name():
            action = "overwrite"
            dst_pkg = PackageSourceItem(
                os.path.join(self.package_dir, tmp_pkg.metadata.spec.name)
            )
        elif dst_pkg.metadata and dst_pkg.metadata.spec.external:
            if dst_pkg.metadata.spec.url != tmp_pkg.metadata.spec.url:
                action = "detach-existing"
        elif tmp_pkg.metadata.spec.external:
            action = "detach-new"
        elif dst_pkg.metadata and (
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
            if dst_pkg.metadata.spec.url:
                target_dirname = "%s@src-%s" % (
                    tmp_pkg.get_safe_dirname(),
                    hashlib.md5(
                        compat.hashlib_encode_data(dst_pkg.metadata.spec.url)
                    ).hexdigest(),
                )
            # move existing into the new place
            pkg_dir = os.path.join(self.package_dir, target_dirname)
            _cleanup_dir(pkg_dir)
            shutil.move(dst_pkg.path, pkg_dir)
            # move new source to the destination location
            _cleanup_dir(dst_pkg.path)
            shutil.move(tmp_pkg.path, dst_pkg.path)
            return PackageSourceItem(dst_pkg.path)

        if action == "detach-new":
            target_dirname = "%s@%s" % (
                tmp_pkg.get_safe_dirname(),
                tmp_pkg.metadata.version,
            )
            if tmp_pkg.metadata.spec.external:
                target_dirname = "%s@src-%s" % (
                    tmp_pkg.get_safe_dirname(),
                    hashlib.md5(
                        compat.hashlib_encode_data(tmp_pkg.metadata.spec.url)
                    ).hexdigest(),
                )
            pkg_dir = os.path.join(self.package_dir, target_dirname)
            _cleanup_dir(pkg_dir)
            shutil.move(tmp_pkg.path, pkg_dir)
            return PackageSourceItem(pkg_dir)

        # otherwise, overwrite existing
        _cleanup_dir(dst_pkg.path)
        shutil.move(tmp_pkg.path, dst_pkg.path)
        return PackageSourceItem(dst_pkg.path)

    def get_installed(self):
        result = []
        for name in os.listdir(self.package_dir):
            pkg_dir = os.path.join(self.package_dir, name)
            if not os.path.isdir(pkg_dir):
                continue
            pkg = PackageSourceItem(pkg_dir)
            if not pkg.metadata:
                try:
                    spec = self.build_legacy_spec(pkg_dir)
                    pkg.metadata = self.build_metadata(pkg_dir, spec)
                except MissingPackageManifestError:
                    pass
            if pkg.metadata:
                result.append(pkg)
        return result

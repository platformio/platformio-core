# Copyright 2014-present Ivan Kravets <me@ikravets.com>
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

import json
import os
from os.path import dirname, isdir, isfile, islink, join
from shutil import copyfile, copytree, rmtree
from tempfile import mkdtemp

import click
import requests
import semantic_version

from platformio import exception, telemetry, util
from platformio.downloader import FileDownloader
from platformio.unpacker import FileUnpacker
from platformio.vcsclient import VCSClientFactory


class PackageRepoIterator(object):

    _MANIFEST_CACHE = {}

    def __init__(self, package, repositories):
        assert isinstance(repositories, list)
        self.package = package
        self.repositories = iter(repositories)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        manifest = {}
        repo = next(self.repositories)
        if isinstance(repo, dict):
            manifest = repo
        elif repo in PackageRepoIterator._MANIFEST_CACHE:
            manifest = PackageRepoIterator._MANIFEST_CACHE[repo]
        else:
            r = None
            try:
                r = requests.get(repo, headers=util.get_request_defheaders())
                r.raise_for_status()
                manifest = r.json()
            except:  # pylint: disable=bare-except
                pass
            finally:
                if r:
                    r.close()
            PackageRepoIterator._MANIFEST_CACHE[repo] = manifest

        if self.package in manifest:
            return manifest[self.package]
        else:
            return self.next()


class PkgRepoMixin(object):

    @staticmethod
    def max_satisfying_repo_version(versions, requirements=None):
        item = None
        systype = util.get_systype()
        if requirements is not None:
            requirements = str(requirements)
        for v in versions:
            if isinstance(v['version'], int):
                continue
            if v['system'] not in ("all", "*") and systype not in v['system']:
                continue
            if requirements and not semantic_version.match(
                    requirements, v['version']):
                continue
            if item is None or semantic_version.compare(
                    v['version'], item['version']) == 1:
                item = v
        return item

    def get_latest_repo_version(self, name, requirements):
        version = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            if (not version or semantic_version.compare(
                    pkgdata['version'], version) == 1):
                version = pkgdata['version']
        return version


class PkgInstallerMixin(object):

    VCS_MANIFEST_NAME = ".piopkgmanager.json"

    def get_manifest_path(self, pkg_dir):
        if not isdir(pkg_dir):
            return None
        manifest_path = join(pkg_dir, self.manifest_name)
        if isfile(manifest_path):
            return manifest_path
        for item in os.listdir(pkg_dir):
            if not isdir(join(pkg_dir, item)):
                continue
            if isfile(join(pkg_dir, item, self.VCS_MANIFEST_NAME)):
                return join(pkg_dir, item, self.VCS_MANIFEST_NAME)
        return None

    def manifest_exists(self, pkg_dir):
        return self.get_manifest_path(pkg_dir) is not None

    def load_manifest(self, pkg_dir):
        manifest_path = self.get_manifest_path(pkg_dir)
        if manifest_path:
            manifest = util.load_json(manifest_path)
            manifest['_manifest_path'] = manifest_path
            manifest['__pkg_dir'] = pkg_dir
            return manifest
        return None

    def _install_from_piorepo(self, name, requirements):
        pkg_dir = None
        pkgdata = None
        versions = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            try:
                pkg_dir = self._install_from_url(
                    name, pkgdata['url'], requirements, pkgdata.get("sha1"))
                break
            except Exception as e:  # pylint: disable=broad-except
                click.secho("Warning! Package Mirror: %s" % e, fg="yellow")
                click.secho("Looking for another mirror...", fg="yellow")

        if versions is None:
            raise exception.UnknownPackage(name)
        elif not pkgdata:
            if "platform" in self.manifest_name:
                raise exception.UndefinedPlatformVersion(
                    name, requirements or "latest")
            else:
                raise exception.UndefinedPackageVersion(
                    name, requirements or "latest", util.get_systype())
        return pkg_dir

    def _install_from_url(self, name, url, requirements=None, sha1=None):
        pkg_dir = None
        tmp_dir = mkdtemp("-package", "installing-", self.package_dir)

        # Handle GitHub URL (https://github.com/user/repo.git)
        if url.endswith(".git") and not url.startswith("git"):
            url = "git+" + url

        try:
            if url.startswith("file://"):
                url = url[7:]
                if isfile(url):
                    self.unpack(url, tmp_dir)
                else:
                    rmtree(tmp_dir)
                    copytree(url, tmp_dir)
            elif url.startswith(("http://", "https://", "ftp://")):
                dlpath = self.download(url, tmp_dir, sha1)
                assert isfile(dlpath)
                self.unpack(dlpath, tmp_dir)
                os.remove(dlpath)
            else:
                vcs = VCSClientFactory.newClient(tmp_dir, url)
                assert vcs.export()
                with open(join(vcs.storage_dir,
                               self.VCS_MANIFEST_NAME), "w") as fp:
                    json.dump({
                        "name": name,
                        "version": "0.0.0+rev%s" % vcs.get_latest_revision(),
                        "url": url}, fp)

            self._check_pkg_structure(tmp_dir)
            pkg_dir = self._install_from_tmp_dir(tmp_dir, requirements)
        finally:
            if isdir(tmp_dir):
                rmtree(tmp_dir)
        return pkg_dir

    def _check_pkg_structure(self, pkg_dir):
        if self.manifest_exists(pkg_dir):
            return True

        for root, _, _ in os.walk(pkg_dir):
            if not self.manifest_exists(root):
                continue
            # copy contents to the root of package directory
            for item in os.listdir(root):
                item_path = join(root, item)
                if isfile(item_path):
                    copyfile(item_path, join(pkg_dir, item))
                elif isdir(item_path):
                    copytree(item_path, join(pkg_dir, item), symlinks=True)
            # remove not used contents
            while True:
                rmtree(root)
                root = dirname(root)
                if root == pkg_dir:
                    break
            break

        if self.manifest_exists(pkg_dir):
            return True

        raise exception.PlatformioException(
            "Could not find '%s' manifest file in the package" %
            self.manifest_name)

    def _install_from_tmp_dir(self, tmp_dir, requirements=None):
        tmpmanifest = self.load_manifest(tmp_dir)
        assert set(["name", "version"]) <= set(tmpmanifest.keys())
        name = tmpmanifest['name']
        pkg_dir = join(self.package_dir, name)

        # package should satisfy requirements
        if requirements:
            assert semantic_version.match(
                requirements, tmpmanifest['version'])

        if self.manifest_exists(pkg_dir):
            manifest = self.load_manifest(pkg_dir)
            cmp_result = semantic_version.compare(
                tmpmanifest['version'], manifest['version'])
            if cmp_result == 1:
                # if main package version < new package, backup it
                os.rename(pkg_dir, join(
                    self.package_dir, "%s@%s" % (name, manifest['version'])))
            elif cmp_result == -1:
                pkg_dir = join(
                    self.package_dir, "%s@%s" % (name, tmpmanifest['version']))

        # remove previous/not-satisfied package
        if isdir(pkg_dir):
            rmtree(pkg_dir)
        os.rename(tmp_dir, pkg_dir)
        assert isdir(pkg_dir)
        return pkg_dir


class BasePkgManager(PkgRepoMixin, PkgInstallerMixin):

    _INSTALLED_CACHE = {}

    def __init__(self, package_dir, repositories=None):
        self.repositories = repositories
        self.package_dir = package_dir
        if not isdir(self.package_dir):
            os.makedirs(self.package_dir)
        assert isdir(self.package_dir)

    @property
    def manifest_name(self):
        raise NotImplementedError()

    @staticmethod
    def download(url, dest_dir, sha1=None):
        fd = FileDownloader(url, dest_dir)
        fd.start()
        if sha1:
            fd.verify(sha1)
        return fd.get_filepath()

    @staticmethod
    def unpack(source_path, dest_dir):
        fu = FileUnpacker(source_path, dest_dir)
        return fu.start()

    def reset_cache(self):
        if self.package_dir in BasePkgManager._INSTALLED_CACHE:
            del BasePkgManager._INSTALLED_CACHE[self.package_dir]

    def print_message(self, message, nl=True):
        click.echo("%s: %s" % (self.__class__.__name__, message), nl=nl)

    def get_installed(self):
        if self.package_dir in BasePkgManager._INSTALLED_CACHE:
            return BasePkgManager._INSTALLED_CACHE[self.package_dir]
        items = []
        for p in sorted(os.listdir(self.package_dir)):
            manifest = self.load_manifest(join(self.package_dir, p))
            if not manifest:
                continue
            assert set(["name", "version"]) <= set(manifest.keys())
            items.append(manifest)
        BasePkgManager._INSTALLED_CACHE[self.package_dir] = items
        return items

    def is_installed(self, name, requirements=None):
        installed = self.get_installed()
        reqspec = None
        if requirements:
            try:
                reqspec = semantic_version.Spec(requirements)
            except ValueError:
                pass

        if not reqspec:
            return any([p['name'] == name for p in installed])

        for p in installed:
            if p['name'] != name:
                continue
            elif reqspec.match(semantic_version.Version(p['version'])):
                return True
        return None

    def max_installed_version(self, name, requirements=None):
        best = None
        reqspec = None
        if requirements:
            try:
                reqspec = semantic_version.Spec(requirements)
            except ValueError:
                pass

        for manifest in self.get_installed():
            if manifest['name'] != name:
                continue
            elif reqspec and not reqspec.match(
                    semantic_version.Version(manifest['version'])):
                continue
            elif (not best or semantic_version.compare(
                    manifest['version'], best['version']) == 1):
                best = manifest

        if best:
            return best.get("__pkg_dir")
        return None

    def install(self, name, requirements, silent=False, trigger_event=True):
        installed = self.is_installed(name, requirements)
        if not installed or not silent:
            self.print_message("Installing %s @ %s:" % (
                click.style(name, fg="cyan"),
                requirements if requirements else "latest"))
        if installed:
            if not silent:
                click.secho("Already installed", fg="yellow")
            return self.max_installed_version(
                name, requirements)

        if (requirements and any([s in requirements for s in ("\\", "/")]) and
                "://" not in requirements and (
                    isfile(requirements) or isdir(requirements))):
            requirements = "file://" + requirements

        if requirements and "://" in requirements:
            pkg_dir = self._install_from_url(name, requirements)
        else:
            pkg_dir = self._install_from_piorepo(name, requirements)
        if not pkg_dir or not self.manifest_exists(pkg_dir):
            raise exception.PackageInstallError(
                name, requirements or "latest", util.get_systype())

        self.reset_cache()
        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Install", label=name)

        return pkg_dir

    def uninstall(self, name, requirements=None, trigger_event=True):
        self.print_message("Uninstalling %s @ %s: \t" % (
            click.style(name, fg="cyan"),
            requirements if requirements else "latest"), nl=False)
        found = False
        for manifest in self.get_installed():
            if manifest['name'] != name:
                continue
            if (requirements and not semantic_version.match(
                    requirements, manifest['version'])):
                continue
            found = True
            if isdir(manifest['__pkg_dir']):
                if islink(manifest['__pkg_dir']):
                    os.unlink(manifest['__pkg_dir'])
                else:
                    rmtree(manifest['__pkg_dir'])

        if not found:
            click.secho("Not installed", fg="yellow")
            return False
        else:
            click.echo("[%s]" % click.style("OK", fg="green"))

        self.reset_cache()
        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Uninstall", label=name)

    def update(self, name, requirements=None):
        self.print_message("Updating %s @ %s:" % (
            click.style(name, fg="yellow"),
            requirements if requirements else "latest"))

        latest_version = self.get_latest_repo_version(name, requirements)
        if latest_version is None:
            click.secho(
                "Ignored! '%s' is not listed in registry" % name,
                fg="yellow")
            return

        current = None
        for manifest in self.get_installed():
            if manifest['name'] != name:
                continue
            if (requirements and not semantic_version.match(
                    requirements, manifest['version'])):
                continue
            if (not current or semantic_version.compare(
                    manifest['version'], current['version']) == 1):
                current = manifest

        if current is None:
            return

        current_version = current['version']
        click.echo("Versions: Current=%s, Latest=%s \t " %
                   (current_version, latest_version), nl=False)

        if current_version == latest_version:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
            return True
        else:
            click.echo("[%s]" % (click.style("Out-of-date", fg="red")))

        self.install(name, latest_version, trigger_event=False)

        telemetry.on_event(
            category=self.__class__.__name__,
            action="Update", label=name)
        return True


class PackageManager(BasePkgManager):

    @property
    def manifest_name(self):
        return "package.json"

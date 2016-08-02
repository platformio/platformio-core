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
from os.path import basename, dirname, isdir, isfile, islink, join
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
        reqspec = None
        if requirements:
            try:
                reqspec = semantic_version.Spec(requirements)
            except ValueError:
                pass

        for v in versions:
            if ("system" in v and v['system'] not in ("all", "*") and
                    systype not in v['system']):
                continue
            specver = semantic_version.Version(v['version'])
            if reqspec and specver not in reqspec:
                continue
            if not item or semantic_version.Version(item['version']) < specver:
                item = v
        return item

    def get_latest_repo_version(self, name, requirements):
        version = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            if not version or semantic_version.compare(pkgdata['version'],
                                                       version) == 1:
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
            manifest['__pkg_dir'] = pkg_dir
            return manifest
        return None

    def check_pkg_structure(self, pkg_dir):
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
                click.secho("Looking for the another mirror...", fg="yellow")

        if versions is None:
            raise exception.UnknownPackage(name)
        elif not pkgdata:
            raise exception.UndefinedPackageVersion(requirements or "latest",
                                                    util.get_systype())
        return pkg_dir

    def _install_from_url(self, name, url, requirements=None, sha1=None):
        pkg_dir = None
        tmp_dir = mkdtemp("-package", "installing-", self.package_dir)

        try:
            if url.startswith("file://"):
                url = url[7:]
                if isfile(url):
                    self.unpack(url, tmp_dir)
                else:
                    rmtree(tmp_dir)
                    copytree(url, tmp_dir)
            elif url.startswith(("http://", "https://")):
                dlpath = self.download(url, tmp_dir, sha1)
                assert isfile(dlpath)
                self.unpack(dlpath, tmp_dir)
                os.remove(dlpath)
            else:
                vcs = VCSClientFactory.newClient(tmp_dir, url)
                assert vcs.export()
                with open(join(vcs.storage_dir, self.VCS_MANIFEST_NAME),
                          "w") as fp:
                    json.dump({
                        "name": name,
                        "version": vcs.get_current_revision(),
                        "url": url,
                        "requirements": requirements
                    }, fp)

            self.check_pkg_structure(tmp_dir)
            pkg_dir = self._install_from_tmp_dir(tmp_dir, requirements)
        finally:
            if isdir(tmp_dir):
                rmtree(tmp_dir)
        return pkg_dir

    def _install_from_tmp_dir(self, tmp_dir, requirements=None):
        tmpmanifest = self.load_manifest(tmp_dir)
        assert set(["name", "version"]) <= set(tmpmanifest.keys())
        name = tmpmanifest['name']
        pkg_dir = join(self.package_dir, name)
        if "id" in tmpmanifest:
            name += "_ID%d" % tmpmanifest['id']
            pkg_dir = join(self.package_dir, name)

        # package should satisfy requirements
        if requirements:
            mismatch_error = (
                "Package version %s doesn't satisfy requirements %s" % (
                    tmpmanifest['version'], requirements))
            try:
                reqspec = semantic_version.Spec(requirements)
                tmpmanver = semantic_version.Version(
                    tmpmanifest['version'], partial=True)
                assert tmpmanver in reqspec, mismatch_error

                if self.manifest_exists(pkg_dir):
                    curmanifest = self.load_manifest(pkg_dir)
                    curmanver = semantic_version.Version(
                        curmanifest['version'], partial=True)
                    # if current package version < new package, backup it
                    if tmpmanver > curmanver:
                        os.rename(pkg_dir, join(self.package_dir, "%s@%s" % (
                            name, curmanifest['version'])))
                    elif tmpmanver < curmanver:
                        pkg_dir = join(self.package_dir, "%s@%s" %
                                       (name, tmpmanifest['version']))
            except ValueError:
                assert tmpmanifest['version'] == requirements, mismatch_error

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

    @staticmethod
    def parse_pkg_name(  # pylint: disable=too-many-branches
            text, requirements=None):
        text = str(text)
        if not requirements and "@" in text and not text.startswith("git@"):
            text, requirements = text.rsplit("@", 1)
        if text.isdigit():
            text = "id=" + text

        url_marker = "://"
        name, url = (None, text)
        if "=" in text and not text.startswith("id="):
            name, url = text.split("=", 1)

        # Handle GitHub URL (https://github.com/user/package)
        if url.startswith("https://github.com/") and \
           not url.endswith((".zip", ".tar.gz")):
            url = "git+" + url
        # Handle Developer Mbed URL
        # (https://developer.mbed.org/users/user/code/package/)
        if url.startswith("https://developer.mbed.org"):
            url = "hg+" + url

        # git@github.com:user/package.git
        if url.startswith("git@"):
            url_marker = "git@"

        if any([s in url for s in ("\\", "/")]) and url_marker not in url:
            if isfile(url) or isdir(url):
                url = "file://" + url
            elif url.count("/") == 1 and not url.startswith("git@"):
                url = "git+https://github.com/" + url
        if url_marker in url and not name:
            _url = url.split("#", 1)[0] if "#" in url else url
            if _url.endswith(("\\", "/")):
                _url = _url[:-1]
            name = basename(_url)
            if "." in name and not name.startswith("."):
                name = name.split(".", 1)[0]

        if url_marker not in url:
            url = None
        return (name or text, requirements, url)

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

    def get_installed_dir(self, name, requirements=None, url=None):
        pkg_id = int(name[3:]) if name.startswith("id=") else 0
        best = None
        reqspec = None
        if requirements:
            try:
                reqspec = semantic_version.Spec(requirements)
            except ValueError:
                pass

        for manifest in self.get_installed():
            if pkg_id and manifest.get("id") != pkg_id:
                continue
            elif not pkg_id and manifest['name'] != name:
                continue
            elif not reqspec and requirements:
                if requirements == manifest['version']:
                    best = manifest
                    break
                continue
            try:
                if reqspec and not reqspec.match(
                        semantic_version.Version(
                            manifest['version'], partial=True)):
                    continue
                elif not best or (semantic_version.Version(
                        manifest['version'], partial=True) >
                                  semantic_version.Version(
                                      best['version'], partial=True)):
                    best = manifest
            except ValueError:
                pass
        if best:
            # check that URL is the same in installed package (VCS)
            if url and best.get("url") != url:
                return None
            return best.get("__pkg_dir")
        return None

    def is_outdated(self, name, requirements=None):
        installed_dir = self.get_installed_dir(name, requirements)
        if not installed_dir:
            click.secho(
                "%s @ %s is not installed" % (name, requirements or "*"),
                fg="yellow")
            return
        manifest_path = self.get_manifest_path(installed_dir)
        if manifest_path.endswith(self.VCS_MANIFEST_NAME):
            return False
        manifest = self.load_manifest(installed_dir)
        return manifest['version'] != self.get_latest_repo_version(
            name, requirements)

    def install(self, name, requirements=None, quiet=False,
                trigger_event=True):
        name, requirements, url = self.parse_pkg_name(name, requirements)
        installed_dir = self.get_installed_dir(name, requirements, url)

        if not installed_dir or not quiet:
            msg = "Installing " + click.style(name, fg="cyan")
            if requirements:
                msg += " @ " + requirements
            self.print_message(msg)
        if installed_dir:
            if not quiet:
                click.secho(
                    "{name} @ {version} is already installed".format(
                        **self.load_manifest(installed_dir)),
                    fg="yellow")
            return installed_dir

        if url:
            pkg_dir = self._install_from_url(name, url, requirements)
        else:
            pkg_dir = self._install_from_piorepo(name, requirements)
        if not pkg_dir or not self.manifest_exists(pkg_dir):
            raise exception.PackageInstallError(name, requirements or "*",
                                                util.get_systype())

        self.reset_cache()
        manifest = self.load_manifest(pkg_dir)

        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Install",
                label=manifest['name'])

        click.secho(
            "{name} @ {version} has been successfully installed!".format(
                **manifest),
            fg="green")

        return pkg_dir

    def uninstall(self, name, requirements=None, trigger_event=True):
        name, requirements, url = self.parse_pkg_name(name, requirements)
        installed_dir = self.get_installed_dir(name, requirements, url)
        if not installed_dir:
            click.secho(
                "%s @ %s is not installed" % (name, requirements or "*"),
                fg="yellow")
            return

        manifest = self.load_manifest(installed_dir)
        click.echo(
            "Uninstalling %s @ %s: \t" % (click.style(
                manifest['name'], fg="cyan"), manifest['version']),
            nl=False)

        if isdir(installed_dir):
            if islink(installed_dir):
                os.unlink(installed_dir)
            else:
                rmtree(installed_dir)

        click.echo("[%s]" % click.style("OK", fg="green"))

        self.reset_cache()
        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Uninstall",
                label=manifest['name'])
        return True

    def update(self, name, requirements=None, only_check=False):
        name, requirements, url = self.parse_pkg_name(name, requirements)
        installed_dir = self.get_installed_dir(name, requirements, url)
        if not installed_dir:
            click.secho(
                "%s @ %s is not installed" % (name, requirements or "*"),
                fg="yellow")
            return

        manifest = self.load_manifest(installed_dir)
        click.echo(
            "Updating %s @ %s: \t" % (click.style(
                manifest['name'], fg="cyan"), manifest['version']),
            nl=False)
        manifest_path = self.get_manifest_path(installed_dir)
        if manifest_path.endswith(self.VCS_MANIFEST_NAME):
            if only_check:
                click.echo("[%s]" % (click.style("Skip", fg="yellow")))
                return
            click.echo("[%s]" % (click.style("Checking", fg="yellow")))
            vcs = VCSClientFactory.newClient(installed_dir, manifest['url'])
            if not vcs.can_be_updated:
                click.secho(
                    "Skip update because repository is fixed "
                    "to %s revision" % manifest['version'],
                    fg="yellow")
                return
            assert vcs.update()
            with open(manifest_path, "w") as fp:
                manifest['version'] = vcs.get_current_revision()
                json.dump(manifest, fp)
        else:
            latest_version = self.get_latest_repo_version(name, requirements)
            if manifest['version'] == latest_version:
                click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
                return
            click.echo("[%s]" % (click.style("Out-of-date", fg="red")))
            if only_check:
                return
            self.install(name, latest_version, trigger_event=False)

        telemetry.on_event(
            category=self.__class__.__name__,
            action="Update",
            label=manifest['name'])
        return True


class PackageManager(BasePkgManager):

    @property
    def manifest_name(self):
        return "package.json"

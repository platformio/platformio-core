# Copyright 2014-present PlatformIO <contact@platformio.org>
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

import codecs
import hashlib
import json
import os
import shutil
from os.path import basename, dirname, getsize, isdir, isfile, islink, join
from tempfile import mkdtemp

import click
import requests
import semantic_version

from platformio import __version__, app, exception, telemetry, util
from platformio.downloader import FileDownloader
from platformio.unpacker import FileUnpacker
from platformio.vcsclient import VCSClientFactory

# pylint: disable=too-many-arguments


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

    PIO_VERSION = semantic_version.Version(util.pepver_to_semver(__version__))

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
            if "system" in v and v['system'] not in ("all", "*") and \
                    systype not in v['system']:
                continue
            if "platformio" in v.get("engines", {}):
                if PkgRepoMixin.PIO_VERSION not in semantic_version.Spec(
                        v['engines']['platformio']):
                    continue
            specver = semantic_version.Version(v['version'])
            if reqspec and specver not in reqspec:
                continue
            if not item or semantic_version.Version(item['version']) < specver:
                item = v
        return item

    def get_latest_repo_version(  # pylint: disable=unused-argument
            self,
            name,
            requirements,
            silent=False):
        version = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            if not version or semantic_version.compare(pkgdata['version'],
                                                       version) == 1:
                version = pkgdata['version']
        return version

    def get_all_repo_versions(self, name):
        result = []
        for versions in PackageRepoIterator(name, self.repositories):
            result.extend([v['version'] for v in versions])
        return sorted(set(result))


class PkgInstallerMixin(object):

    VCS_MANIFEST_NAME = ".piopkgmanager.json"

    FILE_CACHE_VALID = "1m"  # 1 month
    FILE_CACHE_MAX_SIZE = 1024 * 1024

    _INSTALLED_CACHE = {}

    def reset_cache(self):
        if self.package_dir in PkgInstallerMixin._INSTALLED_CACHE:
            del PkgInstallerMixin._INSTALLED_CACHE[self.package_dir]

    def download(self, url, dest_dir, sha1=None):
        cache_key_fname = app.ContentCache.key_from_args(url, "fname")
        cache_key_data = app.ContentCache.key_from_args(url, "data")
        if self.FILE_CACHE_VALID:
            with app.ContentCache() as cc:
                fname = cc.get(cache_key_fname)
                cache_path = cc.get_cache_path(cache_key_data)
                if fname and isfile(cache_path):
                    dst_path = join(dest_dir, fname)
                    shutil.copy(cache_path, dst_path)
                    return dst_path

        fd = FileDownloader(url, dest_dir)
        fd.start()
        if sha1:
            fd.verify(sha1)
        dst_path = fd.get_filepath()
        if not self.FILE_CACHE_VALID or getsize(
                dst_path) > PkgInstallerMixin.FILE_CACHE_MAX_SIZE:
            return dst_path

        with app.ContentCache() as cc:
            cc.set(cache_key_fname, basename(dst_path), self.FILE_CACHE_VALID)
            cc.set(cache_key_data, "DUMMY", self.FILE_CACHE_VALID)
            shutil.copy(dst_path, cc.get_cache_path(cache_key_data))
        return dst_path

    @staticmethod
    def unpack(source_path, dest_dir):
        fu = FileUnpacker(source_path, dest_dir)
        return fu.start()

    @staticmethod
    def generate_install_dirname(manifest):
        name = manifest['name']
        if "id" in manifest:
            name += "_ID%d" % manifest['id']
        return name

    def get_vcs_manifest_path(self, pkg_dir):
        for item in os.listdir(pkg_dir):
            if not isdir(join(pkg_dir, item)):
                continue
            if isfile(join(pkg_dir, item, self.VCS_MANIFEST_NAME)):
                return join(pkg_dir, item, self.VCS_MANIFEST_NAME)
        return None

    def get_manifest_path(self, pkg_dir):
        if not isdir(pkg_dir):
            return None
        manifest_path = self.get_vcs_manifest_path(pkg_dir)
        if manifest_path:
            return manifest_path
        for name in self.manifest_names:
            manifest_path = join(pkg_dir, name)
            if isfile(manifest_path):
                return manifest_path
        return None

    def manifest_exists(self, pkg_dir):
        return self.get_manifest_path(pkg_dir) is not None

    def load_manifest(self, path):  # pylint: disable=too-many-branches
        assert path
        pkg_dir = path
        if isdir(path):
            path = self.get_manifest_path(path)
            if not path:
                return None
        else:
            pkg_dir = dirname(pkg_dir)

        is_vcs_pkg = False
        if isfile(path) and path.endswith(self.VCS_MANIFEST_NAME):
            is_vcs_pkg = True
            pkg_dir = dirname(dirname(path))

        # return from cache
        if self.package_dir in PkgInstallerMixin._INSTALLED_CACHE:
            for manifest in PkgInstallerMixin._INSTALLED_CACHE[
                    self.package_dir]:
                if not is_vcs_pkg and manifest['__pkg_dir'] == pkg_dir:
                    return manifest

        manifest = {}
        if path.endswith(".json"):
            manifest = util.load_json(path)
        elif path.endswith(".properties"):
            with codecs.open(path, encoding="utf-8") as fp:
                for line in fp.readlines():
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    manifest[key.strip()] = value.strip()
        else:
            if "name" not in manifest:
                manifest['name'] = basename(pkg_dir)
            if "version" not in manifest:
                manifest['version'] = "0.0.0"

        manifest['__pkg_dir'] = pkg_dir
        return manifest

    def get_installed(self):
        if self.package_dir in PkgInstallerMixin._INSTALLED_CACHE:
            return PkgInstallerMixin._INSTALLED_CACHE[self.package_dir]
        items = []
        for p in sorted(os.listdir(self.package_dir)):
            pkg_dir = join(self.package_dir, p)
            if not isdir(pkg_dir):
                continue
            manifest = self.load_manifest(pkg_dir)
            if not manifest:
                continue
            assert "name" in manifest
            items.append(manifest)
        PkgInstallerMixin._INSTALLED_CACHE[self.package_dir] = items
        return items

    def check_pkg_structure(self, pkg_dir):
        if self.manifest_exists(pkg_dir):
            return pkg_dir

        for root, _, _ in os.walk(pkg_dir):
            if self.manifest_exists(root):
                return root

        raise exception.MissingPackageManifest(", ".join(self.manifest_names))

    def _install_from_piorepo(self, name, requirements):
        pkg_dir = None
        pkgdata = None
        versions = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            try:
                pkg_dir = self._install_from_url(name, pkgdata['url'],
                                                 requirements,
                                                 pkgdata.get("sha1"))
                break
            except Exception as e:  # pylint: disable=broad-except
                click.secho("Warning! Package Mirror: %s" % e, fg="yellow")
                click.secho("Looking for other mirror...", fg="yellow")

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
                    util.rmtree_(tmp_dir)
                    shutil.copytree(url, tmp_dir)
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

            pkg_dir = self.check_pkg_structure(tmp_dir)
            pkg_dir = self._install_from_tmp_dir(pkg_dir, requirements)
        finally:
            if isdir(tmp_dir):
                util.rmtree_(tmp_dir)
        return pkg_dir

    def _install_from_tmp_dir(self, tmp_dir, requirements=None):
        tmp_manifest_path = self.get_manifest_path(tmp_dir)
        tmp_manifest = self.load_manifest(tmp_manifest_path)
        assert set(["name", "version"]) <= set(tmp_manifest.keys())

        name = self.generate_install_dirname(tmp_manifest)
        pkg_dir = join(self.package_dir, name)

        # package should satisfy requirements
        if requirements:
            mismatch_error = (
                "Package version %s doesn't satisfy requirements %s" % (
                    tmp_manifest['version'], requirements))
            try:
                reqspec = semantic_version.Spec(requirements)
                tmp_version = semantic_version.Version(
                    tmp_manifest['version'], partial=True)
                assert tmp_version in reqspec, mismatch_error
            except ValueError:
                assert tmp_manifest['version'] == requirements, mismatch_error

        if self.manifest_exists(pkg_dir):
            cur_manifest_path = self.get_manifest_path(pkg_dir)
            cur_manifest = self.load_manifest(cur_manifest_path)

            if tmp_manifest_path.endswith(self.VCS_MANIFEST_NAME):
                if cur_manifest.get("url") != tmp_manifest['url']:
                    pkg_dir = join(self.package_dir, "%s@vcs-%s" % (
                        name, hashlib.md5(tmp_manifest['url']).hexdigest()))
            else:
                try:
                    tmp_version = semantic_version.Version(
                        tmp_manifest['version'], partial=True)
                    cur_version = semantic_version.Version(
                        cur_manifest['version'], partial=True)

                    # if current package version < new package, backup it
                    if tmp_version > cur_version:
                        os.rename(pkg_dir,
                                  join(self.package_dir, "%s@%s" %
                                       (name, cur_manifest['version'])))
                    elif tmp_version < cur_version:
                        pkg_dir = join(self.package_dir, "%s@%s" %
                                       (name, tmp_manifest['version']))
                except ValueError:
                    pkg_dir = join(self.package_dir,
                                   "%s@%s" % (name, tmp_manifest['version']))

        # remove previous/not-satisfied package
        if isdir(pkg_dir):
            util.rmtree_(pkg_dir)
        os.rename(tmp_dir, pkg_dir)
        assert isdir(pkg_dir)
        return pkg_dir


class BasePkgManager(PkgRepoMixin, PkgInstallerMixin):

    def __init__(self, package_dir, repositories=None):
        self.repositories = repositories
        self.package_dir = package_dir
        if not isdir(self.package_dir):
            os.makedirs(self.package_dir)
        assert isdir(self.package_dir)

    @property
    def manifest_names(self):
        raise NotImplementedError()

    def print_message(self, message, nl=True):
        click.echo("%s: %s" % (self.__class__.__name__, message), nl=nl)

    @staticmethod
    def parse_pkg_name(  # pylint: disable=too-many-branches
            text, requirements=None):
        text = str(text)
        url_marker = "://"
        if not any([
                requirements, "@" not in text, text.startswith("git@"),
                url_marker in text
        ]):
            text, requirements = text.rsplit("@", 1)
        if text.isdigit():
            text = "id=" + text

        name, url = (None, text)
        if "=" in text and not text.startswith("id="):
            name, url = text.split("=", 1)

        git_conditions = [
            # Handle GitHub URL (https://github.com/user/package)
            url.startswith("https://github.com/") and not url.endswith(
                (".zip", ".tar.gz")),
            url.startswith("http") and
            (url.split("#", 1)[0] if "#" in url else url).endswith(".git")
        ]

        if any(git_conditions):
            url = "git+" + url
        # Handle Developer Mbed URL
        # (https://developer.mbed.org/users/user/code/package/)
        elif url.startswith("https://developer.mbed.org"):
            url = "hg+" + url

        # git@github.com:user/package.git
        if url.startswith("git@"):
            url_marker = "git@"

        if any([s in url for s in ("\\", "/")]) and url_marker not in url:
            if isfile(url) or isdir(url):
                url = "file://" + url
            elif url.count("/") == 1 and not url.startswith("git@"):
                url = "git+https://github.com/" + url

        # determine name
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

    def get_package(self, name, requirements=None, url=None):
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
            elif not reqspec and (requirements or url):
                conds = [
                    requirements == manifest['version'], url and
                    url in manifest.get("url", "")
                ]
                if not best or any(conds):
                    best = manifest
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

        return best

    def get_package_dir(self, name, requirements=None, url=None):
        package = self.get_package(name, requirements, url)
        return package.get("__pkg_dir") if package else None

    def outdated(self, name, requirements=None, url=None):
        """
        Has 3 different results:
        `None` - unknown package, VCS is fixed to commit
        `False` - package is up-to-date
        `String` - a found latest version
        """
        latest = None
        package_dir = self.get_package_dir(name, requirements, url)
        if not package_dir or ("@" in package_dir and
                               "@vcs-" not in package_dir):
            return None
        is_vcs_pkg = False
        manifest_path = self.get_vcs_manifest_path(package_dir)
        if manifest_path:
            is_vcs_pkg = True
            manifest = self.load_manifest(manifest_path)
        else:
            manifest = self.load_manifest(package_dir)
        if is_vcs_pkg:
            vcs = VCSClientFactory.newClient(
                package_dir, manifest['url'], silent=True)
            if not vcs.can_be_updated:
                return None
            latest = vcs.get_latest_revision()
        else:
            try:
                latest = self.get_latest_repo_version(
                    name, requirements, silent=True)
            except (exception.PlatformioException, ValueError):
                return None
        if not latest:
            return None
        up_to_date = False
        try:
            up_to_date = (semantic_version.Version.coerce(manifest['version'])
                          >= semantic_version.Version.coerce(latest))
        except ValueError:
            up_to_date = latest == manifest['version']
        return False if up_to_date else latest

    def install(self,
                name,
                requirements=None,
                silent=False,
                trigger_event=True,
                interactive=False):  # pylint: disable=unused-argument
        name, requirements, url = self.parse_pkg_name(name, requirements)
        package_dir = self.get_package_dir(name, requirements, url)

        if not package_dir or not silent:
            msg = "Installing " + click.style(name, fg="cyan")
            if requirements:
                msg += " @ " + requirements
            self.print_message(msg)
        if package_dir:
            if not silent:
                click.secho(
                    "{name} @ {version} is already installed".format(
                        **self.load_manifest(package_dir)),
                    fg="yellow")
            return package_dir

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
        package_dir = self.get_package_dir(name, requirements, url)
        if not package_dir:
            click.secho(
                "%s @ %s is not installed" % (name, requirements or "*"),
                fg="yellow")
            return

        manifest = self.load_manifest(package_dir)
        click.echo(
            "Uninstalling %s @ %s: \t" % (click.style(
                manifest['name'], fg="cyan"), manifest['version']),
            nl=False)

        if isdir(package_dir):
            if islink(package_dir):
                os.unlink(package_dir)
            else:
                util.rmtree_(package_dir)
            self.reset_cache()

        # unfix package with the same name
        package_dir = self.get_package_dir(manifest['name'])
        if package_dir and "@" in package_dir:
            os.rename(package_dir,
                      join(self.package_dir,
                           self.generate_install_dirname(manifest)))
            self.reset_cache()

        click.echo("[%s]" % click.style("OK", fg="green"))

        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Uninstall",
                label=manifest['name'])
        return True

    def update(  # pylint: disable=too-many-return-statements
            self,
            name,
            requirements=None,
            only_check=False):
        name, requirements, url = self.parse_pkg_name(name, requirements)
        package_dir = self.get_package_dir(name, requirements, url)
        if not package_dir:
            click.secho(
                "%s @ %s is not installed" % (name, requirements or "*"),
                fg="yellow")
            return

        is_vcs_pkg = False
        if self.get_vcs_manifest_path(package_dir):
            is_vcs_pkg = True
            manifest_path = self.get_vcs_manifest_path(package_dir)
        else:
            manifest_path = self.get_manifest_path(package_dir)

        manifest = self.load_manifest(manifest_path)
        click.echo(
            "{} {:<40} @ {:<15}".format(
                "Checking" if only_check else "Updating",
                click.style(manifest['name'], fg="cyan"), manifest['version']),
            nl=False)
        if not util.internet_on():
            click.echo("[%s]" % (click.style("Off-line", fg="yellow")))
            return
        latest = self.outdated(name, requirements, url)
        if latest:
            click.echo("[%s]" % (click.style(latest, fg="red")))
        elif latest is False:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
        else:
            click.echo("[%s]" % (click.style("Skip", fg="yellow")))

        if only_check or latest is False or (not is_vcs_pkg and not latest):
            return

        if is_vcs_pkg:
            vcs = VCSClientFactory.newClient(package_dir, manifest['url'])
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
            self.uninstall(name, manifest['version'], trigger_event=False)
            self.install(name, latest, trigger_event=False)

        self.reset_cache()
        telemetry.on_event(
            category=self.__class__.__name__,
            action="Update",
            label=manifest['name'])
        return True


class PackageManager(BasePkgManager):

    FILE_CACHE_VALID = None  # disable package caching

    @property
    def manifest_names(self):
        return ["package.json"]

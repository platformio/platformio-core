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

import codecs
import hashlib
import json
import os
import re
import shutil
from os.path import basename, getsize, isdir, isfile, islink, join
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

    SRC_MANIFEST_NAME = ".piopkgmanager.json"

    FILE_CACHE_VALID = "1m"  # 1 month
    FILE_CACHE_MAX_SIZE = 1024 * 1024

    MEMORY_CACHE = {}

    @staticmethod
    def cache_get(key, default=None):
        return PkgInstallerMixin.MEMORY_CACHE.get(key, default)

    @staticmethod
    def cache_set(key, value):
        PkgInstallerMixin.MEMORY_CACHE[key] = value

    @staticmethod
    def cache_reset():
        PkgInstallerMixin.MEMORY_CACHE = {}

    def read_dirs(self, src_dir):
        cache_key = "read_dirs-%s" % src_dir
        result = self.cache_get(cache_key)
        if result:
            return result
        result = [
            join(src_dir, name) for name in sorted(os.listdir(src_dir))
            if isdir(join(src_dir, name))
        ]
        self.cache_set(cache_key, result)
        return result

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
    def get_install_dirname(manifest):
        name = re.sub(r"[^\da-z\_\-\. ]", "_", manifest['name'], flags=re.I)
        if "id" in manifest:
            name += "_ID%d" % manifest['id']
        return name

    def get_src_manifest_path(self, pkg_dir):
        if not isdir(pkg_dir):
            return None
        for item in os.listdir(pkg_dir):
            if not isdir(join(pkg_dir, item)):
                continue
            if isfile(join(pkg_dir, item, self.SRC_MANIFEST_NAME)):
                return join(pkg_dir, item, self.SRC_MANIFEST_NAME)
        return None

    def get_manifest_path(self, pkg_dir):
        if not isdir(pkg_dir):
            return None
        for name in self.manifest_names:
            manifest_path = join(pkg_dir, name)
            if isfile(manifest_path):
                return manifest_path
        return None

    def manifest_exists(self, pkg_dir):
        return self.get_manifest_path(pkg_dir) or \
            self.get_src_manifest_path(pkg_dir)

    def load_manifest(self, pkg_dir):
        cache_key = "load_manifest-%s" % pkg_dir
        result = self.cache_get(cache_key)
        if result:
            return result

        manifest = {}
        src_manifest = None
        manifest_path = self.get_manifest_path(pkg_dir)
        src_manifest_path = self.get_src_manifest_path(pkg_dir)
        if src_manifest_path:
            src_manifest = util.load_json(src_manifest_path)

        if not manifest_path and not src_manifest_path:
            return None

        if manifest_path and manifest_path.endswith(".json"):
            manifest = util.load_json(manifest_path)
        elif manifest_path and manifest_path.endswith(".properties"):
            with codecs.open(manifest_path, encoding="utf-8") as fp:
                for line in fp.readlines():
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    manifest[key.strip()] = value.strip()

        if src_manifest:
            if "name" not in manifest:
                manifest['name'] = src_manifest['name']
            if "version" in src_manifest:
                manifest['version'] = src_manifest['version']
            manifest['__src_url'] = src_manifest['url']

        if "name" not in manifest:
            manifest['name'] = basename(pkg_dir)
        if "version" not in manifest:
            manifest['version'] = "0.0.0"

        manifest['__pkg_dir'] = pkg_dir
        self.cache_set(cache_key, manifest)
        return manifest

    def get_installed(self):
        items = []
        for pkg_dir in self.read_dirs(self.package_dir):
            manifest = self.load_manifest(pkg_dir)
            if not manifest:
                continue
            assert "name" in manifest
            items.append(manifest)
        return items

    def get_package(self, name, requirements=None, url=None):
        pkg_id = int(name[3:]) if name.startswith("id=") else 0
        best = None
        for manifest in self.get_installed():
            if url:
                if manifest.get("__src_url") != url:
                    continue
            elif pkg_id and manifest.get("id") != pkg_id:
                continue
            elif not pkg_id and manifest['name'] != name:
                continue

            # strict version or VCS HASH
            if requirements and requirements == manifest['version']:
                return manifest

            try:
                if requirements and not semantic_version.Spec(
                        requirements).match(
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
        manifest = self.get_package(name, requirements, url)
        return manifest.get("__pkg_dir") if manifest and isdir(
            manifest.get("__pkg_dir")) else None

    def find_pkg_root(self, src_dir):
        if self.manifest_exists(src_dir):
            return src_dir
        for root, _, _ in os.walk(src_dir):
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

    def _install_from_url(self,
                          name,
                          url,
                          requirements=None,
                          sha1=None,
                          track=False):
        tmp_dir = mkdtemp("-package", "_tmp_installing-", self.package_dir)
        src_manifest_dir = None
        src_manifest = {"name": name, "url": url, "requirements": requirements}

        try:
            if url.startswith("file://"):
                _url = url[7:]
                if isfile(_url):
                    self.unpack(_url, tmp_dir)
                else:
                    util.rmtree_(tmp_dir)
                    shutil.copytree(_url, tmp_dir)
            elif url.startswith(("http://", "https://")):
                dlpath = self.download(url, tmp_dir, sha1)
                assert isfile(dlpath)
                self.unpack(dlpath, tmp_dir)
                os.remove(dlpath)
            else:
                vcs = VCSClientFactory.newClient(tmp_dir, url)
                assert vcs.export()
                src_manifest_dir = vcs.storage_dir
                src_manifest['version'] = vcs.get_current_revision()

            _tmp_dir = tmp_dir
            if not src_manifest_dir:
                _tmp_dir = self.find_pkg_root(tmp_dir)
                src_manifest_dir = join(_tmp_dir, ".pio")

            # write source data to a special manifest
            if track:
                self._update_src_manifest(src_manifest, src_manifest_dir)

            return self._install_from_tmp_dir(_tmp_dir, requirements)
        finally:
            if isdir(tmp_dir):
                util.rmtree_(tmp_dir)
        return

    def _update_src_manifest(self, data, src_dir):
        if not isdir(src_dir):
            os.makedirs(src_dir)
        src_manifest_path = join(src_dir, self.SRC_MANIFEST_NAME)
        _data = {}
        if isfile(src_manifest_path):
            _data = util.load_json(src_manifest_path)
        _data.update(data)
        with open(src_manifest_path, "w") as fp:
            json.dump(_data, fp)

    def _install_from_tmp_dir(  # pylint: disable=too-many-branches
            self, tmp_dir, requirements=None):
        tmp_manifest = self.load_manifest(tmp_dir)
        assert set(["name", "version"]) <= set(tmp_manifest.keys())

        pkg_dirname = self.get_install_dirname(tmp_manifest)
        pkg_dir = join(self.package_dir, pkg_dirname)
        cur_manifest = self.load_manifest(pkg_dir)

        tmp_semver = None
        cur_semver = None
        try:
            tmp_semver = semantic_version.Version(
                tmp_manifest['version'], partial=True)
            if cur_manifest:
                cur_semver = semantic_version.Version(
                    cur_manifest['version'], partial=True)
        except ValueError:
            pass

        # package should satisfy requirements
        if requirements:
            mismatch_error = (
                "Package version %s doesn't satisfy requirements %s" %
                (tmp_manifest['version'], requirements))
            try:
                assert tmp_semver and tmp_semver in semantic_version.Spec(
                    requirements), mismatch_error
            except (AssertionError, ValueError):
                assert tmp_manifest['version'] == requirements, mismatch_error

        # check if package already exists
        if cur_manifest:
            # 0-overwrite, 1-rename, 2-fix to a version
            action = 0
            if "__src_url" in cur_manifest:
                if cur_manifest['__src_url'] != tmp_manifest.get("__src_url"):
                    action = 1
            elif "__src_url" in tmp_manifest:
                action = 2
            else:
                if tmp_semver and (not cur_semver or tmp_semver > cur_semver):
                    action = 1
                elif tmp_semver and cur_semver and tmp_semver != cur_semver:
                    action = 2

            # rename
            if action == 1:
                target_dirname = "%s@%s" % (pkg_dirname,
                                            cur_manifest['version'])
                if "__src_url" in cur_manifest:
                    target_dirname = "%s@src-%s" % (
                        pkg_dirname,
                        hashlib.md5(cur_manifest['__src_url']).hexdigest())
                os.rename(pkg_dir, join(self.package_dir, target_dirname))
            # fix to a version
            elif action == 2:
                target_dirname = "%s@%s" % (pkg_dirname,
                                            tmp_manifest['version'])
                if "__src_url" in tmp_manifest:
                    target_dirname = "%s@src-%s" % (
                        pkg_dirname,
                        hashlib.md5(tmp_manifest['__src_url']).hexdigest())
                pkg_dir = join(self.package_dir, target_dirname)

        # remove previous/not-satisfied package
        if isdir(pkg_dir):
            util.rmtree_(pkg_dir)
        os.rename(tmp_dir, pkg_dir)
        assert isdir(pkg_dir)
        self.cache_reset()
        return pkg_dir


class BasePkgManager(PkgRepoMixin, PkgInstallerMixin):

    # Handle circle dependencies
    INSTALL_HISTORY = None

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
    def parse_pkg_input(  # pylint: disable=too-many-branches
            text, requirements=None):
        text = str(text)
        # git@github.com:user/package.git
        url_marker = text[:4]
        if url_marker not in ("git@", "git+") or ":" not in text:
            url_marker = "://"

        req_conditions = [
            not requirements,
            "@" in text,
            not url_marker.startswith("git")
        ]  # yapf: disable
        if all(req_conditions):
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
        if url.startswith("https://developer.mbed.org"):
            url = "hg+" + url

        if any([s in url for s in ("\\", "/")]) and url_marker not in url:
            if isfile(url) or isdir(url):
                url = "file://" + url
            elif url.count("/") == 1 and "git" not in url_marker:
                url = "git+https://github.com/" + url

        # determine name
        if url_marker in url and not name:
            _url = url.split("#", 1)[0] if "#" in url else url
            if _url.endswith(("\\", "/")):
                _url = _url[:-1]
            name = basename(_url)
            if "." in name and not name.startswith("."):
                name = name.rsplit(".", 1)[0]

        if url_marker not in url:
            url = None
        return (name or text, requirements, url)

    def outdated(self, pkg_dir, requirements=None):
        """
        Has 3 different results:
        `None` - unknown package, VCS is fixed to commit
        `False` - package is up-to-date
        `String` - a found latest version
        """
        assert isdir(pkg_dir)
        latest = None
        manifest = self.load_manifest(pkg_dir)
        # skip a fixed package to a specific version
        if "@" in pkg_dir and "__src_url" not in manifest:
            return None

        if "__src_url" in manifest:
            try:
                vcs = VCSClientFactory.newClient(
                    pkg_dir, manifest['__src_url'], silent=True)
            except (AttributeError, exception.PlatformioException):
                return None
            if not vcs.can_be_updated:
                return None
            latest = vcs.get_latest_revision()
        else:
            try:
                latest = self.get_latest_repo_version(
                    "id=%d" % manifest['id']
                    if "id" in manifest else manifest['name'],
                    requirements,
                    silent=True)
            except (exception.PlatformioException, ValueError):
                return None

        if not latest:
            return None

        up_to_date = False
        try:
            assert "__src_url" not in manifest
            up_to_date = (semantic_version.Version.coerce(manifest['version'])
                          >= semantic_version.Version.coerce(latest))
        except (AssertionError, ValueError):
            up_to_date = latest == manifest['version']

        return False if up_to_date else latest

    def install(self,
                name,
                requirements=None,
                silent=False,
                trigger_event=True):

        # avoid circle dependencies
        if not self.INSTALL_HISTORY:
            self.INSTALL_HISTORY = []
        history_key = "%s-%s" % (name, requirements) if requirements else name
        if history_key in self.INSTALL_HISTORY:
            return
        self.INSTALL_HISTORY.append(history_key)

        name, requirements, url = self.parse_pkg_input(name, requirements)
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
            pkg_dir = self._install_from_url(
                name, url, requirements, track=True)
        else:
            pkg_dir = self._install_from_piorepo(name, requirements)
        if not pkg_dir or not self.manifest_exists(pkg_dir):
            raise exception.PackageInstallError(name, requirements or "*",
                                                util.get_systype())

        manifest = self.load_manifest(pkg_dir)
        assert manifest

        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Install",
                label=manifest['name'])

        if not silent:
            click.secho(
                "{name} @ {version} has been successfully installed!".format(
                    **manifest),
                fg="green")

        return pkg_dir

    def uninstall(self, package, requirements=None, trigger_event=True):
        if isdir(package):
            pkg_dir = package
        else:
            name, requirements, url = self.parse_pkg_input(
                package, requirements)
            pkg_dir = self.get_package_dir(name, requirements, url)

        if not pkg_dir:
            raise exception.UnknownPackage("%s @ %s" % (package,
                                                        requirements or "*"))

        manifest = self.load_manifest(pkg_dir)
        click.echo(
            "Uninstalling %s @ %s: \t" %
            (click.style(manifest['name'], fg="cyan"), manifest['version']),
            nl=False)

        if islink(pkg_dir):
            os.unlink(pkg_dir)
        else:
            util.rmtree_(pkg_dir)
        self.cache_reset()

        # unfix package with the same name
        pkg_dir = self.get_package_dir(manifest['name'])
        if pkg_dir and "@" in pkg_dir:
            os.rename(pkg_dir,
                      join(self.package_dir,
                           self.get_install_dirname(manifest)))
            self.cache_reset()

        click.echo("[%s]" % click.style("OK", fg="green"))

        if trigger_event:
            telemetry.on_event(
                category=self.__class__.__name__,
                action="Uninstall",
                label=manifest['name'])
        return True

    def update(  # pylint: disable=too-many-return-statements
            self,
            package,
            requirements=None,
            only_check=False):
        if isdir(package):
            pkg_dir = package
        else:
            pkg_dir = self.get_package_dir(*self.parse_pkg_input(package))

        if not pkg_dir:
            raise exception.UnknownPackage("%s @ %s" % (package,
                                                        requirements or "*"))

        manifest = self.load_manifest(pkg_dir)
        name = manifest['name']

        click.echo(
            "{} {:<40} @ {:<15}".format(
                "Checking" if only_check else "Updating",
                click.style(manifest['name'], fg="cyan"), manifest['version']),
            nl=False)
        if not util.internet_on():
            click.echo("[%s]" % (click.style("Off-line", fg="yellow")))
            return

        latest = self.outdated(pkg_dir, requirements)
        if latest:
            click.echo("[%s]" % (click.style(latest, fg="red")))
        elif latest is False:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
        else:
            click.echo("[%s]" % (click.style("Skip", fg="yellow")))

        if only_check or not latest:
            return

        if "__src_url" in manifest:
            vcs = VCSClientFactory.newClient(pkg_dir, manifest['__src_url'])
            assert vcs.update()
            self._update_src_manifest(
                dict(version=vcs.get_current_revision()), vcs.storage_dir)
        else:
            self.uninstall(pkg_dir, trigger_event=False)
            self.install(name, latest, trigger_event=False)

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

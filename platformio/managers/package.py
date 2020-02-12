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
import json
import os
import re
import shutil
from os.path import basename, getsize, isdir, isfile, islink, join, realpath
from tempfile import mkdtemp

import click
import requests
import semantic_version

from platformio import __version__, app, exception, fs, util
from platformio.compat import hashlib_encode_data
from platformio.downloader import FileDownloader
from platformio.lockfile import LockFile
from platformio.package.exception import ManifestException
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.unpacker import FileUnpacker
from platformio.vcsclient import VCSClientFactory

# pylint: disable=too-many-arguments, too-many-return-statements


class PackageRepoIterator(object):
    def __init__(self, package, repositories):
        assert isinstance(repositories, list)
        self.package = package
        self.repositories = iter(repositories)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    @staticmethod
    @util.memoized(expire="60s")
    def load_manifest(url):
        r = None
        try:
            r = requests.get(url, headers=util.get_request_defheaders())
            r.raise_for_status()
            return r.json()
        except:  # pylint: disable=bare-except
            pass
        finally:
            if r:
                r.close()
        return None

    def next(self):
        repo = next(self.repositories)
        manifest = repo if isinstance(repo, dict) else self.load_manifest(repo)
        if manifest and self.package in manifest:
            return manifest[self.package]
        return next(self)


class PkgRepoMixin(object):

    PIO_VERSION = semantic_version.Version(util.pepver_to_semver(__version__))

    @staticmethod
    def is_system_compatible(valid_systems):
        if not valid_systems or "*" in valid_systems:
            return True
        if not isinstance(valid_systems, list):
            valid_systems = list([valid_systems])
        return util.get_systype() in valid_systems

    def max_satisfying_repo_version(self, versions, requirements=None):
        item = None
        reqspec = None
        try:
            reqspec = (
                semantic_version.SimpleSpec(requirements) if requirements else None
            )
        except ValueError:
            pass

        for v in versions:
            if not self.is_system_compatible(v.get("system")):
                continue
            # if "platformio" in v.get("engines", {}):
            #     if PkgRepoMixin.PIO_VERSION not in requirements.SimpleSpec(
            #             v['engines']['platformio']):
            #         continue
            specver = semantic_version.Version(v["version"])
            if reqspec and specver not in reqspec:
                continue
            if not item or semantic_version.Version(item["version"]) < specver:
                item = v
        return item

    def get_latest_repo_version(  # pylint: disable=unused-argument
        self, name, requirements, silent=False
    ):
        version = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            if (
                not version
                or semantic_version.compare(pkgdata["version"], version) == 1
            ):
                version = pkgdata["version"]
        return version

    def get_all_repo_versions(self, name):
        result = []
        for versions in PackageRepoIterator(name, self.repositories):
            result.extend([semantic_version.Version(v["version"]) for v in versions])
        return [str(v) for v in sorted(set(result))]


class PkgInstallerMixin(object):

    SRC_MANIFEST_NAME = ".piopkgmanager.json"
    TMP_FOLDER_PREFIX = "_tmp_installing-"

    FILE_CACHE_VALID = None  # for example, 1 week = "7d"
    FILE_CACHE_MAX_SIZE = 1024 * 1024 * 50  # 50 Mb

    MEMORY_CACHE = {}  # cache for package manifests and read dirs

    def cache_get(self, key, default=None):
        return self.MEMORY_CACHE.get(key, default)

    def cache_set(self, key, value):
        self.MEMORY_CACHE[key] = value

    def cache_reset(self):
        self.MEMORY_CACHE.clear()

    def read_dirs(self, src_dir):
        cache_key = "read_dirs-%s" % src_dir
        result = self.cache_get(cache_key)
        if result:
            return result
        result = [
            join(src_dir, name)
            for name in sorted(os.listdir(src_dir))
            if isdir(join(src_dir, name))
        ]
        self.cache_set(cache_key, result)
        return result

    def download(self, url, dest_dir, sha1=None):
        cache_key_fname = app.ContentCache.key_from_args(url, "fname")
        cache_key_data = app.ContentCache.key_from_args(url, "data")
        if self.FILE_CACHE_VALID:
            with app.ContentCache() as cc:
                fname = str(cc.get(cache_key_fname))
                cache_path = cc.get_cache_path(cache_key_data)
                if fname and isfile(cache_path):
                    dst_path = join(dest_dir, fname)
                    shutil.copy(cache_path, dst_path)
                    click.echo("Using cache: %s" % cache_path)
                    return dst_path

        with_progress = not app.is_disabled_progressbar()
        try:
            fd = FileDownloader(url, dest_dir)
            fd.start(with_progress=with_progress)
        except IOError as e:
            raise_error = not with_progress
            if with_progress:
                try:
                    fd = FileDownloader(url, dest_dir)
                    fd.start(with_progress=False)
                except IOError:
                    raise_error = True
            if raise_error:
                click.secho(
                    "Error: Please read http://bit.ly/package-manager-ioerror",
                    fg="red",
                    err=True,
                )
                raise e

        if sha1:
            fd.verify(sha1)
        dst_path = fd.get_filepath()
        if (
            not self.FILE_CACHE_VALID
            or getsize(dst_path) > PkgInstallerMixin.FILE_CACHE_MAX_SIZE
        ):
            return dst_path

        with app.ContentCache() as cc:
            cc.set(cache_key_fname, basename(dst_path), self.FILE_CACHE_VALID)
            cc.set(cache_key_data, "DUMMY", self.FILE_CACHE_VALID)
            shutil.copy(dst_path, cc.get_cache_path(cache_key_data))
        return dst_path

    @staticmethod
    def unpack(source_path, dest_dir):
        with_progress = not app.is_disabled_progressbar()
        try:
            with FileUnpacker(source_path) as fu:
                return fu.unpack(dest_dir, with_progress=with_progress)
        except IOError as e:
            if not with_progress:
                raise e
            with FileUnpacker(source_path) as fu:
                return fu.unpack(dest_dir, with_progress=False)

    @staticmethod
    def parse_semver_version(value, raise_exception=False):
        try:
            try:
                return semantic_version.Version(value)
            except ValueError:
                if "." not in str(value) and not str(value).isdigit():
                    raise ValueError("Invalid SemVer version %s" % value)
                return semantic_version.Version.coerce(value)
        except ValueError as e:
            if raise_exception:
                raise e
        return None

    @staticmethod
    def parse_pkg_uri(text, requirements=None):  # pylint: disable=too-many-branches
        text = str(text)
        name, url = None, None

        # Parse requirements
        req_conditions = [
            "@" in text,
            not requirements,
            ":" not in text or text.rfind("/") < text.rfind("@"),
        ]
        if all(req_conditions):
            text, requirements = text.rsplit("@", 1)

        # Handle PIO Library Registry ID
        if text.isdigit():
            text = "id=" + text
        # Parse custom name
        elif "=" in text and not text.startswith("id="):
            name, text = text.split("=", 1)

        # Parse URL
        # if valid URL with scheme vcs+protocol://
        if "+" in text and text.find("+") < text.find("://"):
            url = text
        elif "/" in text or "\\" in text:
            git_conditions = [
                # Handle GitHub URL (https://github.com/user/package)
                text.startswith("https://github.com/")
                and not text.endswith((".zip", ".tar.gz")),
                (text.split("#", 1)[0] if "#" in text else text).endswith(".git"),
            ]
            hg_conditions = [
                # Handle Developer Mbed URL
                # (https://developer.mbed.org/users/user/code/package/)
                # (https://os.mbed.com/users/user/code/package/)
                text.startswith("https://developer.mbed.org"),
                text.startswith("https://os.mbed.com"),
            ]
            if any(git_conditions):
                url = "git+" + text
            elif any(hg_conditions):
                url = "hg+" + text
            elif "://" not in text and (isfile(text) or isdir(text)):
                url = "file://" + text
            elif "://" in text:
                url = text
            # Handle short version of GitHub URL
            elif text.count("/") == 1:
                url = "git+https://github.com/" + text

        # Parse name from URL
        if url and not name:
            _url = url.split("#", 1)[0] if "#" in url else url
            if _url.endswith(("\\", "/")):
                _url = _url[:-1]
            name = basename(_url)
            if "." in name and not name.startswith("."):
                name = name.rsplit(".", 1)[0]

        return (name or text, requirements, url)

    @staticmethod
    def get_install_dirname(manifest):
        name = re.sub(r"[^\da-z\_\-\. ]", "_", manifest["name"], flags=re.I)
        if "id" in manifest:
            name += "_ID%d" % manifest["id"]
        return str(name)

    @classmethod
    def get_src_manifest_path(cls, pkg_dir):
        if not isdir(pkg_dir):
            return None
        for item in os.listdir(pkg_dir):
            if not isdir(join(pkg_dir, item)):
                continue
            if isfile(join(pkg_dir, item, cls.SRC_MANIFEST_NAME)):
                return join(pkg_dir, item, cls.SRC_MANIFEST_NAME)
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
        return self.get_manifest_path(pkg_dir) or self.get_src_manifest_path(pkg_dir)

    def load_manifest(self, pkg_dir):  # pylint: disable=too-many-branches
        cache_key = "load_manifest-%s" % pkg_dir
        result = self.cache_get(cache_key)
        if result:
            return result

        manifest = {}
        src_manifest = None
        manifest_path = self.get_manifest_path(pkg_dir)
        src_manifest_path = self.get_src_manifest_path(pkg_dir)
        if src_manifest_path:
            src_manifest = fs.load_json(src_manifest_path)

        if not manifest_path and not src_manifest_path:
            return None

        try:
            manifest = ManifestParserFactory.new_from_file(manifest_path).as_dict()
        except ManifestException:
            pass

        if src_manifest:
            if "version" in src_manifest:
                manifest["version"] = src_manifest["version"]
            manifest["__src_url"] = src_manifest["url"]
            # handle a custom package name
            autogen_name = self.parse_pkg_uri(manifest["__src_url"])[0]
            if "name" not in manifest or autogen_name != src_manifest["name"]:
                manifest["name"] = src_manifest["name"]

        if "name" not in manifest:
            manifest["name"] = basename(pkg_dir)
        if "version" not in manifest:
            manifest["version"] = "0.0.0"

        manifest["__pkg_dir"] = realpath(pkg_dir)
        self.cache_set(cache_key, manifest)
        return manifest

    def get_installed(self):
        items = []
        for pkg_dir in self.read_dirs(self.package_dir):
            if self.TMP_FOLDER_PREFIX in pkg_dir:
                continue
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
            elif not pkg_id and manifest["name"] != name:
                continue
            elif not PkgRepoMixin.is_system_compatible(manifest.get("system")):
                continue

            # strict version or VCS HASH
            if requirements and requirements == manifest["version"]:
                return manifest

            try:
                if requirements and not semantic_version.SimpleSpec(requirements).match(
                    self.parse_semver_version(manifest["version"], raise_exception=True)
                ):
                    continue
                if not best or (
                    self.parse_semver_version(manifest["version"], raise_exception=True)
                    > self.parse_semver_version(best["version"], raise_exception=True)
                ):
                    best = manifest
            except ValueError:
                pass

        return best

    def get_package_dir(self, name, requirements=None, url=None):
        manifest = self.get_package(name, requirements, url)
        return (
            manifest.get("__pkg_dir")
            if manifest and isdir(manifest.get("__pkg_dir"))
            else None
        )

    def get_package_by_dir(self, pkg_dir):
        for manifest in self.get_installed():
            if manifest["__pkg_dir"] == realpath(pkg_dir):
                return manifest
        return None

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
        last_exc = None
        for versions in PackageRepoIterator(name, self.repositories):
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue
            try:
                pkg_dir = self._install_from_url(
                    name, pkgdata["url"], requirements, pkgdata.get("sha1")
                )
                break
            except Exception as e:  # pylint: disable=broad-except
                last_exc = e
                click.secho("Warning! Package Mirror: %s" % e, fg="yellow")
                click.secho("Looking for another mirror...", fg="yellow")

        if versions is None:
            util.internet_on(raise_exception=True)
            raise exception.UnknownPackage(
                name + (". Error -> %s" % last_exc if last_exc else "")
            )
        if not pkgdata:
            raise exception.UndefinedPackageVersion(
                requirements or "latest", util.get_systype()
            )
        return pkg_dir

    def _install_from_url(self, name, url, requirements=None, sha1=None, track=False):
        tmp_dir = mkdtemp("-package", self.TMP_FOLDER_PREFIX, self.package_dir)
        src_manifest_dir = None
        src_manifest = {"name": name, "url": url, "requirements": requirements}

        try:
            if url.startswith("file://"):
                _url = url[7:]
                if isfile(_url):
                    self.unpack(_url, tmp_dir)
                else:
                    fs.rmtree(tmp_dir)
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
                src_manifest["version"] = vcs.get_current_revision()

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
                fs.rmtree(tmp_dir)
        return None

    def _update_src_manifest(self, data, src_dir):
        if not isdir(src_dir):
            os.makedirs(src_dir)
        src_manifest_path = join(src_dir, self.SRC_MANIFEST_NAME)
        _data = {}
        if isfile(src_manifest_path):
            _data = fs.load_json(src_manifest_path)
        _data.update(data)
        with open(src_manifest_path, "w") as fp:
            json.dump(_data, fp)

    def _install_from_tmp_dir(  # pylint: disable=too-many-branches
        self, tmp_dir, requirements=None
    ):
        tmp_manifest = self.load_manifest(tmp_dir)
        assert set(["name", "version"]) <= set(tmp_manifest)

        pkg_dirname = self.get_install_dirname(tmp_manifest)
        pkg_dir = join(self.package_dir, pkg_dirname)
        cur_manifest = self.load_manifest(pkg_dir)

        tmp_semver = self.parse_semver_version(tmp_manifest["version"])
        cur_semver = None
        if cur_manifest:
            cur_semver = self.parse_semver_version(cur_manifest["version"])

        # package should satisfy requirements
        if requirements:
            mismatch_error = "Package version %s doesn't satisfy requirements %s" % (
                tmp_manifest["version"],
                requirements,
            )
            try:
                assert tmp_semver and tmp_semver in semantic_version.SimpleSpec(
                    requirements
                ), mismatch_error
            except (AssertionError, ValueError):
                assert tmp_manifest["version"] == requirements, mismatch_error

        # check if package already exists
        if cur_manifest:
            # 0-overwrite, 1-rename, 2-fix to a version
            action = 0
            if "__src_url" in cur_manifest:
                if cur_manifest["__src_url"] != tmp_manifest.get("__src_url"):
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
                target_dirname = "%s@%s" % (pkg_dirname, cur_manifest["version"])
                if "__src_url" in cur_manifest:
                    target_dirname = "%s@src-%s" % (
                        pkg_dirname,
                        hashlib.md5(
                            hashlib_encode_data(cur_manifest["__src_url"])
                        ).hexdigest(),
                    )
                shutil.move(pkg_dir, join(self.package_dir, target_dirname))
            # fix to a version
            elif action == 2:
                target_dirname = "%s@%s" % (pkg_dirname, tmp_manifest["version"])
                if "__src_url" in tmp_manifest:
                    target_dirname = "%s@src-%s" % (
                        pkg_dirname,
                        hashlib.md5(
                            hashlib_encode_data(tmp_manifest["__src_url"])
                        ).hexdigest(),
                    )
                pkg_dir = join(self.package_dir, target_dirname)

        # remove previous/not-satisfied package
        if isdir(pkg_dir):
            fs.rmtree(pkg_dir)
        shutil.move(tmp_dir, pkg_dir)
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

    def outdated(self, pkg_dir, requirements=None):
        """
        Has 3 different results:
        `None` - unknown package, VCS is detached to commit
        `False` - package is up-to-date
        `String` - a found latest version
        """
        if not isdir(pkg_dir):
            return None
        latest = None
        manifest = self.load_manifest(pkg_dir)
        # skip detached package to a specific version
        if "@" in pkg_dir and "__src_url" not in manifest and not requirements:
            return None

        if "__src_url" in manifest:
            try:
                vcs = VCSClientFactory.newClient(
                    pkg_dir, manifest["__src_url"], silent=True
                )
            except (AttributeError, exception.PlatformioException):
                return None
            if not vcs.can_be_updated:
                return None
            latest = vcs.get_latest_revision()
        else:
            try:
                latest = self.get_latest_repo_version(
                    "id=%d" % manifest["id"] if "id" in manifest else manifest["name"],
                    requirements,
                    silent=True,
                )
            except (exception.PlatformioException, ValueError):
                return None

        if not latest:
            return None

        up_to_date = False
        try:
            assert "__src_url" not in manifest
            up_to_date = self.parse_semver_version(
                manifest["version"], raise_exception=True
            ) >= self.parse_semver_version(latest, raise_exception=True)
        except (AssertionError, ValueError):
            up_to_date = latest == manifest["version"]

        return False if up_to_date else latest

    def install(
        self, name, requirements=None, silent=False, after_update=False, force=False
    ):  # pylint: disable=unused-argument
        pkg_dir = None
        # interprocess lock
        with LockFile(self.package_dir):
            self.cache_reset()

            name, requirements, url = self.parse_pkg_uri(name, requirements)
            package_dir = self.get_package_dir(name, requirements, url)

            # avoid circle dependencies
            if not self.INSTALL_HISTORY:
                self.INSTALL_HISTORY = []
            history_key = "%s-%s-%s" % (name, requirements or "", url or "")
            if history_key in self.INSTALL_HISTORY:
                return package_dir
            self.INSTALL_HISTORY.append(history_key)

            if package_dir and force:
                self.uninstall(package_dir)
                package_dir = None

            if not package_dir or not silent:
                msg = "Installing " + click.style(name, fg="cyan")
                if requirements:
                    msg += " @ " + requirements
                self.print_message(msg)
            if package_dir:
                if not silent:
                    click.secho(
                        "{name} @ {version} is already installed".format(
                            **self.load_manifest(package_dir)
                        ),
                        fg="yellow",
                    )
                return package_dir

            if url:
                pkg_dir = self._install_from_url(name, url, requirements, track=True)
            else:
                pkg_dir = self._install_from_piorepo(name, requirements)

            if not pkg_dir or not self.manifest_exists(pkg_dir):
                raise exception.PackageInstallError(
                    name, requirements or "*", util.get_systype()
                )

            manifest = self.load_manifest(pkg_dir)
            assert manifest

            click.secho(
                "{name} @ {version} has been successfully installed!".format(
                    **manifest
                ),
                fg="green",
            )

        return pkg_dir

    def uninstall(
        self, package, requirements=None, after_update=False
    ):  # pylint: disable=unused-argument
        # interprocess lock
        with LockFile(self.package_dir):
            self.cache_reset()

            if isdir(package) and self.get_package_by_dir(package):
                pkg_dir = package
            else:
                name, requirements, url = self.parse_pkg_uri(package, requirements)
                pkg_dir = self.get_package_dir(name, requirements, url)

            if not pkg_dir:
                raise exception.UnknownPackage(
                    "%s @ %s" % (package, requirements or "*")
                )

            manifest = self.load_manifest(pkg_dir)
            click.echo(
                "Uninstalling %s @ %s: \t"
                % (click.style(manifest["name"], fg="cyan"), manifest["version"]),
                nl=False,
            )

            if islink(pkg_dir):
                os.unlink(pkg_dir)
            else:
                fs.rmtree(pkg_dir)
            self.cache_reset()

            # unfix package with the same name
            pkg_dir = self.get_package_dir(manifest["name"])
            if pkg_dir and "@" in pkg_dir:
                shutil.move(
                    pkg_dir, join(self.package_dir, self.get_install_dirname(manifest))
                )
                self.cache_reset()

            click.echo("[%s]" % click.style("OK", fg="green"))

        return True

    def update(self, package, requirements=None, only_check=False):
        self.cache_reset()
        if isdir(package) and self.get_package_by_dir(package):
            pkg_dir = package
        else:
            pkg_dir = self.get_package_dir(*self.parse_pkg_uri(package))

        if not pkg_dir:
            raise exception.UnknownPackage("%s @ %s" % (package, requirements or "*"))

        manifest = self.load_manifest(pkg_dir)
        name = manifest["name"]

        click.echo(
            "{} {:<40} @ {:<15}".format(
                "Checking" if only_check else "Updating",
                click.style(manifest["name"], fg="cyan"),
                manifest["version"],
            ),
            nl=False,
        )
        if not util.internet_on():
            click.echo("[%s]" % (click.style("Off-line", fg="yellow")))
            return None

        latest = self.outdated(pkg_dir, requirements)
        if latest:
            click.echo("[%s]" % (click.style(latest, fg="red")))
        elif latest is False:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
        else:
            click.echo("[%s]" % (click.style("Detached", fg="yellow")))

        if only_check or not latest:
            return True

        if "__src_url" in manifest:
            vcs = VCSClientFactory.newClient(pkg_dir, manifest["__src_url"])
            assert vcs.update()
            self._update_src_manifest(
                dict(version=vcs.get_current_revision()), vcs.storage_dir
            )
        else:
            self.uninstall(pkg_dir, after_update=True)
            self.install(name, latest, after_update=True)

        return True


class PackageManager(BasePkgManager):
    @property
    def manifest_names(self):
        return ["package.json"]

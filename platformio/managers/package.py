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

import os
from os.path import dirname, isdir, isfile, islink, join
from shutil import copyfile, copytree, rmtree

import click
import requests
import semantic_version

from platformio import exception, telemetry, util
from platformio.downloader import FileDownloader
from platformio.unpacker import FileUnpacker


class PackageManager(object):

    _INSTALLED_CACHE = {}

    def __init__(self, package_dir=None, repositories=None):
        self._INSTALLED_CACHE = {}
        self.repositories = repositories
        self.package_dir = package_dir or join(util.get_home_dir(), "packages")
        if not isdir(self.package_dir):
            os.makedirs(self.package_dir)
        assert isdir(self.package_dir)

    @staticmethod
    def reset_cache():
        PackageManager._INSTALLED_CACHE = {}

    @property
    def manifest_name(self):
        return "package.json"

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

    def check_structure(self, pkg_dir):
        if isfile(join(pkg_dir, self.manifest_name)):
            return True

        for root, _, files in os.walk(pkg_dir):
            if self.manifest_name not in files:
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

        if isfile(join(pkg_dir, self.manifest_name)):
            return True

        raise exception.PlatformioException(
            "Could not find '%s' manifest file in the package" %
            self.manifest_name)

    def make_pkg_dir(self, name, version):
        pkg_dir = join(self.package_dir, name)
        if isfile(join(pkg_dir, self.manifest_name)):
            manifest = util.load_json(
                join(pkg_dir, self.manifest_name))

            cmp_result = semantic_version.compare(version, manifest['version'])
            if cmp_result == 1:
                # if main package version < new package, backup it
                print pkg_dir, join(
                    self.package_dir, "%s@%s" % (name, manifest['version']))
                os.rename(pkg_dir, join(
                    self.package_dir, "%s@%s" % (name, manifest['version'])))
            elif cmp_result == -1:
                pkg_dir = join(
                    self.package_dir, "%s@%s" % (name, version))

        # remove previous/not-satisfied package
        if isdir(pkg_dir):
            rmtree(pkg_dir)
        os.makedirs(pkg_dir)
        assert isdir(pkg_dir)

        self.reset_cache()
        return pkg_dir

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

    def max_satisfying_version(self, name, requirements=None):
        best = None
        for manifest in self.get_installed():
            if manifest['name'] != name:
                continue
            elif requirements and not semantic_version.match(
                    requirements, manifest['version']):
                continue
            elif (not best or semantic_version.compare(
                    manifest['version'], best['version']) == 1):
                best = manifest
        return best

    def get_installed(self):
        if self.package_dir in PackageManager._INSTALLED_CACHE:
            return PackageManager._INSTALLED_CACHE[self.package_dir]
        items = []
        for p in sorted(os.listdir(self.package_dir)):
            manifest_path = join(self.package_dir, p, self.manifest_name)
            if not isfile(manifest_path):
                continue
            manifest = util.load_json(manifest_path)
            manifest['_manifest_path'] = manifest_path
            assert set(["name", "version"]) <= set(manifest.keys())
            items.append(manifest)
        PackageManager._INSTALLED_CACHE[self.package_dir] = items
        return items

    def is_installed(self, name, requirements=None):
        installed = self.get_installed()
        if requirements is None:
            return any([p['name'] == name for p in installed])

        for p in installed:
            if p['name'] != name:
                continue
            elif semantic_version.match(requirements, p['version']):
                return True
        return None

    def install(self, name, requirements, silent=False, trigger_event=True):
        installed = self.is_installed(name, requirements)
        if not installed or not silent:
            click.echo("Installing %s %s @ %s:" % (
                self.manifest_name.split(".")[0],
                click.style(name, fg="cyan"),
                requirements if requirements else "latest"))
        if installed:
            if not silent:
                click.secho("Already installed", fg="yellow")
            return self.max_satisfying_version(
                name, requirements).get("_manifest_path")

        manifest_path = None
        if name.startswith("file://"):
            manifest_path = self._install_from_local_dir(name[7:])
        else:
            manifest_path = self._install_from_piorepo(name, requirements)
        if not isfile(manifest_path):
            raise exception.PackageInstallError(
                name, requirements or "latest", util.get_systype())

        self.reset_cache()
        if trigger_event:
            telemetry.on_event(
                category="PackageManager", action="Install", label=name)

        return manifest_path

    def _install_from_piorepo(self, name, requirements):
        pkg_dir = None
        pkgdata = None
        versions = None
        for versions in PackageRepoIterator(name, self.repositories):
            dlpath = None
            pkgdata = self.max_satisfying_repo_version(versions, requirements)
            if not pkgdata:
                continue

            pkg_dir = self.make_pkg_dir(name, pkgdata['version'])
            try:
                dlpath = self.download(
                    pkgdata['url'], pkg_dir, pkgdata.get("sha1"))
                assert isfile(dlpath)
                self.unpack(dlpath, pkg_dir)
                self.check_structure(pkg_dir)
                break
            except Exception as e:  # pylint: disable=broad-except
                click.secho("Warning! Package Mirror: %s" % e, fg="yellow")
                click.secho("Looking for another mirror...", fg="yellow")
            finally:
                if dlpath and isfile(dlpath):
                    os.remove(dlpath)

        if versions is None:
            raise exception.UnknownPackage(name)
        elif not pkgdata:
            if "platform" in self.manifest_name:
                raise exception.UndefinedPlatformVersion(
                    name, requirements or "latest")
            else:
                raise exception.UndefinedPackageVersion(
                    name, requirements or "latest", util.get_systype())

        return join(pkg_dir, self.manifest_name)

    def _install_from_local_dir(self, local_dir):
        if not isfile(join(local_dir, self.manifest_name)):
            raise exception.InvalidLocalPackage(
                local_dir, self.manifest_name)

        manifest = util.load_json(join(local_dir, self.manifest_name))
        assert set(["name", "version"]) <= set(manifest.keys())
        pkg_dir = self.make_pkg_dir(manifest['name'], manifest['version'])
        rmtree(pkg_dir)
        copytree(local_dir, pkg_dir, symlinks=True)

        return join(pkg_dir, self.manifest_name)

    def uninstall(self, name, requirements=None, trigger_event=True):
        click.echo("Uninstalling %s %s @ %s: \t" % (
            self.manifest_name.split(".")[0],
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
            if isfile(manifest['_manifest_path']):
                pkg_dir = dirname(manifest['_manifest_path'])
                if islink(pkg_dir):
                    os.unlink(pkg_dir)
                else:
                    rmtree(pkg_dir)

        if not found:
            click.secho("Not installed", fg="yellow")
            return False
        else:
            click.echo("[%s]" % click.style("OK", fg="green"))

        self.reset_cache()
        if trigger_event:
            telemetry.on_event(
                category="PackageManager", action="Uninstall", label=name)

    def update(self, name, requirements=None):
        click.echo("Updating %s %s @ %s:" % (
            self.manifest_name.split(".")[0],
            click.style(name, fg="yellow"),
            requirements if requirements else "latest"))

        latest_version = self.get_latest_repo_version(name, requirements)
        if latest_version is None:
            click.secho("Ignored! '%s' is not listed in "
                        "Package Repository" % name, fg="yellow")
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
            category="PackageManager", action="Update", label=name)
        return True


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

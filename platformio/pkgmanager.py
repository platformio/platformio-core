# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import makedirs, remove
from os.path import isdir, join
from shutil import rmtree
from time import time

from click import echo, secho, style

from platformio.downloader import FileDownloader
from platformio.exception import (InvalidPackageVersion, NonSystemPackage,
                                  UnknownPackage)
from platformio.unpacker import FileUnpacker
from platformio.util import AppState, get_api_result, get_home_dir, get_systype


class PackageManager(object):

    DBFILE_PATH = join(get_home_dir(), "installed.json")

    def __init__(self):
        self._package_dir = join(get_home_dir(), "packages")
        if not isdir(self._package_dir):
            makedirs(self._package_dir)
        assert isdir(self._package_dir)

    @staticmethod
    def get_manifest():
        try:
            return PackageManager._cached_manifest
        except AttributeError:
            PackageManager._cached_manifest = get_api_result("/packages")
        return PackageManager._cached_manifest

    @staticmethod
    def download(url, dest_dir, sha1=None):
        fd = FileDownloader(url, dest_dir)
        fd.start()
        fd.verify(sha1)
        return fd.get_filepath()

    @staticmethod
    def unpack(pkgpath, dest_dir):
        fu = FileUnpacker(pkgpath, dest_dir)
        return fu.start()

    @staticmethod
    def get_installed():
        pkgs = {}
        with AppState() as state:
            pkgs = state.get("installed_packages", {})
        return pkgs

    @staticmethod
    def update_appstate_instpkgs(data):
        with AppState() as state:
            state['installed_packages'] = data

    def is_installed(self, name):
        return name in self.get_installed()

    def get_info(self, name, version=None):
        manifest = self.get_manifest()
        if name not in manifest:
            raise UnknownPackage(name)

        # check system platform
        systype = get_systype()
        builds = ([b for b in manifest[name] if b['system'] == "all" or systype
                   in b['system']])
        if not builds:
            raise NonSystemPackage(name, systype)

        if version:
            for b in builds:
                if b['version'] == version:
                    return b
            raise InvalidPackageVersion(name, version)
        else:
            return sorted(builds, key=lambda s: s['version'])[-1]

    def install(self, name):
        echo("Installing %s package:" % style(name, fg="cyan"))

        if self.is_installed(name):
            secho("Already installed", fg="yellow")
            return False

        info = self.get_info(name)
        pkg_dir = join(self._package_dir, name)
        if not isdir(pkg_dir):
            makedirs(pkg_dir)

        dlpath = self.download(info['url'], pkg_dir, info['sha1'])
        if self.unpack(dlpath, pkg_dir):
            self._register(name, info['version'])
        # remove archive
        remove(dlpath)

    def uninstall(self, name):
        echo("Uninstalling %s package: \t" % style(name, fg="cyan"),
             nl=False)

        if not self.is_installed(name):
            secho("Not installed", fg="yellow")
            return False

        rmtree(join(self._package_dir, name))
        self._unregister(name)
        echo("[%s]" % style("OK", fg="green"))

    def update(self, name):
        echo("Updating %s package:" % style(name, fg="yellow"))

        installed = self.get_installed()
        current_version = installed[name]['version']
        latest_version = self.get_info(name)['version']

        echo("Versions: Current=%d, Latest=%d \t " % (
            current_version, latest_version), nl=False)

        if current_version == latest_version:
            echo("[%s]" % (style("Up-to-date", fg="green")))
            return True
        else:
            echo("[%s]" % (style("Out-of-date", fg="red")))

        self.uninstall(name)
        self.install(name)

    def _register(self, name, version):
        data = self.get_installed()
        data[name] = {
            "version": version,
            "time": time()
        }
        self.update_appstate_instpkgs(data)

    def _unregister(self, name):
        data = self.get_installed()
        del data[name]
        self.update_appstate_instpkgs(data)

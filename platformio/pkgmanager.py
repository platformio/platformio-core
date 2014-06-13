# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from os import makedirs, remove
from os.path import isdir, isfile, join
from shutil import rmtree

from click import echo, secho, style
from requests import get

from platformio import __pkgmanifesturl__
from platformio.downloader import FileDownloader
from platformio.exception import (InvalidPackageVersion, NonSystemPackage,
                                  UnknownPackage)
from platformio.unpacker import FileUnpacker
from platformio.util import get_home_dir, get_system


class PackageManager(object):

    DBFILE_PATH = join(get_home_dir(), "installed.json")

    def __init__(self, platform_name):
        self._platform_name = platform_name

    @staticmethod
    def get_manifest():
        try:
            return PackageManager._cached_manifest
        except AttributeError:
            PackageManager._cached_manifest = get(__pkgmanifesturl__).json()
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
    def get_installed(platform=None):
        data = {}
        if isfile(PackageManager.DBFILE_PATH):
            with open(PackageManager.DBFILE_PATH) as fp:
                data = json.load(fp)
        return data.get(platform, None) if platform else data

    def get_platform_dir(self):
        return join(get_home_dir(), self._platform_name)

    def is_installed(self, name):
        installed = self.get_installed()
        return (self._platform_name in installed and name in
                installed[self._platform_name])

    def get_info(self, name, version=None):
        manifest = self.get_manifest()
        if name not in manifest:
            raise UnknownPackage(name)

        # check system platform
        system = get_system()
        builds = ([b for b in manifest[name] if b['system'] == "all" or system
                   in b['system']])
        if not builds:
            raise NonSystemPackage(name, system)

        if version:
            for b in builds:
                if b['version'] == version:
                    return b
            raise InvalidPackageVersion(name, version)
        else:
            return sorted(builds, key=lambda s: s['version'])[-1]

    def install(self, name, path):
        echo("Installing %s package:" % style(name, fg="cyan"))

        if self.is_installed(name):
            secho("Already installed", fg="yellow")
            return

        info = self.get_info(name)
        pkg_dir = join(self.get_platform_dir(), path)
        if not isdir(pkg_dir):
            makedirs(pkg_dir)

        dlpath = self.download(info['url'], pkg_dir, info['sha1'])
        if self.unpack(dlpath, pkg_dir):
            self._register(name, info['version'], path)
        # remove archive
        remove(dlpath)

    def uninstall(self, name, path):
        echo("Uninstalling %s package: \t" % style(name, fg="cyan"),
             nl=False)
        rmtree(join(self.get_platform_dir(), path))
        self._unregister(name)
        echo("[%s]" % style("OK", fg="green"))

    def update(self, name):
        echo("Updating %s package:" % style(name, fg="yellow"))

        installed = self.get_installed(self._platform_name)
        current_version = installed[name]['version']
        latest_version = self.get_info(name)['version']

        echo("Versions: Current=%d, Latest=%d \t " % (
            current_version, latest_version), nl=False)

        if current_version == latest_version:
            echo("[%s]" % (style("Up-to-date", fg="green")))
            return True
        else:
            echo("[%s]" % (style("Out-of-date", fg="red")))

        self.uninstall(name, installed[name]['path'])
        self.install(name, installed[name]['path'])

    def register_platform(self, name):
        data = self.get_installed()
        if name not in data:
            data[name] = {}
        self._update_db(data)
        return data

    def unregister_platform(self, name):
        data = self.get_installed()
        del data[name]
        self._update_db(data)

    def _register(self, name, version, path):
        data = self.get_installed()
        if self._platform_name not in data:
            data = self.register_platform(self._platform_name)
        data[self._platform_name][name] = {
            "version": version,
            "path": path
        }
        self._update_db(data)

    def _unregister(self, name):
        data = self.get_installed()
        del data[self._platform_name][name]
        self._update_db(data)

    def _update_db(self, data):
        with open(self.DBFILE_PATH, "w") as fp:
            json.dump(data, fp)

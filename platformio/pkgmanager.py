# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from os import makedirs, remove
from os.path import isdir, isfile, join

from requests import get

from platformio import __pkgmanifesturl__
from platformio.downloader import FileDownloader
from platformio.exception import (InvalidPackageVersion, NonSystemPackage,
                                  PackageInstalled, UnknownPackage)
from platformio.unpacker import FileUnpacker
from platformio.util import get_home_dir, get_system


class PackageManager(object):

    def __init__(self, platform_name):
        self._platform_name = platform_name
        self._platforms_dir = get_home_dir()
        self._dbfile = join(self._platforms_dir, "installed.json")

    @staticmethod
    def get_manifest():
        return get(__pkgmanifesturl__).json()

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

    def get_installed(self):
        data = {}
        if isfile(self._dbfile):
            with open(self._dbfile) as fp:
                data = json.load(fp)
        return data

    def is_installed(self, name):
        installed = self.get_installed()
        return (self._platform_name in installed and name in
                installed[self._platform_name])

    def get_info(self, name, version=None):
        if self.is_installed(name):
            raise PackageInstalled(name)

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
        info = self.get_info(name)
        pkg_dir = join(self._platforms_dir, self._platform_name, path)
        if not isdir(pkg_dir):
            makedirs(pkg_dir)

        dlpath = self.download(info['url'], pkg_dir, info['sha1'])
        if self.unpack(dlpath, pkg_dir):
            self._register(name, info['version'], path)
        # remove archive
        remove(dlpath)

    def _register(self, name, version, path):
        data = self.get_installed()
        if self._platform_name not in data:
            data[self._platform_name] = {}
        data[self._platform_name][name] = {
            "version": version,
            "path": path
        }
        with open(self._dbfile, "w") as fp:
            json.dump(data, fp)

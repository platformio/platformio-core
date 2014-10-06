# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from os import listdir, makedirs, remove
from os.path import isdir, isfile, join
from shutil import rmtree
from tempfile import gettempdir

from platformio.downloader import FileDownloader
from platformio.exception import LibAlreadyInstalledError, LibNotInstalledError
from platformio.unpacker import FileUnpacker
from platformio.util import get_api_result


class LibraryManager(object):

    CONFIG_NAME = "library.json"

    def __init__(self, lib_dir):
        self.lib_dir = lib_dir

    @staticmethod
    def download(url, dest_dir):
        fd = FileDownloader(url, dest_dir)
        fd.start()
        return fd.get_filepath()

    @staticmethod
    def unpack(pkgpath, dest_dir):
        fu = FileUnpacker(pkgpath, dest_dir)
        return fu.start()

    def get_installed(self):
        items = []
        if not isdir(self.lib_dir):
            return items
        for item in listdir(self.lib_dir):
            conf_path = join(self.lib_dir, item, self.CONFIG_NAME)
            if isfile(conf_path):
                items.append(item)
        return items

    def get_info(self, name):
        conf_path = join(self.lib_dir, name, self.CONFIG_NAME)
        if not isfile(conf_path):
            raise LibNotInstalledError(name)
        with open(conf_path, "r") as f:
            return json.load(f)

    def is_installed(self, name):
        return isfile(join(self.lib_dir, name, self.CONFIG_NAME))

    def install(self, name, version=None):
        if self.is_installed(name):
            raise LibAlreadyInstalledError()

        dlinfo = get_api_result("/lib/download/" + name, dict(version=version)
                                if version else None)
        try:
            dlpath = self.download(dlinfo['url'], gettempdir())
            _lib_dir = join(self.lib_dir, name)
            if not isdir(_lib_dir):
                makedirs(_lib_dir)
            self.unpack(dlpath, _lib_dir)
        finally:
            remove(dlpath)

        return self.is_installed(name)

    def uninstall(self, name):
        if self.is_installed(name):
            rmtree(join(self.lib_dir, name))
            return True
        else:
            raise LibNotInstalledError(name)

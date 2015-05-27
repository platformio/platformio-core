# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
import re
from os import listdir, makedirs, remove, rename
from os.path import isdir, isfile, join
from shutil import rmtree
from tempfile import gettempdir

from platformio import telemetry, util
from platformio.downloader import FileDownloader
from platformio.exception import LibAlreadyInstalledError, LibNotInstalledError
from platformio.unpacker import FileUnpacker


class LibraryManager(object):

    CONFIG_NAME = ".library.json"

    def __init__(self, lib_dir=None):
        self.lib_dir = lib_dir or util.get_lib_dir()

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
        items = {}
        if not isdir(self.lib_dir):
            return items
        for dirname in sorted(listdir(self.lib_dir)):
            conf_path = join(self.lib_dir, dirname, self.CONFIG_NAME)
            if not isfile(conf_path):
                continue
            with open(conf_path, "r") as f:
                items[dirname] = json.load(f)
        return items

    def get_latest_versions(self):
        lib_ids = [str(item['id']) for item in self.get_installed().values()]
        if not lib_ids:
            return None
        return util.get_api_result("/lib/version/" + str(",".join(lib_ids)))

    def get_outdated(self):
        outdated = []
        for id_, latest_version in (self.get_latest_versions() or {}).items():
            info = self.get_info(int(id_))
            if latest_version != info['version']:
                outdated.append(info['name'])
        return outdated

    def get_info(self, id_):
        for item in self.get_installed().values():
            if "id" in item and item['id'] == id_:
                return item
        raise LibNotInstalledError(id_)

    def is_installed(self, id_):
        try:
            return int(self.get_info(id_)['id']) == id_
        except LibNotInstalledError:
            return False

    def install(self, id_, version=None):
        if self.is_installed(id_):
            raise LibAlreadyInstalledError()

        dlinfo = util.get_api_result(
            "/lib/download/" + str(id_),
            dict(version=version) if version else None
        )
        dlpath = None
        tmplib_dir = join(self.lib_dir, str(id_))
        try:
            dlpath = self.download(dlinfo['url'], gettempdir())
            if not isdir(tmplib_dir):
                makedirs(tmplib_dir)
            self.unpack(dlpath, tmplib_dir)
        finally:
            if dlpath:
                remove(dlpath)

        info = self.get_info(id_)
        rename(tmplib_dir, join(self.lib_dir, "%s_ID%d" % (
            re.sub(r"[^\da-zA-Z]+", "_", info['name']), id_)))

        telemetry.on_event(
            category="LibraryManager", action="Install",
            label="#%d %s" % (id_, info['name'])
        )

        return True

    def uninstall(self, id_):
        for libdir, item in self.get_installed().iteritems():
            if "id" in item and item['id'] == id_:
                rmtree(join(self.lib_dir, libdir))
                telemetry.on_event(
                    category="LibraryManager", action="Uninstall",
                    label="#%d %s" % (id_, item['name'])
                )
                return True
        raise LibNotInstalledError(id_)

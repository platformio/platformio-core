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

import os
import tarfile
from binascii import crc32
from os.path import getmtime, getsize, isdir, isfile, join

from twisted.python import constants  # pylint: disable=import-error

from platformio.compat import hashlib_encode_data


class PROJECT_SYNC_STAGE(constants.Flags):
    INIT = constants.FlagConstant()
    DBINDEX = constants.FlagConstant()
    DELETE = constants.FlagConstant()
    UPLOAD = constants.FlagConstant()
    EXTRACTED = constants.FlagConstant()
    COMPLETED = constants.FlagConstant()


class ProjectSync:
    def __init__(self, path):
        self.path = path
        if not isdir(self.path):
            os.makedirs(self.path)
        self.items = []
        self._db = {}

    def add_item(self, path, relpath, cb_filter=None):
        self.items.append((path, relpath, cb_filter))

    def get_items(self):
        return self.items

    def rebuild_dbindex(self):
        self._db = {}
        for (path, relpath, cb_filter) in self.items:
            if cb_filter and not cb_filter(path):
                continue
            self._insert_to_db(path, relpath)
            if not isdir(path):
                continue
            for (root, _, files) in os.walk(path, followlinks=True):
                for name in files:
                    self._insert_to_db(
                        join(root, name), join(relpath, root[len(path) + 1 :], name)
                    )

    def _insert_to_db(self, path, relpath):
        if not isfile(path):
            return
        index_hash = "%s-%s-%s" % (relpath, getmtime(path), getsize(path))
        index = crc32(hashlib_encode_data(index_hash))
        self._db[index] = (path, relpath)

    def get_dbindex(self):
        return list(self._db.keys())

    def delete_dbindex(self, dbindex):
        for index in dbindex:
            if index not in self._db:
                continue
            path = self._db[index][0]
            if isfile(path):
                os.remove(path)
            del self._db[index]
        self.delete_empty_folders()
        return True

    def delete_empty_folders(self):
        deleted = False
        for item in self.items:
            if not isdir(item[0]):
                continue
            for root, dirs, files in os.walk(item[0]):
                if not dirs and not files and root != item[0]:
                    deleted = True
                    os.rmdir(root)
        if deleted:
            return self.delete_empty_folders()

        return True

    def compress_items(self, fileobj, dbindex, max_size):
        compressed = []
        total_size = 0
        tar_opts = dict(fileobj=fileobj, mode="w:gz", bufsize=0, dereference=True)
        with tarfile.open(**tar_opts) as tgz:
            for index in dbindex:
                compressed.append(index)
                if index not in self._db:
                    continue
                path, relpath = self._db[index]
                tgz.add(path, relpath)
                total_size += getsize(path)
                if total_size > max_size:
                    break
        return compressed

    def decompress_items(self, fileobj):
        fileobj.seek(0)
        with tarfile.open(fileobj=fileobj, mode="r:gz") as tgz:
            tgz.extractall(self.path)
        return True

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

from os import chmod
from os.path import exists, islink, join
from tarfile import open as tarfile_open
from time import mktime
from zipfile import ZipFile

import click

from platformio import exception, util


class ArchiveBase(object):

    def __init__(self, arhfileobj):
        self._afo = arhfileobj

    def get_items(self):
        raise NotImplementedError()

    def get_item_filename(self, item):
        raise NotImplementedError()

    def extract_item(self, item, dest_dir):
        self._afo.extract(item, dest_dir)
        self.after_extract(item, dest_dir)

    def after_extract(self, item, dest_dir):
        pass

    def close(self):
        self._afo.close()


class TARArchive(ArchiveBase):

    def __init__(self, archpath):
        super(TARArchive, self).__init__(tarfile_open(archpath))

    def get_items(self):
        return self._afo.getmembers()

    def get_item_filename(self, item):
        return item.name


class ZIPArchive(ArchiveBase):

    def __init__(self, archpath):
        super(ZIPArchive, self).__init__(ZipFile(archpath))

    @staticmethod
    def preserve_permissions(item, dest_dir):
        attrs = item.external_attr >> 16L
        if attrs:
            chmod(join(dest_dir, item.filename), attrs)

    @staticmethod
    def preserve_mtime(item, dest_dir):
        util.change_filemtime(
            join(dest_dir, item.filename),
            mktime(list(item.date_time) + [0] * 3))

    def get_items(self):
        return self._afo.infolist()

    def get_item_filename(self, item):
        return item.filename

    def after_extract(self, item, dest_dir):
        self.preserve_permissions(item, dest_dir)
        self.preserve_mtime(item, dest_dir)


class FileUnpacker(object):

    def __init__(self, archpath):
        self.archpath = archpath
        self._unpacker = None

    def __enter__(self):
        if self.archpath.lower().endswith((".gz", ".bz2")):
            self._unpacker = TARArchive(self.archpath)
        elif self.archpath.lower().endswith(".zip"):
            self._unpacker = ZIPArchive(self.archpath)
        if not self._unpacker:
            raise exception.UnsupportedArchiveType(self.archpath)
        return self

    def __exit__(self, *args):
        if self._unpacker:
            self._unpacker.close()

    def unpack(self, dest_dir=".", with_progress=True):
        assert self._unpacker
        if not with_progress:
            click.echo("Unpacking...")
            for item in self._unpacker.get_items():
                self._unpacker.extract_item(item, dest_dir)
        else:
            items = self._unpacker.get_items()
            with click.progressbar(items, label="Unpacking") as pb:
                for item in pb:
                    self._unpacker.extract_item(item, dest_dir)

        # check on disk
        for item in self._unpacker.get_items():
            filename = self._unpacker.get_item_filename(item)
            item_path = join(dest_dir, filename)
            if not islink(item_path) and not exists(item_path):
                raise exception.ExtractArchiveItemError(filename, dest_dir)

        return True

# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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
from os.path import join, splitext
from tarfile import open as tarfile_open
from time import mktime
from zipfile import ZipFile

import click

from platformio import app, util
from platformio.exception import UnsupportedArchiveType


class ArchiveBase(object):

    def __init__(self, arhfileobj):
        self._afo = arhfileobj

    def get_items(self):
        raise NotImplementedError()

    def extract_item(self, item, dest_dir):
        self._afo.extract(item, dest_dir)
        self.after_extract(item, dest_dir)

    def after_extract(self, item, dest_dir):
        pass


class TARArchive(ArchiveBase):

    def __init__(self, archpath):
        ArchiveBase.__init__(self, tarfile_open(archpath))

    def get_items(self):
        return self._afo.getmembers()


class ZIPArchive(ArchiveBase):

    def __init__(self, archpath):
        ArchiveBase.__init__(self, ZipFile(archpath))

    @staticmethod
    def preserve_permissions(item, dest_dir):
        attrs = item.external_attr >> 16L
        if attrs:
            chmod(join(dest_dir, item.filename), attrs)

    @staticmethod
    def preserve_mtime(item, dest_dir):
        util.change_filemtime(
            join(dest_dir, item.filename),
            mktime(list(item.date_time) + [0] * 3)
        )

    def get_items(self):
        return self._afo.infolist()

    def after_extract(self, item, dest_dir):
        self.preserve_permissions(item, dest_dir)
        self.preserve_mtime(item, dest_dir)


class FileUnpacker(object):

    def __init__(self, archpath, dest_dir="."):
        self._archpath = archpath
        self._dest_dir = dest_dir
        self._unpacker = None

        _, archext = splitext(archpath.lower())
        if archext in (".gz", ".bz2"):
            self._unpacker = TARArchive(archpath)
        elif archext == ".zip":
            self._unpacker = ZIPArchive(archpath)

        if not self._unpacker:
            raise UnsupportedArchiveType(archpath)

    def start(self):
        if app.is_disabled_progressbar():
            click.echo("Unpacking...")
            for item in self._unpacker.get_items():
                self._unpacker.extract_item(item, self._dest_dir)
        else:
            with click.progressbar(self._unpacker.get_items(),
                                   label="Unpacking") as pb:
                for item in pb:
                    self._unpacker.extract_item(item, self._dest_dir)
        return True

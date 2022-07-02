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
from tarfile import open as tarfile_open
from time import mktime
from zipfile import ZipFile

import click

from platformio import fs
from platformio.package.exception import PackageException


class ExtractArchiveItemError(PackageException):

    MESSAGE = (
        "Could not extract `{0}` to `{1}`. Try to disable antivirus "
        "tool or check this solution -> https://bit.ly/faq-package-manager"
    )


class BaseArchiver:
    def __init__(self, arhfileobj):
        self._afo = arhfileobj

    def get_items(self):
        raise NotImplementedError()

    def get_item_filename(self, item):
        raise NotImplementedError()

    def is_link(self, item):
        raise NotImplementedError()

    def extract_item(self, item, dest_dir):
        self._afo.extract(item, dest_dir)
        self.after_extract(item, dest_dir)

    def after_extract(self, item, dest_dir):
        pass

    def close(self):
        self._afo.close()


class TARArchiver(BaseArchiver):
    def __init__(self, archpath):
        super().__init__(tarfile_open(archpath))  # pylint: disable=consider-using-with

    def get_items(self):
        return self._afo.getmembers()

    def get_item_filename(self, item):
        return item.name

    @staticmethod
    def is_link(item):  # pylint: disable=arguments-differ
        return item.islnk() or item.issym()

    @staticmethod
    def resolve_path(path):
        return os.path.realpath(os.path.abspath(path))

    def is_bad_path(self, path, base):
        return not self.resolve_path(os.path.join(base, path)).startswith(base)

    def is_bad_link(self, item, base):
        return not self.resolve_path(
            os.path.join(os.path.join(base, os.path.dirname(item.name)), item.linkname)
        ).startswith(base)

    def extract_item(self, item, dest_dir):
        dest_dir = self.resolve_path(dest_dir)
        bad_conds = [
            self.is_bad_path(item.name, dest_dir),
            self.is_link(item) and self.is_bad_link(item, dest_dir),
        ]
        if not any(bad_conds):
            super().extract_item(item, dest_dir)
        else:
            click.secho(
                "Blocked insecure item `%s` from TAR archive" % item.name,
                fg="red",
                err=True,
            )


class ZIPArchiver(BaseArchiver):
    def __init__(self, archpath):
        super().__init__(ZipFile(archpath))  # pylint: disable=consider-using-with

    @staticmethod
    def preserve_permissions(item, dest_dir):
        attrs = item.external_attr >> 16
        if attrs:
            os.chmod(os.path.join(dest_dir, item.filename), attrs)

    @staticmethod
    def preserve_mtime(item, dest_dir):
        fs.change_filemtime(
            os.path.join(dest_dir, item.filename),
            mktime(tuple(item.date_time) + tuple([0, 0, 0])),
        )

    @staticmethod
    def is_link(_):  # pylint: disable=arguments-differ
        return False

    def get_items(self):
        return self._afo.infolist()

    def get_item_filename(self, item):
        return item.filename

    def after_extract(self, item, dest_dir):
        self.preserve_permissions(item, dest_dir)
        self.preserve_mtime(item, dest_dir)


class FileUnpacker:
    def __init__(self, path):
        self.path = path
        self._archiver = None

    def __enter__(self):
        self._archiver = self.new_archiver(self.path)
        return self

    def __exit__(self, *args):
        if self._archiver:
            self._archiver.close()

    @staticmethod
    def new_archiver(path):
        magic_map = {
            b"\x1f\x8b\x08": TARArchiver,
            b"\x42\x5a\x68": TARArchiver,
            b"\x50\x4b\x03\x04": ZIPArchiver,
        }
        magic_len = max(len(k) for k in magic_map)
        with open(path, "rb") as fp:
            data = fp.read(magic_len)
            for magic, archiver in magic_map.items():
                if data.startswith(magic):
                    return archiver(path)
        raise PackageException("Unknown archive type '%s'" % path)

    def unpack(
        self, dest_dir=None, with_progress=True, check_unpacked=True, silent=False
    ):
        assert self._archiver
        if not dest_dir:
            dest_dir = os.getcwd()
        if not with_progress or silent:
            if not silent:
                click.echo("Unpacking...")
            for item in self._archiver.get_items():
                self._archiver.extract_item(item, dest_dir)
        else:
            items = self._archiver.get_items()
            with click.progressbar(items, label="Unpacking") as pb:
                for item in pb:
                    self._archiver.extract_item(item, dest_dir)

        if not check_unpacked:
            return True

        # check on disk
        for item in self._archiver.get_items():
            filename = self._archiver.get_item_filename(item)
            item_path = os.path.join(dest_dir, filename)
            try:
                if not self._archiver.is_link(item) and not os.path.exists(item_path):
                    raise ExtractArchiveItemError(filename, dest_dir)
            except NotImplementedError:
                pass
        return True

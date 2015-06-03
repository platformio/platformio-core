# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from email.utils import parsedate_tz
from math import ceil
from os.path import getsize, join
from time import mktime

import click
import requests

from platformio import util
from platformio.exception import (FDSHASumMismatch, FDSizeMismatch,
                                  FDUnrecognizedStatusCode)


class FileDownloader(object):

    CHUNK_SIZE = 1024

    def __init__(self, url, dest_dir=None):
        self._url = url
        self._fname = url.split("/")[-1]

        self._destination = self._fname
        if dest_dir:
            self.set_destination(join(dest_dir, self._fname))

        self._progressbar = None
        self._request = None

        # make connection
        self._request = requests.get(url, stream=True,
                                     headers=util.get_request_defheaders())
        if self._request.status_code != 200:
            raise FDUnrecognizedStatusCode(self._request.status_code, url)

    def set_destination(self, destination):
        self._destination = destination

    def get_filepath(self):
        return self._destination

    def get_lmtime(self):
        return self._request.headers['last-modified']

    def get_size(self):
        return int(self._request.headers['content-length'])

    def start(self):
        itercontent = self._request.iter_content(chunk_size=self.CHUNK_SIZE)
        f = open(self._destination, "wb")
        chunks = int(ceil(self.get_size() / float(self.CHUNK_SIZE)))

        if util.is_ci():
            click.echo("Downloading...")
            for _ in range(0, chunks):
                f.write(next(itercontent))
        else:
            with click.progressbar(length=chunks, label="Downloading") as pb:
                for _ in pb:
                    f.write(next(itercontent))
        f.close()
        self._request.close()

        self._preserve_filemtime(self.get_lmtime())

    def verify(self, sha1=None):
        _dlsize = getsize(self._destination)
        if _dlsize != self.get_size():
            raise FDSizeMismatch(_dlsize, self._fname, self.get_size())

        if not sha1:
            return

        dlsha1 = None
        try:
            result = util.exec_command(["sha1sum", self._destination])
            dlsha1 = result['out']
        except OSError:
            try:
                result = util.exec_command(
                    ["shasum", "-a", "1", self._destination])
                dlsha1 = result['out']
            except OSError:
                pass

        if dlsha1:
            dlsha1 = dlsha1[1:41] if dlsha1.startswith("\\") else dlsha1[:40]
            if sha1 != dlsha1:
                raise FDSHASumMismatch(dlsha1, self._fname, sha1)

    def _preserve_filemtime(self, lmdate):
        timedata = parsedate_tz(lmdate)
        lmtime = mktime(timedata[:9])
        util.change_filemtime(self._destination, lmtime)

    def __del__(self):
        if self._request:
            self._request.close()

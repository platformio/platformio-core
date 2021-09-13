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

import io
import math
from email.utils import parsedate_tz
from os.path import getsize, join
from time import mktime

import click
import requests

from platformio import __default_requests_timeout__, app, fs
from platformio.package.exception import PackageException


class FileDownloader(object):
    def __init__(self, url, dest_dir=None):
        self._request = None
        # make connection
        self._request = requests.get(
            url,
            stream=True,
            headers={"User-Agent": app.get_user_agent()},
            timeout=__default_requests_timeout__,
        )
        if self._request.status_code != 200:
            raise PackageException(
                "Got the unrecognized status code '{0}' when downloaded {1}".format(
                    self._request.status_code, url
                )
            )

        disposition = self._request.headers.get("content-disposition")
        if disposition and "filename=" in disposition:
            self._fname = (
                disposition[disposition.index("filename=") + 9 :]
                .replace('"', "")
                .replace("'", "")
            )
        else:
            self._fname = [p for p in url.split("/") if p][-1]
        self._fname = str(self._fname)
        self._destination = self._fname
        if dest_dir:
            self.set_destination(join(dest_dir, self._fname))

    def set_destination(self, destination):
        self._destination = destination

    def get_filepath(self):
        return self._destination

    def get_lmtime(self):
        return self._request.headers.get("last-modified")

    def get_size(self):
        if "content-length" not in self._request.headers:
            return -1
        return int(self._request.headers["content-length"])

    def start(self, with_progress=True, silent=False):
        label = "Downloading"
        itercontent = self._request.iter_content(chunk_size=io.DEFAULT_BUFFER_SIZE)
        fp = open(self._destination, "wb")  # pylint: disable=consider-using-with
        try:
            if not with_progress or self.get_size() == -1:
                if not silent:
                    click.echo("%s..." % label)
                for chunk in itercontent:
                    if chunk:
                        fp.write(chunk)
            else:
                chunks = int(math.ceil(self.get_size() / float(io.DEFAULT_BUFFER_SIZE)))
                with click.progressbar(length=chunks, label=label) as pb:
                    for _ in pb:
                        fp.write(next(itercontent))
        finally:
            fp.close()
            self._request.close()

        if self.get_lmtime():
            self._preserve_filemtime(self.get_lmtime())

        return True

    def verify(self, checksum=None):
        _dlsize = getsize(self._destination)
        if self.get_size() != -1 and _dlsize != self.get_size():
            raise PackageException(
                (
                    "The size ({0:d} bytes) of downloaded file '{1}' "
                    "is not equal to remote size ({2:d} bytes)"
                ).format(_dlsize, self._fname, self.get_size())
            )
        if not checksum:
            return True

        checksum_len = len(checksum)
        hash_algo = None
        if checksum_len == 32:
            hash_algo = "md5"
        elif checksum_len == 40:
            hash_algo = "sha1"
        elif checksum_len == 64:
            hash_algo = "sha256"

        if not hash_algo:
            raise PackageException(
                "Could not determine checksum algorithm by %s" % checksum
            )

        dl_checksum = fs.calculate_file_hashsum(hash_algo, self._destination)
        if checksum.lower() != dl_checksum.lower():
            raise PackageException(
                "The checksum '{0}' of the downloaded file '{1}' "
                "does not match to the remote '{2}'".format(
                    dl_checksum, self._fname, checksum
                )
            )
        return True

    def _preserve_filemtime(self, lmdate):
        timedata = parsedate_tz(lmdate)
        lmtime = mktime(timedata[:9])
        fs.change_filemtime(self._destination, lmtime)

    def __del__(self):
        if self._request:
            self._request.close()

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
from email.utils import parsedate
from os.path import getsize, join
from time import mktime

import click

from platformio import fs
from platformio.compat import is_terminal
from platformio.http import HTTPSession
from platformio.package.exception import PackageException


class FileDownloader:
    def __init__(self, url, dest_dir=None):
        self._http_session = HTTPSession()
        self._http_response = None
        # make connection
        self._http_response = self._http_session.get(
            url,
            stream=True,
        )
        if self._http_response.status_code != 200:
            raise PackageException(
                "Got the unrecognized status code '{0}' when downloaded {1}".format(
                    self._http_response.status_code, url
                )
            )

        disposition = self._http_response.headers.get("content-disposition")
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
        return self._http_response.headers.get("last-modified")

    def get_size(self):
        if "content-length" not in self._http_response.headers:
            return -1
        return int(self._http_response.headers["content-length"])

    def start(self, with_progress=True, silent=False):
        label = "Downloading"
        file_size = self.get_size()
        itercontent = self._http_response.iter_content(
            chunk_size=io.DEFAULT_BUFFER_SIZE
        )
        try:
            with open(self._destination, "wb") as fp:
                if file_size == -1 or not with_progress or silent:
                    if not silent:
                        click.echo(f"{label}...")
                    for chunk in itercontent:
                        fp.write(chunk)

                elif not is_terminal():
                    click.echo(f"{label} 0%", nl=False)
                    print_percent_step = 10
                    printed_percents = 0
                    downloaded_size = 0
                    for chunk in itercontent:
                        fp.write(chunk)
                        downloaded_size += len(chunk)
                        if (downloaded_size / file_size * 100) >= (
                            printed_percents + print_percent_step
                        ):
                            printed_percents += print_percent_step
                            click.echo(f" {printed_percents}%", nl=False)
                    click.echo("")

                else:
                    with click.progressbar(
                        length=file_size,
                        iterable=itercontent,
                        label=label,
                        update_min_steps=min(
                            256 * 1024, file_size / 100
                        ),  # every 256Kb or less,
                    ) as pb:
                        for chunk in pb:
                            pb.update(len(chunk))
                            fp.write(chunk)
        finally:
            self._http_response.close()
            self._http_session.close()

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
        lmtime = mktime(parsedate(lmdate))
        fs.change_filemtime(self._destination, lmtime)

    def __del__(self):
        self._http_session.close()
        if self._http_response:
            self._http_response.close()

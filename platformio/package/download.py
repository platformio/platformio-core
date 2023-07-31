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
import tempfile
import time
from email.utils import parsedate
from urllib.parse import urlparse

import click
import httpx

from platformio import fs
from platformio.compat import is_terminal
from platformio.http import apply_default_kwargs
from platformio.package.exception import PackageException


class FileDownloader:
    def __init__(self, url, dst_dir=None):
        self.url = url
        self.dst_dir = dst_dir

        self._destination = None
        self._http_response = None

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

    def get_disposition_filname(self):
        disposition = self._http_response.headers.get("content-disposition")
        if disposition and "filename=" in disposition:
            return (
                disposition[disposition.index("filename=") + 9 :]
                .replace('"', "")
                .replace("'", "")
            )
        return [p for p in urlparse(self.url).path.split("/") if p][-1]

    def start(self, with_progress=True, silent=False):
        label = "Downloading"
        with httpx.stream("GET", self.url, **apply_default_kwargs()) as response:
            if response.status_code != 200:
                raise PackageException(
                    f"Got the unrecognized status code '{response.status_code}' "
                    "when downloading '{self.url}'"
                )
            self._http_response = response
            total_size = self.get_size()
            if not self._destination:
                assert self.dst_dir

            with open(self._destination, "wb") as fp:
                if total_size == -1 or not with_progress or silent:
                    if not silent:
                        click.echo(f"{label}...")
                    for chunk in response.iter_bytes():
                        fp.write(chunk)

                elif not is_terminal():
                    click.echo(f"{label} 0%", nl=False)
                    print_percent_step = 10
                    printed_percents = 0
                    downloaded_size = 0
                    for chunk in response.iter_bytes():
                        fp.write(chunk)
                        downloaded_size += len(chunk)
                        if (downloaded_size / total_size * 100) >= (
                            printed_percents + print_percent_step
                        ):
                            printed_percents += print_percent_step
                            click.echo(f" {printed_percents}%", nl=False)
                    click.echo("")

                else:
                    with click.progressbar(
                        length=total_size,
                        iterable=response.iter_bytes(),
                        label=label,
                        update_min_steps=min(
                            256 * 1024, total_size / 100
                        ),  # every 256Kb or less
                    ) as pb:
                        for chunk in pb:
                            pb.update(len(chunk))
                            fp.write(chunk)

        last_modified = self.get_lmtime()
        if last_modified:
            self._preserve_filemtime(last_modified)

        return True

    def _set_tmp_destination(self):
        dst_dir = self.dst_dir or tempfile.mkdtemp()
        self.set_destination(os.path.join(dst_dir, self.get_disposition_filname()))

    def _preserve_filemtime(self, lmdate):
        lmtime = time.mktime(parsedate(lmdate))
        fs.change_filemtime(self._destination, lmtime)

    def verify(self, checksum=None):
        remote_size = self.get_size()
        downloaded_size = os.path.getsize(self._destination)
        if remote_size not in (-1, downloaded_size):
            raise PackageException(
                f"The size ({downloaded_size} bytes) of downloaded file "
                f"'{self._destination}' is not equal to remote size "
                f"({remote_size} bytes)"
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
                f"Could not determine checksum algorithm by {checksum}"
            )

        dl_checksum = fs.calculate_file_hashsum(hash_algo, self._destination)
        if checksum.lower() != dl_checksum.lower():
            raise PackageException(
                "The checksum '{0}' of the downloaded file '{1}' "
                "does not match to the remote '{2}'".format(
                    dl_checksum, self._destination, checksum
                )
            )
        return True

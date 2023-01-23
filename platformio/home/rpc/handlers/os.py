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

import glob
import io
import os
import shutil
from functools import cmp_to_key

import click
from starlette.concurrency import run_in_threadpool

from platformio import fs
from platformio.cache import ContentCache
from platformio.device.list.util import list_logical_devices
from platformio.http import HTTPSession, ensure_internet_on


class HTTPAsyncSession(HTTPSession):
    async def request(  # pylint: disable=signature-differs,invalid-overridden-method
        self, *args, **kwargs
    ):
        func = super().request
        return await run_in_threadpool(func, *args, **kwargs)


class OSRPC:
    @staticmethod
    async def fetch_content(url, data=None, headers=None, cache_valid=None):
        if not headers:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
                    "AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 "
                    "Safari/603.3.8"
                )
            }
        cache_key = ContentCache.key_from_args(url, data) if cache_valid else None
        with ContentCache() as cc:
            if cache_key:
                result = cc.get(cache_key)
                if result is not None:
                    return result

        # check internet before and resolve issue with 60 seconds timeout
        ensure_internet_on(raise_exception=True)

        session = HTTPAsyncSession()
        if data:
            r = await session.post(url, data=data, headers=headers)
        else:
            r = await session.get(url, headers=headers)

        r.raise_for_status()
        result = r.text
        if cache_valid:
            with ContentCache() as cc:
                cc.set(cache_key, result, cache_valid)
        return result

    async def request_content(self, uri, data=None, headers=None, cache_valid=None):
        if uri.startswith("http"):
            return await self.fetch_content(uri, data, headers, cache_valid)
        if os.path.isfile(uri):
            with io.open(uri, encoding="utf-8") as fp:
                return fp.read()
        return None

    @staticmethod
    def open_url(url):
        return click.launch(url)

    @staticmethod
    def reveal_file(path):
        return click.launch(path, locate=True)

    @staticmethod
    def open_file(path):
        return click.launch(path)

    @staticmethod
    def is_file(path):
        return os.path.isfile(path)

    @staticmethod
    def is_dir(path):
        return os.path.isdir(path)

    @staticmethod
    def make_dirs(path):
        return os.makedirs(path)

    @staticmethod
    def get_file_mtime(path):
        return os.path.getmtime(path)

    @staticmethod
    def rename(src, dst):
        return os.rename(src, dst)

    @staticmethod
    def copy(src, dst):
        return shutil.copytree(src, dst, symlinks=True)

    @staticmethod
    def glob(pathnames, root=None):
        if not isinstance(pathnames, list):
            pathnames = [pathnames]
        result = set()
        for pathname in pathnames:
            result |= set(
                glob.glob(
                    os.path.join(root, pathname) if root else pathname, recursive=True
                )
            )
        return list(result)

    @staticmethod
    def list_dir(path):
        def _cmp(x, y):
            if x[1] and not y[1]:
                return -1
            if not x[1] and y[1]:
                return 1
            if x[0].lower() > y[0].lower():
                return 1
            if x[0].lower() < y[0].lower():
                return -1
            return 0

        items = []
        if path.startswith("~"):
            path = fs.expanduser(path)
        if not os.path.isdir(path):
            return items
        for item in os.listdir(path):
            try:
                item_is_dir = os.path.isdir(os.path.join(path, item))
                if item_is_dir:
                    os.listdir(os.path.join(path, item))
                items.append((item, item_is_dir))
            except OSError:
                pass
        return sorted(items, key=cmp_to_key(_cmp))

    @staticmethod
    def get_logical_devices():
        items = []
        for item in list_logical_devices():
            if item["name"]:
                item["name"] = item["name"]
            items.append(item)
        return items

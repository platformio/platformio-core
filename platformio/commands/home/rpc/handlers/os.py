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

from __future__ import absolute_import

import glob
import os
import shutil
from functools import cmp_to_key

import click
from twisted.internet import defer  # pylint: disable=import-error

from platformio import app, fs, util
from platformio.commands.home import helpers
from platformio.compat import PY2, get_filesystem_encoding


class OSRPC(object):
    @staticmethod
    @defer.inlineCallbacks
    def fetch_content(uri, data=None, headers=None, cache_valid=None):
        if not headers:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
                    "AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 "
                    "Safari/603.3.8"
                )
            }
        cache_key = app.ContentCache.key_from_args(uri, data) if cache_valid else None
        with app.ContentCache() as cc:
            if cache_key:
                result = cc.get(cache_key)
                if result is not None:
                    defer.returnValue(result)

        # check internet before and resolve issue with 60 seconds timeout
        util.internet_on(raise_exception=True)

        session = helpers.requests_session()
        if data:
            r = yield session.post(uri, data=data, headers=headers)
        else:
            r = yield session.get(uri, headers=headers)

        r.raise_for_status()
        result = r.text
        if cache_valid:
            with app.ContentCache() as cc:
                cc.set(cache_key, result, cache_valid)
        defer.returnValue(result)

    def request_content(self, uri, data=None, headers=None, cache_valid=None):
        if uri.startswith("http"):
            return self.fetch_content(uri, data, headers, cache_valid)
        if os.path.isfile(uri):
            return fs.get_file_contents(uri, encoding="utf8")
        return None

    @staticmethod
    def open_url(url):
        return click.launch(url)

    @staticmethod
    def reveal_file(path):
        return click.launch(
            path.encode(get_filesystem_encoding()) if PY2 else path, locate=True
        )

    @staticmethod
    def open_file(path):
        return click.launch(path.encode(get_filesystem_encoding()) if PY2 else path)

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
        return shutil.copytree(src, dst)

    @staticmethod
    def glob(pathnames, root=None):
        if not isinstance(pathnames, list):
            pathnames = [pathnames]
        result = set()
        for pathname in pathnames:
            result |= set(glob.glob(os.path.join(root, pathname) if root else pathname))
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
        for item in util.get_logical_devices():
            if item["name"]:
                item["name"] = item["name"]
            items.append(item)
        return items

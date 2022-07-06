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

import codecs
import hashlib
import os
from time import time

from platformio import app, fs
from platformio.compat import hashlib_encode_data
from platformio.package.lockfile import LockFile
from platformio.project.helpers import get_project_cache_dir


class ContentCache:
    def __init__(self, namespace=None):
        self.cache_dir = os.path.join(get_project_cache_dir(), namespace or "content")
        self._db_path = os.path.join(self.cache_dir, "db.data")
        self._lockfile = None
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

    def __enter__(self):
        # cleanup obsolete items
        self.delete()
        return self

    def __exit__(self, type_, value, traceback):
        pass

    @staticmethod
    def key_from_args(*args):
        h = hashlib.sha1()
        for arg in args:
            if arg:
                h.update(hashlib_encode_data(arg))
        return h.hexdigest()

    def get_cache_path(self, key):
        assert "/" not in key and "\\" not in key
        key = str(key)
        assert len(key) > 3
        return os.path.join(self.cache_dir, key)

    def get(self, key):
        cache_path = self.get_cache_path(key)
        if not os.path.isfile(cache_path):
            return None
        with codecs.open(cache_path, "rb", encoding="utf8") as fp:
            return fp.read()

    def set(self, key, data, valid):
        if not app.get_setting("enable_cache"):
            return False
        cache_path = self.get_cache_path(key)
        if os.path.isfile(cache_path):
            self.delete(key)
        if not data:
            return False
        tdmap = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        assert valid.endswith(tuple(tdmap))
        expire_time = int(time() + tdmap[valid[-1]] * int(valid[:-1]))

        if not self._lock_dbindex():
            return False

        if not os.path.isdir(os.path.dirname(cache_path)):
            os.makedirs(os.path.dirname(cache_path))
        try:
            with codecs.open(cache_path, mode="wb", encoding="utf8") as fp:
                fp.write(data)
            with open(self._db_path, mode="a", encoding="utf8") as fp:
                fp.write("%s=%s\n" % (str(expire_time), os.path.basename(cache_path)))
        except UnicodeError:
            if os.path.isfile(cache_path):
                try:
                    os.remove(cache_path)
                except OSError:
                    pass

        return self._unlock_dbindex()

    def delete(self, keys=None):
        """Keys=None, delete expired items"""
        if not os.path.isfile(self._db_path):
            return None
        if not keys:
            keys = []
        if not isinstance(keys, list):
            keys = [keys]
        paths_for_delete = [self.get_cache_path(k) for k in keys]
        found = False
        newlines = []
        with open(self._db_path, encoding="utf8") as fp:
            for line in fp.readlines():
                line = line.strip()
                if "=" not in line:
                    continue
                expire, fname = line.split("=")
                path = os.path.join(self.cache_dir, fname)
                try:
                    if (
                        time() < int(expire)
                        and os.path.isfile(path)
                        and path not in paths_for_delete
                    ):
                        newlines.append(line)
                        continue
                except ValueError:
                    pass
                found = True
                if os.path.isfile(path):
                    try:
                        os.remove(path)
                        if not os.listdir(os.path.dirname(path)):
                            fs.rmtree(os.path.dirname(path))
                    except OSError:
                        pass

        if found and self._lock_dbindex():
            with open(self._db_path, mode="w", encoding="utf8") as fp:
                fp.write("\n".join(newlines) + "\n")
            self._unlock_dbindex()

        return True

    def clean(self):
        if not os.path.isdir(self.cache_dir):
            return
        fs.rmtree(self.cache_dir)

    def _lock_dbindex(self):
        self._lockfile = LockFile(self.cache_dir)
        try:
            self._lockfile.acquire()
        except:  # pylint: disable=bare-except
            return False

        return True

    def _unlock_dbindex(self):
        if self._lockfile:
            self._lockfile.release()
        return True


#
# Helpers
#


def cleanup_content_cache(namespace=None):
    with ContentCache(namespace) as cc:
        cc.clean()

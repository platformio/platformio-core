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

# pylint: disable=unused-import, no-name-in-module, import-error,
# pylint: disable=no-member, undefined-variable, unexpected-keyword-arg

import glob
import inspect
import json
import locale
import os
import re
import sys

from platformio.exception import UserSideException

PY2 = sys.version_info[0] == 2
CYGWIN = sys.platform.startswith("cygwin")
WINDOWS = sys.platform.startswith("win")
MACOS = sys.platform.startswith("darwin")


def get_filesystem_encoding():
    return sys.getfilesystemencoding() or sys.getdefaultencoding()


def get_locale_encoding():
    try:
        return locale.getdefaultlocale()[1]
    except ValueError:
        return None


def get_object_members(obj, ignore_private=True):
    members = inspect.getmembers(obj, lambda a: not inspect.isroutine(a))
    if not ignore_private:
        return members
    return {
        item[0]: item[1]
        for item in members
        if not (item[0].startswith("__") and item[0].endswith("__"))
    }


def ci_strings_are_equal(a, b):
    if a == b:
        return True
    if not a or not b:
        return False
    return a.strip().lower() == b.strip().lower()


def ensure_python3(raise_exception=True):
    compatible = sys.version_info >= (3, 6)
    if not raise_exception or compatible:
        return compatible
    raise UserSideException(
        "Python 3.6 or later is required for this operation. \n"
        "Please check a migration guide:\n"
        "https://docs.platformio.org/en/latest/core/migration.html"
        "#drop-support-for-python-2-and-3-5"
    )


if PY2:
    import imp

    string_types = (str, unicode)

    def create_task(coro, name=None):
        raise NotImplementedError

    def get_running_loop():
        raise NotImplementedError

    def is_bytes(x):
        return isinstance(x, (buffer, bytearray))

    def path_to_unicode(path):
        if isinstance(path, unicode):
            return path
        return path.decode(get_filesystem_encoding())

    def hashlib_encode_data(data):
        if is_bytes(data):
            return data
        if isinstance(data, unicode):
            data = data.encode(get_filesystem_encoding())
        elif not isinstance(data, string_types):
            data = str(data)
        return data

    def dump_json_to_unicode(obj):
        if isinstance(obj, unicode):
            return obj
        return json.dumps(
            obj, encoding=get_filesystem_encoding(), ensure_ascii=False
        ).encode("utf8")

    _magic_check = re.compile("([*?[])")
    _magic_check_bytes = re.compile(b"([*?[])")

    def glob_recursive(pathname):
        return glob.glob(pathname)

    def glob_escape(pathname):
        """Escape all special characters."""
        # https://github.com/python/cpython/blob/master/Lib/glob.py#L161
        # Escaping is done by wrapping any of "*?[" between square brackets.
        # Metacharacters do not work in the drive part and shouldn't be
        # escaped.
        drive, pathname = os.path.splitdrive(pathname)
        if isinstance(pathname, bytes):
            pathname = _magic_check_bytes.sub(br"[\1]", pathname)
        else:
            pathname = _magic_check.sub(r"[\1]", pathname)
        return drive + pathname

    def load_python_module(name, pathname):
        return imp.load_source(name, pathname)


else:
    import importlib.util
    from glob import escape as glob_escape

    if sys.version_info >= (3, 7):
        from asyncio import create_task, get_running_loop
    else:
        from asyncio import ensure_future as create_task
        from asyncio import get_event_loop as get_running_loop

    string_types = (str,)

    def is_bytes(x):
        return isinstance(x, (bytes, memoryview, bytearray))

    def path_to_unicode(path):
        return path

    def hashlib_encode_data(data):
        if is_bytes(data):
            return data
        if not isinstance(data, string_types):
            data = str(data)
        return data.encode()

    def dump_json_to_unicode(obj):
        if isinstance(obj, string_types):
            return obj
        return json.dumps(obj)

    def glob_recursive(pathname):
        return glob.glob(pathname, recursive=True)

    def load_python_module(name, pathname):
        spec = importlib.util.spec_from_file_location(name, pathname)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

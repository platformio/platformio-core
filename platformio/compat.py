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
# pylint: disable=no-member, undefined-variable

import inspect
import json
import locale
import os
import re
import sys

PY2 = sys.version_info[0] == 2
CYGWIN = sys.platform.startswith("cygwin")
WINDOWS = sys.platform.startswith("win")


def get_filesystem_encoding():
    return sys.getfilesystemencoding() or sys.getdefaultencoding()


def get_locale_encoding():
    try:
        return locale.getdefaultlocale()[1]
    except ValueError:
        return None


def get_class_attributes(cls):
    attributes = inspect.getmembers(cls, lambda a: not inspect.isroutine(a))
    return {
        a[0]: a[1]
        for a in attributes
        if not (a[0].startswith("__") and a[0].endswith("__"))
    }


if PY2:
    import imp

    string_types = (str, unicode)

    def is_bytes(x):
        return isinstance(x, (buffer, bytearray))

    def path_to_unicode(path):
        if isinstance(path, unicode):
            return path
        return path.decode(get_filesystem_encoding()).encode("utf-8")

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
            obj, encoding=get_filesystem_encoding(), ensure_ascii=False, sort_keys=True
        ).encode("utf8")

    _magic_check = re.compile("([*?[])")
    _magic_check_bytes = re.compile(b"([*?[])")

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
        return json.dumps(obj, ensure_ascii=False, sort_keys=True)

    def load_python_module(name, pathname):
        spec = importlib.util.spec_from_file_location(name, pathname)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

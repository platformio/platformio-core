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

import hashlib
import os
import re

from SCons.Platform import TempFileMunge  # pylint: disable=import-error
from SCons.Script import COMMAND_LINE_TARGETS  # pylint: disable=import-error
from SCons.Subst import quote_spaces  # pylint: disable=import-error

from platformio.compat import IS_WINDOWS, hashlib_encode_data

# There are the next limits depending on a platform:
# - Windows = 8192
# - Unix    = 131072
# We need ~512 characters for compiler and temporary file paths
MAX_LINE_LENGTH = (8192 if IS_WINDOWS else 131072) - 512

WINPATHSEP_RE = re.compile(r"\\([^\"'\\]|$)")


def tempfile_arg_esc_func(arg):
    arg = quote_spaces(arg)
    if not IS_WINDOWS:
        return arg
    # GCC requires double Windows slashes, let's use UNIX separator
    return WINPATHSEP_RE.sub(r"/\1", arg)


def long_sources_hook(env, sources):
    _sources = str(sources).replace("\\", "/")
    if len(str(_sources)) < MAX_LINE_LENGTH:
        return sources

    # fix space in paths
    data = []
    for line in _sources.split(".o "):
        line = line.strip()
        if not line.endswith(".o"):
            line += ".o"
        data.append('"%s"' % line)

    return '@"%s"' % _file_long_data(env, " ".join(data))


def _file_long_data(env, data):
    build_dir = env.subst("$BUILD_DIR")
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    tmp_file = os.path.join(
        build_dir, "longcmd-%s" % hashlib.md5(hashlib_encode_data(data)).hexdigest()
    )
    if os.path.isfile(tmp_file):
        return tmp_file
    with open(tmp_file, mode="w", encoding="utf8") as fp:
        fp.write(data)
    return tmp_file


def exists(env):
    return "compiledb" not in COMMAND_LINE_TARGETS and not env.IsIntegrationDump()


def generate(env):
    if not exists(env):
        return env
    kwargs = dict(
        _long_sources_hook=long_sources_hook,
        TEMPFILE=TempFileMunge,
        MAXLINELENGTH=MAX_LINE_LENGTH,
        TEMPFILEARGESCFUNC=tempfile_arg_esc_func,
        TEMPFILESUFFIX=".tmp",
        TEMPFILEDIR="$BUILD_DIR",
    )

    for name in ("LINKCOM", "ASCOM", "ASPPCOM", "CCCOM", "CXXCOM"):
        kwargs[name] = "${TEMPFILE('%s','$%sSTR')}" % (env.get(name), name)

    kwargs["ARCOM"] = env.get("ARCOM", "").replace(
        "$SOURCES", "${_long_sources_hook(__env__, SOURCES)}"
    )
    env.Replace(**kwargs)

    return env

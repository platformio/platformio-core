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
from hashlib import sha1
from os import walk
from os.path import abspath, dirname, expanduser, isdir, isfile, join

from platformio import __version__
from platformio.compat import PY2, WINDOWS
from platformio.project.config import ProjectConfig


def get_project_dir():
    return os.getcwd()


def is_platformio_project(project_dir=None):
    if not project_dir:
        project_dir = get_project_dir()
    return isfile(join(project_dir, "platformio.ini"))


def find_project_dir_above(path):
    if isfile(path):
        path = dirname(path)
    if is_platformio_project(path):
        return path
    if isdir(dirname(path)):
        return find_project_dir_above(dirname(path))
    return None


def get_project_optional_dir(name, default=None):
    paths = None

    # check for system environment variable
    var_name = "PLATFORMIO_%s" % name.upper()
    if var_name in os.environ:
        paths = os.getenv(var_name)

    config = ProjectConfig.get_instance(
        join(get_project_dir(), "platformio.ini"))
    if (config.has_section("platformio")
            and config.has_option("platformio", name)):
        paths = config.get("platformio", name)

    if not paths:
        return default

    items = []
    for item in paths.split(", "):
        if item.startswith("~"):
            item = expanduser(item)
        items.append(abspath(item))
    paths = ", ".join(items)

    while "$PROJECT_HASH" in paths:
        project_dir = get_project_dir()
        paths = paths.replace(
            "$PROJECT_HASH",
            sha1(project_dir if PY2 else project_dir.encode()).hexdigest()
            [:10])

    return paths


def get_projectworkspace_dir():
    return get_project_optional_dir("workspace_dir",
                                    join(get_project_dir(), ".pio"))


def get_projectbuild_dir(force=False):
    path = get_project_optional_dir("build_dir",
                                    join(get_projectworkspace_dir(), "build"))
    try:
        if not isdir(path):
            os.makedirs(path)
    except Exception as e:  # pylint: disable=broad-except
        if not force:
            raise Exception(e)
    return path


def get_projectlib_dir():
    return get_project_optional_dir("lib_dir", join(get_project_dir(), "lib"))


def get_projectlibdeps_dir():
    return get_project_optional_dir("libdeps_dir",
                                    join(get_project_dir(), ".piolibdeps"))


def get_projectsrc_dir():
    return get_project_optional_dir("src_dir", join(get_project_dir(), "src"))


def get_projectinclude_dir():
    return get_project_optional_dir("include_dir",
                                    join(get_project_dir(), "include"))


def get_projecttest_dir():
    return get_project_optional_dir("test_dir", join(get_project_dir(),
                                                     "test"))


def get_projectboards_dir():
    return get_project_optional_dir("boards_dir",
                                    join(get_project_dir(), "boards"))


def get_projectdata_dir():
    return get_project_optional_dir("data_dir", join(get_project_dir(),
                                                     "data"))


def calculate_project_hash():
    check_suffixes = (".c", ".cc", ".cpp", ".h", ".hpp", ".s", ".S")
    chunks = [__version__]
    for d in (get_projectsrc_dir(), get_projectlib_dir()):
        if not isdir(d):
            continue
        for root, _, files in walk(d):
            for f in files:
                path = join(root, f)
                if path.endswith(check_suffixes):
                    chunks.append(path)
    chunks_to_str = ",".join(sorted(chunks))
    if WINDOWS:
        # Fix issue with useless project rebuilding for case insensitive FS.
        # A case of disk drive can differ...
        chunks_to_str = chunks_to_str.lower()
    return sha1(chunks_to_str if PY2 else chunks_to_str.encode()).hexdigest()

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

import json
import os
from hashlib import sha1
from os import walk
from os.path import (basename, dirname, expanduser, isdir, isfile, join,
                     realpath, splitdrive)

from click.testing import CliRunner

from platformio import __version__, exception
from platformio.compat import WINDOWS, hashlib_encode_data
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
    project_dir = get_project_dir()
    config = ProjectConfig.get_instance(join(project_dir, "platformio.ini"))
    optional_dir = config.get("platformio", name)

    if not optional_dir:
        return default

    if "$PROJECT_HASH" in optional_dir:
        optional_dir = optional_dir.replace(
            "$PROJECT_HASH", "%s-%s" %
            (basename(project_dir), sha1(
                hashlib_encode_data(project_dir)).hexdigest()[:10]))

    if optional_dir.startswith("~"):
        optional_dir = expanduser(optional_dir)

    return realpath(optional_dir)


def get_project_core_dir():
    default = join(expanduser("~"), ".platformio")
    core_dir = get_project_optional_dir(
        "core_dir", get_project_optional_dir("home_dir", default))
    win_core_dir = None
    if WINDOWS and core_dir == default:
        win_core_dir = splitdrive(core_dir)[0] + "\\.platformio"
        if isdir(win_core_dir):
            core_dir = win_core_dir

    if not isdir(core_dir):
        try:
            os.makedirs(core_dir)
        except OSError as e:
            if win_core_dir:
                os.makedirs(win_core_dir)
                core_dir = win_core_dir
            else:
                raise e

    assert isdir(core_dir)
    return core_dir


def get_project_global_lib_dir():
    return get_project_optional_dir("globallib_dir",
                                    join(get_project_core_dir(), "lib"))


def get_project_platforms_dir():
    return get_project_optional_dir("platforms_dir",
                                    join(get_project_core_dir(), "platforms"))


def get_project_packages_dir():
    return get_project_optional_dir("packages_dir",
                                    join(get_project_core_dir(), "packages"))


def get_project_cache_dir():
    return get_project_optional_dir("cache_dir",
                                    join(get_project_core_dir(), ".cache"))


def get_project_workspace_dir():
    return get_project_optional_dir("workspace_dir",
                                    join(get_project_dir(), ".pio"))


def get_project_build_dir(force=False):
    path = get_project_optional_dir("build_dir",
                                    join(get_project_workspace_dir(), "build"))
    try:
        if not isdir(path):
            os.makedirs(path)
    except Exception as e:  # pylint: disable=broad-except
        if not force:
            raise Exception(e)
    return path


def get_project_libdeps_dir():
    return get_project_optional_dir(
        "libdeps_dir", join(get_project_workspace_dir(), "libdeps"))


def get_project_lib_dir():
    return get_project_optional_dir("lib_dir", join(get_project_dir(), "lib"))


def get_project_include_dir():
    return get_project_optional_dir("include_dir",
                                    join(get_project_dir(), "include"))


def get_project_src_dir():
    return get_project_optional_dir("src_dir", join(get_project_dir(), "src"))


def get_project_test_dir():
    return get_project_optional_dir("test_dir", join(get_project_dir(),
                                                     "test"))


def get_project_boards_dir():
    return get_project_optional_dir("boards_dir",
                                    join(get_project_dir(), "boards"))


def get_project_data_dir():
    return get_project_optional_dir("data_dir", join(get_project_dir(),
                                                     "data"))


def get_project_shared_dir():
    return get_project_optional_dir("shared_dir",
                                    join(get_project_dir(), "shared"))


def calculate_project_hash():
    check_suffixes = (".c", ".cc", ".cpp", ".h", ".hpp", ".s", ".S")
    chunks = [__version__]
    for d in (get_project_src_dir(), get_project_lib_dir()):
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
    return sha1(hashlib_encode_data(chunks_to_str)).hexdigest()


def load_project_ide_data(project_dir, env_name):
    from platformio.commands.run import cli as cmd_run
    result = CliRunner().invoke(cmd_run, [
        "--project-dir", project_dir, "--environment", env_name, "--target",
        "idedata"
    ])
    if result.exit_code != 0 and not isinstance(result.exception,
                                                exception.ReturnErrorCode):
        raise result.exception
    if '"includes":' not in result.output:
        raise exception.PlatformioException(result.output)

    for line in result.output.split("\n"):
        line = line.strip()
        if line.startswith('{"') and line.endswith("}"):
            return json.loads(line)
    return None

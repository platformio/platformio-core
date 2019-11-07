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
from os.path import dirname, isdir, isfile, join

from click.testing import CliRunner

from platformio import __version__, exception, fs
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


def get_project_core_dir():
    """ Deprecated, use ProjectConfig.get_optional_dir("core") instead """
    return ProjectConfig.get_instance(
        join(get_project_dir(), "platformio.ini")
    ).get_optional_dir("core", exists=True)


def get_project_cache_dir():
    """ Deprecated, use ProjectConfig.get_optional_dir("cache") instead """
    return ProjectConfig.get_instance(
        join(get_project_dir(), "platformio.ini")
    ).get_optional_dir("cache")


def get_project_global_lib_dir():
    """
    Deprecated, use ProjectConfig.get_optional_dir("globallib") instead
    "platformio-node-helpers" depends on it
    """
    return ProjectConfig.get_instance(
        join(get_project_dir(), "platformio.ini")
    ).get_optional_dir("globallib")


def get_project_lib_dir():
    """
    Deprecated, use ProjectConfig.get_optional_dir("lib") instead
    "platformio-node-helpers" depends on it
    """
    return ProjectConfig.get_instance(
        join(get_project_dir(), "platformio.ini")
    ).get_optional_dir("lib")


def get_project_libdeps_dir():
    """
    Deprecated, use ProjectConfig.get_optional_dir("libdeps") instead
    "platformio-node-helpers" depends on it
    """
    return ProjectConfig.get_instance(
        join(get_project_dir(), "platformio.ini")
    ).get_optional_dir("libdeps")


def get_default_projects_dir():
    docs_dir = join(fs.expanduser("~"), "Documents")
    try:
        assert WINDOWS
        import ctypes.wintypes  # pylint: disable=import-outside-toplevel

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        docs_dir = buf.value
    except:  # pylint: disable=bare-except
        pass
    return join(docs_dir, "PlatformIO", "Projects")


def compute_project_checksum(config):
    # rebuild when PIO Core version changes
    checksum = sha1(hashlib_encode_data(__version__))

    # configuration file state
    checksum.update(hashlib_encode_data(config.to_json()))

    # project file structure
    check_suffixes = (".c", ".cc", ".cpp", ".h", ".hpp", ".s", ".S")
    for d in (
        config.get_optional_dir("include"),
        config.get_optional_dir("src"),
        config.get_optional_dir("lib"),
    ):
        if not isdir(d):
            continue
        chunks = []
        for root, _, files in walk(d):
            for f in files:
                path = join(root, f)
                if path.endswith(check_suffixes):
                    chunks.append(path)
        if not chunks:
            continue
        chunks_to_str = ",".join(sorted(chunks))
        if WINDOWS:  # case insensitive OS
            chunks_to_str = chunks_to_str.lower()
        checksum.update(hashlib_encode_data(chunks_to_str))

    return checksum.hexdigest()


def load_project_ide_data(project_dir, env_or_envs):
    # pylint: disable=import-outside-toplevel
    from platformio.commands.run.command import cli as cmd_run

    assert env_or_envs
    envs = env_or_envs
    if not isinstance(envs, list):
        envs = [envs]
    args = ["--project-dir", project_dir, "--target", "idedata"]
    for env in envs:
        args.extend(["-e", env])
    result = CliRunner().invoke(cmd_run, args)
    if result.exit_code != 0 and not isinstance(
        result.exception, exception.ReturnErrorCode
    ):
        raise result.exception
    if '"includes":' not in result.output:
        raise exception.PlatformioException(result.output)

    data = {}
    for line in result.output.split("\n"):
        line = line.strip()
        if line.startswith('{"') and line.endswith("}") and "env_name" in line:
            _data = json.loads(line)
            if "env_name" in _data:
                data[_data["env_name"]] = _data
    if not isinstance(env_or_envs, list) and env_or_envs in data:
        return data[env_or_envs]
    return data or None

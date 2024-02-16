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
import re
import subprocess
from hashlib import sha1

from click.testing import CliRunner

from platformio import __version__, exception, fs
from platformio.compat import IS_MACOS, IS_WINDOWS, hashlib_encode_data
from platformio.project.config import ProjectConfig


def get_project_dir():
    return os.getcwd()


def is_platformio_project(project_dir=None):
    if not project_dir:
        project_dir = get_project_dir()
    return os.path.isfile(os.path.join(project_dir, "platformio.ini"))


def find_project_dir_above(path):
    if os.path.isfile(path):
        path = os.path.dirname(path)
    if is_platformio_project(path):
        return path
    if os.path.isdir(os.path.dirname(path)):
        return find_project_dir_above(os.path.dirname(path))
    return None


def get_project_watch_lib_dirs():
    """Used by platformio-node-helpers.project.observer.fetchLibDirs"""
    config = ProjectConfig.get_instance()
    result = [
        config.get("platformio", "globallib_dir"),
        config.get("platformio", "lib_dir"),
    ]
    libdeps_dir = config.get("platformio", "libdeps_dir")
    if not os.path.isdir(libdeps_dir):
        return result
    for d in os.listdir(libdeps_dir):
        if os.path.isdir(os.path.join(libdeps_dir, d)):
            result.append(os.path.join(libdeps_dir, d))
    return result


get_project_all_lib_dirs = get_project_watch_lib_dirs


def get_project_cache_dir():
    """Deprecated, use ProjectConfig.get("platformio", "cache_dir") instead"""
    return ProjectConfig.get_instance().get("platformio", "cache_dir")


def get_default_projects_dir():
    docs_dir = os.path.join(fs.expanduser("~"), "Documents")
    try:
        assert IS_WINDOWS
        import ctypes.wintypes  # pylint: disable=import-outside-toplevel

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        docs_dir = buf.value
    except:  # pylint: disable=bare-except
        if not IS_MACOS:
            try:
                docs_dir = (
                    subprocess.check_output(["xdg-user-dir", "DOCUMENTS"])
                    .decode("utf-8")
                    .strip()
                )
            except FileNotFoundError:  # command not found
                pass
    return os.path.join(docs_dir, "PlatformIO", "Projects")


def compute_project_checksum(config):
    # rebuild when PIO Core version changes
    checksum = sha1(hashlib_encode_data(__version__))

    # configuration file state
    config_data = config.to_json()
    if IS_WINDOWS:
        # issue #4600: fix drive letter
        config_data = re.sub(
            r"([A-Z]):\\",
            lambda match: "%s:\\" % match.group(1).lower(),
            config_data,
            flags=re.I,
        )
    checksum.update(hashlib_encode_data(config_data))

    # project file structure
    check_suffixes = (".c", ".cc", ".cpp", ".h", ".hpp", ".s", ".S")
    for d in (
        config.get("platformio", "include_dir"),
        config.get("platformio", "src_dir"),
        config.get("platformio", "lib_dir"),
    ):
        if not os.path.isdir(d):
            continue
        chunks = []
        for root, _, files in os.walk(d):
            for f in files:
                path = os.path.join(root, f)
                if path.endswith(check_suffixes):
                    chunks.append(path)
        if not chunks:
            continue
        chunks_to_str = ",".join(sorted(chunks))
        if IS_WINDOWS:  # case insensitive OS
            chunks_to_str = chunks_to_str.lower()
        checksum.update(hashlib_encode_data(chunks_to_str))

    return checksum.hexdigest()


def load_build_metadata(project_dir, env_or_envs, cache=False, build_type=None):
    assert env_or_envs
    env_names = env_or_envs
    if not isinstance(env_names, list):
        env_names = [env_names]

    with fs.cd(project_dir):
        result = _get_cached_build_metadata(env_names) if cache else {}
        # incompatible build-type data
        for env_name in list(result.keys()):
            if build_type is None:
                build_type = ProjectConfig.get_instance().get(
                    f"env:{env_name}", "build_type"
                )
            if result[env_name].get("build_type", "") != build_type:
                del result[env_name]
        missed_env_names = set(env_names) - set(result.keys())
        if missed_env_names:
            result.update(
                _load_build_metadata(project_dir, missed_env_names, build_type)
            )

    if not isinstance(env_or_envs, list) and env_or_envs in result:
        return result[env_or_envs]
    return result or None


# Backward compatibiility with dev-platforms
load_project_ide_data = load_build_metadata


def _load_build_metadata(project_dir, env_names, build_type=None):
    # pylint: disable=import-outside-toplevel
    from platformio import app
    from platformio.run.cli import cli as cmd_run

    args = ["--project-dir", project_dir, "--target", "__idedata"]
    if build_type == "debug":
        args.extend(["--target", "__debug"])
    # if build_type == "test":
    #     args.extend(["--target", "__test"])
    for name in env_names:
        args.extend(["-e", name])
    app.set_session_var("pause_telemetry", True)
    result = CliRunner().invoke(cmd_run, args)
    app.set_session_var("pause_telemetry", False)
    if result.exit_code != 0 and not isinstance(
        result.exception, exception.ReturnErrorCode
    ):
        raise result.exception
    if '"includes":' not in result.output:
        raise exception.UserSideException(result.output)
    return _get_cached_build_metadata(env_names)


def _get_cached_build_metadata(env_names):
    build_dir = ProjectConfig.get_instance().get("platformio", "build_dir")
    result = {}
    for env_name in env_names:
        if not os.path.isfile(os.path.join(build_dir, env_name, "idedata.json")):
            continue
        result[env_name] = fs.load_json(
            os.path.join(build_dir, env_name, "idedata.json")
        )
    return result

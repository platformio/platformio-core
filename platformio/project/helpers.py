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
import subprocess
from hashlib import sha1

from click.testing import CliRunner

from platformio import __version__, exception, fs
from platformio.compat import IS_MACOS, IS_WINDOWS, hashlib_encode_data
from platformio.project.config import ProjectConfig


def get_project_dir():
    return os.getcwd()


def get_project_id(project_dir=None):
    return hashlib.sha1(
        hashlib_encode_data(project_dir or get_project_dir())
    ).hexdigest()


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


def get_build_type(config, env, run_targets=None):
    types = []
    run_targets = run_targets or []
    declared_build_type = config.get(f"env:{env}", "build_type")
    if (
        set(["__debug", "__memusage"]) & set(run_targets)
        or declared_build_type == "debug"
    ):
        types.append("debug")
    if "__test" in run_targets or declared_build_type == "test":
        types.append("test")
    return "+".join(types or ["release"])


def load_build_metadata(project_dir, env_or_envs, cache=False, debug=False, test=False):
    assert env_or_envs
    envs = env_or_envs
    if not isinstance(envs, list):
        envs = [envs]
    run_targets = []
    if debug:
        run_targets.append("__debug")
    if test:
        run_targets.append("__test")

    with fs.cd(project_dir or os.getcwd()):
        result = _get_cached_build_metadata(envs, run_targets) if cache else {}
        missed_envs = set(envs) - set(result.keys())
        if missed_envs:
            result.update(_load_build_metadata(missed_envs, run_targets))

    if not isinstance(env_or_envs, list) and env_or_envs in result:
        return result[env_or_envs]
    return result or None


# Backward compatibiility with dev-platforms
load_project_ide_data = load_build_metadata


def _get_cached_build_metadata(envs, run_targets=None):
    config = ProjectConfig.get_instance(os.path.join(os.getcwd(), "platformio.ini"))
    build_dir = config.get("platformio", "build_dir")
    result = {}
    for env in envs:
        build_type = get_build_type(config, env, run_targets)
        json_path = os.path.join(build_dir, env, build_type, "metadata.json")
        if os.path.isfile(json_path):
            result[env] = fs.load_json(json_path)
    return result


def _load_build_metadata(envs, run_targets=None):
    # pylint: disable=import-outside-toplevel
    from platformio import app
    from platformio.run.cli import cli as cmd_run

    args = ["--target", "__metadata"]
    for target in run_targets or []:
        args.extend(["--target", target])
    for env in envs:
        args.extend(["-e", env])
    app.set_session_var("pause_telemetry", True)
    result = CliRunner().invoke(cmd_run, args)
    app.set_session_var("pause_telemetry", False)
    if result.exit_code != 0 and not isinstance(
        result.exception, exception.ReturnErrorCode
    ):
        raise result.exception
    if "Metadata has been saved to the following location" not in result.output:
        raise exception.UserSideException(result.output)
    return _get_cached_build_metadata(envs, run_targets)

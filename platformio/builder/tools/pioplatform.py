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
import sys

from SCons.Script import ARGUMENTS  # pylint: disable=import-error
from SCons.Script import COMMAND_LINE_TARGETS  # pylint: disable=import-error
from SCons.Script import DefaultEnvironment  # pylint: disable=import-error

from platformio import fs, util
from platformio.compat import IS_MACOS, IS_WINDOWS
from platformio.package.meta import PackageItem
from platformio.package.version import get_original_version
from platformio.platform.exception import UnknownBoard
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectOptions

# pylint: disable=too-many-branches, too-many-locals


@util.memoized()
def _PioPlatform():
    env = DefaultEnvironment()
    return PlatformFactory.from_env(env["PIOENV"], targets=COMMAND_LINE_TARGETS)


def PioPlatform(_):
    return _PioPlatform()


def BoardConfig(env, board=None):
    with fs.cd(env.subst("$PROJECT_DIR")):
        try:
            p = env.PioPlatform()
            board = board or env.get("BOARD")
            assert board, "BoardConfig: Board is not defined"
            return p.board_config(board)
        except (AssertionError, UnknownBoard) as exc:
            sys.stderr.write("Error: %s\n" % str(exc))
            env.Exit(1)
    return None


def GetFrameworkScript(env, framework):
    p = env.PioPlatform()
    assert p.frameworks and framework in p.frameworks
    script_path = env.subst(p.frameworks[framework]["script"])
    if not os.path.isfile(script_path):
        script_path = os.path.join(p.get_dir(), script_path)
    return script_path


def LoadPioPlatform(env):
    p = env.PioPlatform()

    # Ensure real platform name
    env["PIOPLATFORM"] = p.name

    # Add toolchains and uploaders to $PATH and $*_LIBRARY_PATH
    for pkg in p.get_installed_packages():
        type_ = p.get_package_type(pkg.metadata.name)
        if type_ not in ("toolchain", "uploader", "debugger"):
            continue
        env.PrependENVPath(
            "PATH",
            (
                os.path.join(pkg.path, "bin")
                if os.path.isdir(os.path.join(pkg.path, "bin"))
                else pkg.path
            ),
        )
        if (
            not IS_WINDOWS
            and os.path.isdir(os.path.join(pkg.path, "lib"))
            and type_ != "toolchain"
        ):
            env.PrependENVPath(
                "DYLD_LIBRARY_PATH" if IS_MACOS else "LD_LIBRARY_PATH",
                os.path.join(pkg.path, "lib"),
            )

    # Platform specific LD Scripts
    if os.path.isdir(os.path.join(p.get_dir(), "ldscripts")):
        env.Prepend(LIBPATH=[os.path.join(p.get_dir(), "ldscripts")])

    if "BOARD" not in env:
        return

    # update board manifest with overridden data from INI config
    board_config = env.BoardConfig()
    for option, value in env.GetProjectOptions():
        if not option.startswith("board_"):
            continue
        option = option.lower()[6:]
        try:
            if isinstance(board_config.get(option), bool):
                value = str(value).lower() in ("1", "yes", "true")
            elif isinstance(board_config.get(option), int):
                value = int(value)
        except KeyError:
            pass
        board_config.update(option, value)

    # load default variables from board config
    for option_meta in ProjectOptions.values():
        if not option_meta.buildenvvar or option_meta.buildenvvar in env:
            continue
        data_path = (
            option_meta.name[6:]
            if option_meta.name.startswith("board_")
            else option_meta.name.replace("_", ".")
        )
        try:
            env[option_meta.buildenvvar] = board_config.get(data_path)
        except KeyError:
            pass

    if "build.ldscript" in board_config:
        env.Replace(LDSCRIPT_PATH=board_config.get("build.ldscript"))


def PrintConfiguration(env):  # pylint: disable=too-many-statements
    platform = env.PioPlatform()
    pkg_metadata = PackageItem(platform.get_dir()).metadata
    board_config = env.BoardConfig() if "BOARD" in env else None

    def _get_configuration_data():
        return (
            None
            if not board_config
            else [
                "CONFIGURATION:",
                "https://docs.platformio.org/page/boards/%s/%s.html"
                % (platform.name, board_config.id),
            ]
        )

    def _get_plaform_data():
        data = [
            "PLATFORM: %s (%s)"
            % (
                platform.title,
                pkg_metadata.version if pkg_metadata else platform.version,
            )
        ]
        if (
            int(ARGUMENTS.get("PIOVERBOSE", 0))
            and pkg_metadata
            and pkg_metadata.spec.external
        ):
            data.append("(%s)" % pkg_metadata.spec.uri)
        if board_config:
            data.extend([">", board_config.get("name")])
        return data

    def _get_hardware_data():
        data = ["HARDWARE:"]
        mcu = env.subst("$BOARD_MCU")
        f_cpu = env.subst("$BOARD_F_CPU")
        if mcu:
            data.append(mcu.upper())
        if f_cpu:
            f_cpu = int("".join([c for c in str(f_cpu) if c.isdigit()]))
            data.append("%dMHz," % (f_cpu / 1000000))
        if not board_config:
            return data
        ram = board_config.get("upload", {}).get("maximum_ram_size")
        flash = board_config.get("upload", {}).get("maximum_size")
        data.append(
            "%s RAM, %s Flash"
            % (fs.humanize_file_size(ram), fs.humanize_file_size(flash))
        )
        return data

    def _get_debug_data():
        debug_tools = (
            board_config.get("debug", {}).get("tools") if board_config else None
        )
        if not debug_tools:
            return None
        data = [
            "DEBUG:",
            "Current",
            "(%s)"
            % board_config.get_debug_tool_name(env.GetProjectOption("debug_tool")),
        ]
        onboard = []
        external = []
        for key, value in debug_tools.items():
            if value.get("onboard"):
                onboard.append(key)
            else:
                external.append(key)
        if onboard:
            data.extend(["On-board", "(%s)" % ", ".join(sorted(onboard))])
        if external:
            data.extend(["External", "(%s)" % ", ".join(sorted(external))])
        return data

    def _get_packages_data():
        data = []
        for item in platform.dump_used_packages():
            original_version = get_original_version(item["version"])
            info = "%s @ %s" % (item["name"], item["version"])
            extra = []
            if original_version:
                extra.append(original_version)
            if "src_url" in item and int(ARGUMENTS.get("PIOVERBOSE", 0)):
                extra.append(item["src_url"])
            if extra:
                info += " (%s)" % ", ".join(extra)
            data.append(info)
        if not data:
            return None
        return ["PACKAGES:"] + ["\n - %s" % d for d in sorted(data)]

    for data in (
        _get_configuration_data(),
        _get_plaform_data(),
        _get_hardware_data(),
        _get_debug_data(),
        _get_packages_data(),
    ):
        if data and len(data) > 1:
            print(" ".join(data))


def exists(_):
    return True


def generate(env):
    env.AddMethod(PioPlatform)
    env.AddMethod(BoardConfig)
    env.AddMethod(GetFrameworkScript)
    env.AddMethod(LoadPioPlatform)
    env.AddMethod(PrintConfiguration)
    return env

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

from __future__ import absolute_import

import base64
import sys
from os.path import isdir, isfile, join

from SCons.Script import COMMAND_LINE_TARGETS

from platformio import exception, util
from platformio.managers.platform import PlatformFactory

# pylint: disable=too-many-branches, too-many-locals


@util.memoized()
def initPioPlatform(name):
    return PlatformFactory.newPlatform(name)


def PioPlatform(env):
    variables = {}
    for name in env['PIOVARIABLES']:
        if name in env:
            variables[name.lower()] = env[name]
    p = initPioPlatform(env['PLATFORM_MANIFEST'])
    p.configure_default_packages(variables, COMMAND_LINE_TARGETS)
    return p


def BoardConfig(env, board=None):
    p = initPioPlatform(env['PLATFORM_MANIFEST'])
    try:
        board = board or env.get("BOARD")
        assert board, "BoardConfig: Board is not defined"
        config = p.board_config(board)
    except (AssertionError, exception.UnknownBoard) as e:
        sys.stderr.write("Error: %s\n" % str(e))
        env.Exit(1)
    return config


def GetFrameworkScript(env, framework):
    p = env.PioPlatform()
    assert p.frameworks and framework in p.frameworks
    script_path = env.subst(p.frameworks[framework]['script'])
    if not isfile(script_path):
        script_path = join(p.get_dir(), script_path)
    return script_path


def LoadPioPlatform(env, variables):
    p = env.PioPlatform()
    installed_packages = p.get_installed_packages()

    # Ensure real platform name
    env['PIOPLATFORM'] = p.name

    # Add toolchains and uploaders to $PATH and $*_LIBRARY_PATH
    systype = util.get_systype()
    for name in installed_packages:
        type_ = p.get_package_type(name)
        if type_ not in ("toolchain", "uploader", "debugger"):
            continue
        pkg_dir = p.get_package_dir(name)
        env.PrependENVPath(
            "PATH",
            join(pkg_dir, "bin") if isdir(join(pkg_dir, "bin")) else pkg_dir)
        if ("windows" not in systype and isdir(join(pkg_dir, "lib"))
                and type_ != "toolchain"):
            env.PrependENVPath(
                "DYLD_LIBRARY_PATH"
                if "darwin" in systype else "LD_LIBRARY_PATH",
                join(pkg_dir, "lib"))

    # Platform specific LD Scripts
    if isdir(join(p.get_dir(), "ldscripts")):
        env.Prepend(LIBPATH=[join(p.get_dir(), "ldscripts")])

    if "BOARD" not in env:
        # handle _MCU and _F_CPU variables for AVR native
        for key, value in variables.UnknownVariables().items():
            if not key.startswith("BOARD_"):
                continue
            env.Replace(
                **{key.upper().replace("BUILD.", ""): base64.b64decode(value)})
        return

    # update board manifest with a custom data
    board_config = env.BoardConfig()
    for key, value in variables.UnknownVariables().items():
        if not key.startswith("BOARD_"):
            continue
        board_config.update(key.lower()[6:], base64.b64decode(value))

    # update default environment variables
    for key in variables.keys():
        if key in env or \
                not any([key.startswith("BOARD_"), key.startswith("UPLOAD_")]):
            continue
        _opt, _val = key.lower().split("_", 1)
        if _opt == "board":
            _opt = "build"
        if _val in board_config.get(_opt):
            env.Replace(**{key: board_config.get("%s.%s" % (_opt, _val))})

    if "build.ldscript" in board_config:
        env.Replace(LDSCRIPT_PATH=board_config.get("build.ldscript"))


def PrintConfiguration(env):
    platform = env.PioPlatform()
    platform_data = ["PLATFORM: %s >" % platform.title]
    hardware_data = ["HARDWARE:"]
    configuration_data = ["CONFIGURATION:"]
    mcu = env.subst("$BOARD_MCU")
    f_cpu = env.subst("$BOARD_F_CPU")
    if mcu:
        hardware_data.append(mcu.upper())
    if f_cpu:
        f_cpu = int("".join([c for c in str(f_cpu) if c.isdigit()]))
        hardware_data.append("%dMHz" % (f_cpu / 1000000))

    debug_tools = None
    if "BOARD" in env:
        board_config = env.BoardConfig()
        platform_data.append(board_config.get("name"))

        debug_tools = board_config.get("debug", {}).get("tools")
        ram = board_config.get("upload", {}).get("maximum_ram_size")
        flash = board_config.get("upload", {}).get("maximum_size")
        hardware_data.append(
            "%s RAM (%s Flash)" % (util.format_filesize(ram),
                                   util.format_filesize(flash)))
        configuration_data.append(
            "https://docs.platformio.org/page/boards/%s/%s.html" %
            (platform.name, board_config.id))

    for data in (configuration_data, platform_data, hardware_data):
        if len(data) > 1:
            print(" ".join(data))

    # Debugging
    if not debug_tools:
        return

    data = [
        "CURRENT(%s)" % board_config.get_debug_tool_name(
            env.subst("$DEBUG_TOOL"))
    ]
    onboard = []
    external = []
    for key, value in debug_tools.items():
        if value.get("onboard"):
            onboard.append(key)
        else:
            external.append(key)
    if onboard:
        data.append("ON-BOARD(%s)" % ", ".join(sorted(onboard)))
    if external:
        data.append("EXTERNAL(%s)" % ", ".join(sorted(external)))

    print("DEBUG: %s" % " ".join(data))


def exists(_):
    return True


def generate(env):
    env.AddMethod(PioPlatform)
    env.AddMethod(BoardConfig)
    env.AddMethod(GetFrameworkScript)
    env.AddMethod(LoadPioPlatform)
    env.AddMethod(PrintConfiguration)
    return env

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


import glob
import os

import SCons.Defaults  # pylint: disable=import-error
import SCons.Subst  # pylint: disable=import-error
from SCons.Script import COMMAND_LINE_TARGETS  # pylint: disable=import-error

from platformio.proc import exec_command, where_is_program


def IsIntegrationDump(_):
    return set(["__idedata", "idedata"]) & set(COMMAND_LINE_TARGETS)


def DumpIntegrationIncludes(env):
    result = dict(build=[], compatlib=[], toolchain=[])

    result["build"].extend(
        [
            env.subst("$PROJECT_INCLUDE_DIR"),
            env.subst("$PROJECT_SRC_DIR"),
        ]
    )
    result["build"].extend(
        [os.path.abspath(env.subst(item)) for item in env.get("CPPPATH", [])]
    )

    # installed libs
    for lb in env.GetLibBuilders():
        result["compatlib"].extend(
            [os.path.abspath(inc) for inc in lb.get_include_dirs()]
        )

    # includes from toolchains
    p = env.PioPlatform()
    for pkg in p.get_installed_packages(with_optional=False):
        if p.get_package_type(pkg.metadata.name) != "toolchain":
            continue
        toolchain_dir = glob.escape(pkg.path)
        toolchain_incglobs = [
            os.path.join(toolchain_dir, "*", "include", "c++", "*"),
            os.path.join(toolchain_dir, "*", "include", "c++", "*", "*-*-*"),
            os.path.join(toolchain_dir, "lib", "gcc", "*", "*", "include*"),
            os.path.join(toolchain_dir, "*", "include*"),
        ]
        for g in toolchain_incglobs:
            result["toolchain"].extend([os.path.abspath(inc) for inc in glob.glob(g)])

    return result


def get_gcc_defines(env):
    items = []
    try:
        sysenv = os.environ.copy()
        sysenv["PATH"] = str(env["ENV"]["PATH"])
        result = exec_command(
            "echo | %s -dM -E -" % env.subst("$CC"), env=sysenv, shell=True
        )
    except OSError:
        return items
    if result["returncode"] != 0:
        return items
    for line in result["out"].split("\n"):
        tokens = line.strip().split(" ", 2)
        if not tokens or tokens[0] != "#define":
            continue
        if len(tokens) > 2:
            items.append("%s=%s" % (tokens[1], tokens[2]))
        else:
            items.append(tokens[1])
    return items


def dump_defines(env):
    defines = []
    # global symbols
    for item in SCons.Defaults.processDefines(env.get("CPPDEFINES", [])):
        item = item.strip()
        if item:
            defines.append(env.subst(item).replace('\\"', '"'))

    # special symbol for Atmel AVR MCU
    if env["PIOPLATFORM"] == "atmelavr":
        board_mcu = env.get("BOARD_MCU")
        if not board_mcu and "BOARD" in env:
            board_mcu = env.BoardConfig().get("build.mcu")
        if board_mcu:
            defines.append(
                str(
                    "__AVR_%s__"
                    % board_mcu.upper()
                    .replace("ATMEGA", "ATmega")
                    .replace("ATTINY", "ATtiny")
                )
            )

    # built-in GCC marcos
    # if env.GetCompilerType() == "gcc":
    #     defines.extend(get_gcc_defines(env))

    return defines


def dump_svd_path(env):
    svd_path = env.GetProjectOption("debug_svd_path")
    if svd_path:
        return os.path.abspath(svd_path)

    if "BOARD" not in env:
        return None
    try:
        svd_path = env.BoardConfig().get("debug.svd_path")
        assert svd_path
    except (AssertionError, KeyError):
        return None
    # custom path to SVD file
    if os.path.isfile(svd_path):
        return svd_path
    # default file from ./platform/misc/svd folder
    p = env.PioPlatform()
    if os.path.isfile(os.path.join(p.get_dir(), "misc", "svd", svd_path)):
        return os.path.abspath(os.path.join(p.get_dir(), "misc", "svd", svd_path))
    return None


def _subst_cmd(env, cmd):
    args = env.subst_list(cmd, SCons.Subst.SUBST_CMD)[0]
    return " ".join([SCons.Subst.quote_spaces(arg) for arg in args])


def DumpIntegrationData(*args):
    projenv, globalenv = args[0:2]  # pylint: disable=unbalanced-tuple-unpacking
    data = {
        "build_type": globalenv.GetBuildType(),
        "env_name": globalenv["PIOENV"],
        "libsource_dirs": [
            globalenv.subst(item) for item in globalenv.GetLibSourceDirs()
        ],
        "defines": dump_defines(projenv),
        "includes": projenv.DumpIntegrationIncludes(),
        "cc_flags": _subst_cmd(projenv, "$CFLAGS $CCFLAGS $CPPFLAGS"),
        "cxx_flags": _subst_cmd(projenv, "$CXXFLAGS $CCFLAGS $CPPFLAGS"),
        "cc_path": where_is_program(
            globalenv.subst("$CC"), globalenv.subst("${ENV['PATH']}")
        ),
        "cxx_path": where_is_program(
            globalenv.subst("$CXX"), globalenv.subst("${ENV['PATH']}")
        ),
        "gdb_path": where_is_program(
            globalenv.subst("$GDB"), globalenv.subst("${ENV['PATH']}")
        ),
        "prog_path": globalenv.subst("$PROGPATH"),
        "svd_path": dump_svd_path(globalenv),
        "compiler_type": globalenv.GetCompilerType(),
        "targets": globalenv.DumpTargets(),
        "extra": dict(
            flash_images=[
                {"offset": item[0], "path": globalenv.subst(item[1])}
                for item in globalenv.get("FLASH_EXTRA_IMAGES", [])
            ]
        ),
    }
    for key in ("IDE_EXTRA_DATA", "INTEGRATION_EXTRA_DATA"):
        data["extra"].update(globalenv.get(key, {}))
    return data


def exists(_):
    return True


def generate(env):
    env["IDE_EXTRA_DATA"] = {}  # legacy support
    env["INTEGRATION_EXTRA_DATA"] = {}
    env.AddMethod(IsIntegrationDump)
    env.AddMethod(DumpIntegrationIncludes)
    env.AddMethod(DumpIntegrationData)
    return env

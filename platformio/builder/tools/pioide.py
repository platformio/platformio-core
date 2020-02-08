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

import os
from glob import glob

from SCons.Defaults import processDefines  # pylint: disable=import-error

from platformio.compat import glob_escape
from platformio.managers.core import get_core_package_dir
from platformio.proc import exec_command, where_is_program


def _dump_includes(env):
    includes = []

    for item in env.get("CPPPATH", []):
        includes.append(env.subst(item))

    # installed libs
    for lb in env.GetLibBuilders():
        includes.extend(lb.get_include_dirs())

    # includes from toolchains
    p = env.PioPlatform()
    for name in p.get_installed_packages():
        if p.get_package_type(name) != "toolchain":
            continue
        toolchain_dir = glob_escape(p.get_package_dir(name))
        toolchain_incglobs = [
            os.path.join(toolchain_dir, "*", "include*"),
            os.path.join(toolchain_dir, "*", "include", "c++", "*"),
            os.path.join(toolchain_dir, "*", "include", "c++", "*", "*-*-*"),
            os.path.join(toolchain_dir, "lib", "gcc", "*", "*", "include*"),
        ]
        for g in toolchain_incglobs:
            includes.extend(glob(g))

    unity_dir = get_core_package_dir("tool-unity")
    if unity_dir:
        includes.append(unity_dir)

    includes.extend([env.subst("$PROJECT_INCLUDE_DIR"), env.subst("$PROJECT_SRC_DIR")])

    # remove duplicates
    result = []
    for item in includes:
        item = os.path.realpath(item)
        if item not in result:
            result.append(item)

    return result


def _get_gcc_defines(env):
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


def _dump_defines(env):
    defines = []
    # global symbols
    for item in processDefines(env.get("CPPDEFINES", [])):
        defines.append(env.subst(item).replace("\\", ""))

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
    #     defines.extend(_get_gcc_defines(env))

    return defines


def _get_svd_path(env):
    svd_path = env.GetProjectOption("debug_svd_path")
    if svd_path:
        return os.path.realpath(svd_path)

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
        return os.path.realpath(os.path.join(p.get_dir(), "misc", "svd", svd_path))
    return None


def _escape_build_flag(flags):
    return [flag if " " not in flag else '"%s"' % flag for flag in flags]


def DumpIDEData(env):

    env["__escape_build_flag"] = _escape_build_flag

    LINTCCOM = (
        "${__escape_build_flag(CFLAGS)} ${__escape_build_flag(CCFLAGS)} $CPPFLAGS"
    )
    LINTCXXCOM = (
        "${__escape_build_flag(CXXFLAGS)} ${__escape_build_flag(CCFLAGS)} $CPPFLAGS"
    )

    data = {
        "env_name": env["PIOENV"],
        "libsource_dirs": [env.subst(l) for l in env.GetLibSourceDirs()],
        "defines": _dump_defines(env),
        "includes": _dump_includes(env),
        "cc_flags": env.subst(LINTCCOM),
        "cxx_flags": env.subst(LINTCXXCOM),
        "cc_path": where_is_program(env.subst("$CC"), env.subst("${ENV['PATH']}")),
        "cxx_path": where_is_program(env.subst("$CXX"), env.subst("${ENV['PATH']}")),
        "gdb_path": where_is_program(env.subst("$GDB"), env.subst("${ENV['PATH']}")),
        "prog_path": env.subst("$PROG_PATH"),
        "flash_extra_images": [
            {"offset": item[0], "path": env.subst(item[1])}
            for item in env.get("FLASH_EXTRA_IMAGES", [])
        ],
        "svd_path": _get_svd_path(env),
        "compiler_type": env.GetCompilerType(),
    }

    env_ = env.Clone()
    # https://github.com/platformio/platformio-atom-ide/issues/34
    _new_defines = []
    for item in processDefines(env_.get("CPPDEFINES", [])):
        item = item.replace('\\"', '"')
        if " " in item:
            _new_defines.append(item.replace(" ", "\\\\ "))
        else:
            _new_defines.append(item)
    env_.Replace(CPPDEFINES=_new_defines)

    data.update({"cc_flags": env_.subst(LINTCCOM), "cxx_flags": env_.subst(LINTCXXCOM)})

    return data


def exists(_):
    return True


def generate(env):
    env.AddMethod(DumpIDEData)
    return env

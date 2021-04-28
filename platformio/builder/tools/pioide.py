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

import glob
import os

import SCons.Defaults  # pylint: disable=import-error
import SCons.Subst  # pylint: disable=import-error

from platformio.package.manager.core import get_core_package_dir
from platformio.proc import exec_command, where_is_program


def _dump_includes(env):
    includes = {}

    includes["build"] = [
        env.subst("$PROJECT_INCLUDE_DIR"),
        env.subst("$PROJECT_SRC_DIR"),
    ]
    includes["build"].extend(
        [os.path.realpath(env.subst(item)) for item in env.get("CPPPATH", [])]
    )

    # installed libs
    includes["compatlib"] = []
    for lb in env.GetLibBuilders():
        includes["compatlib"].extend(
            [os.path.realpath(inc) for inc in lb.get_include_dirs()]
        )

    # includes from toolchains
    p = env.PioPlatform()
    includes["toolchain"] = []
    for pkg in p.get_installed_packages():
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
            includes["toolchain"].extend(
                [os.path.realpath(inc) for inc in glob.glob(g)]
            )

    # include Unity framework if there are tests in project
    includes["unity"] = []
    auto_install_unity = False
    test_dir = env.GetProjectConfig().get_optional_dir("test")
    if os.path.isdir(test_dir) and os.listdir(test_dir) != ["README"]:
        auto_install_unity = True
    unity_dir = get_core_package_dir(
        "tool-unity",
        auto_install=auto_install_unity,
    )
    if unity_dir:
        includes["unity"].append(unity_dir)

    return includes


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
    for item in SCons.Defaults.processDefines(env.get("CPPDEFINES", [])):
        item = item.strip()
        if item:
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


def _subst_cmd(env, cmd):
    args = env.subst_list(cmd, SCons.Subst.SUBST_CMD)[0]
    return " ".join([SCons.Subst.quote_spaces(arg) for arg in args])


def DumpIDEData(env, globalenv):
    """env here is `projenv`"""

    data = {
        "env_name": env["PIOENV"],
        "libsource_dirs": [env.subst(item) for item in env.GetLibSourceDirs()],
        "defines": _dump_defines(env),
        "includes": _dump_includes(env),
        "cc_path": where_is_program(env.subst("$CC"), env.subst("${ENV['PATH']}")),
        "cxx_path": where_is_program(env.subst("$CXX"), env.subst("${ENV['PATH']}")),
        "gdb_path": where_is_program(env.subst("$GDB"), env.subst("${ENV['PATH']}")),
        "prog_path": env.subst("$PROG_PATH"),
        "svd_path": _get_svd_path(env),
        "compiler_type": env.GetCompilerType(),
        "targets": globalenv.DumpTargets(),
        "extra": dict(
            flash_images=[
                {"offset": item[0], "path": env.subst(item[1])}
                for item in env.get("FLASH_EXTRA_IMAGES", [])
            ]
        ),
    }
    data["extra"].update(env.get("IDE_EXTRA_DATA", {}))

    env_ = env.Clone()
    # https://github.com/platformio/platformio-atom-ide/issues/34
    _new_defines = []
    for item in SCons.Defaults.processDefines(env_.get("CPPDEFINES", [])):
        item = item.replace('\\"', '"')
        if " " in item:
            _new_defines.append(item.replace(" ", "\\\\ "))
        else:
            _new_defines.append(item)
    env_.Replace(CPPDEFINES=_new_defines)

    # export C/C++ build flags
    data.update(
        {
            "cc_flags": _subst_cmd(env_, "$CFLAGS $CCFLAGS $CPPFLAGS"),
            "cxx_flags": _subst_cmd(env_, "$CXXFLAGS $CCFLAGS $CPPFLAGS"),
        }
    )

    return data


def exists(_):
    return True


def generate(env):
    env.AddMethod(DumpIDEData)
    return env

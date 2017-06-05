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

from glob import glob
from os.path import join

from SCons.Defaults import processDefines

from platformio import util
from platformio.managers.core import get_core_package_dir


def dump_includes(env):
    includes = []

    for item in env.get("CPPPATH", []):
        includes.append(env.subst(item))

    # installed libs
    for lb in env.GetLibBuilders():
        includes.extend(lb.get_inc_dirs())

    # includes from toolchains
    p = env.PioPlatform()
    for name in p.get_installed_packages():
        if p.get_package_type(name) != "toolchain":
            continue
        toolchain_dir = util.glob_escape(p.get_package_dir(name))
        toolchain_incglobs = [
            join(toolchain_dir, "*", "include*"),
            join(toolchain_dir, "lib", "gcc", "*", "*", "include*")
        ]
        for g in toolchain_incglobs:
            includes.extend(glob(g))

    unity_dir = get_core_package_dir("tool-unity")
    if unity_dir:
        includes.append(unity_dir)

    return includes


def dump_defines(env):
    defines = []
    # global symbols
    for item in processDefines(env.get("CPPDEFINES", [])):
        defines.append(env.subst(item).replace('\\', ''))

    # special symbol for Atmel AVR MCU
    if env['PIOPLATFORM'] == "atmelavr":
        defines.append(
            "__AVR_%s__" % env.BoardConfig().get("build.mcu").upper()
            .replace("ATMEGA", "ATmega").replace("ATTINY", "ATtiny"))
    return defines


def DumpIDEData(env):
    LINTCCOM = "$CFLAGS $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS"
    LINTCXXCOM = "$CXXFLAGS $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS"

    data = {
        "libsource_dirs":
        [env.subst(l) for l in env.get("LIBSOURCE_DIRS", [])],
        "defines":
        dump_defines(env),
        "includes":
        dump_includes(env),
        "cc_flags":
        env.subst(LINTCCOM),
        "cxx_flags":
        env.subst(LINTCXXCOM),
        "cc_path":
        util.where_is_program(env.subst("$CC"), env.subst("${ENV['PATH']}")),
        "cxx_path":
        util.where_is_program(env.subst("$CXX"), env.subst("${ENV['PATH']}")),
        "gdb_path":
        util.where_is_program(env.subst("$GDB"), env.subst("${ENV['PATH']}")),
        "prog_path":
        env.subst("$PROG_PATH")
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

    data.update({
        "cc_flags": env_.subst(LINTCCOM),
        "cxx_flags": env_.subst(LINTCXXCOM)
    })

    return data


def exists(_):
    return True


def generate(env):
    env.AddMethod(DumpIDEData)
    return env

# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

import atexit
import re
from glob import glob
from os import environ, listdir, remove
from os.path import basename, isdir, isfile, join

from platformio.util import exec_command, where_is_program


class InoToCPPConverter(object):

    PROTOTYPE_RE = re.compile(
        r"""^(
        (\s*[a-z_\d]+\*?){1,2}      # return type
        (\s+[a-z_\d]+\s*)           # name of prototype
        \([a-z_,\.\*\&\[\]\s\d]*\)  # arguments
        )\s*\{                      # must end with {
        """,
        re.X | re.M | re.I
    )

    DETECTMAIN_RE = re.compile(r"void\s+(setup|loop)\s*\(", re.M | re.I)

    STRIPCOMMENTS_RE = re.compile(r"(/\*.*?\*/|^\s*//[^\r\n]*$)",
                                  re.M | re.S)

    def __init__(self, nodes):
        self.nodes = nodes

    def is_main_node(self, contents):
        return self.DETECTMAIN_RE.search(contents)

    @staticmethod
    def _replace_comments_callback(match):
        if "\n" in match.group(1):
            return "\n" * match.group(1).count("\n")
        else:
            return " "

    def _parse_prototypes(self, contents):
        prototypes = []
        reserved_keywords = set(["if", "else", "while"])
        for item in self.PROTOTYPE_RE.findall(contents):
            if set([item[1].strip(), item[2].strip()]) & reserved_keywords:
                continue
            prototypes.append(item[0])
        return prototypes

    def append_prototypes(self, fname, contents, prototypes):
        contents = self.STRIPCOMMENTS_RE.sub(self._replace_comments_callback,
                                             contents)
        result = []
        is_appended = False
        linenum = 0
        for line in contents.splitlines():
            linenum += 1
            line = line.strip()

            if not is_appended and line and not line.startswith("#"):
                is_appended = True
                result.append("%s;" % ";\n".join(prototypes))
                result.append('#line %d "%s"' % (linenum, fname))

            result.append(line)

        return result

    def convert(self):
        prototypes = []
        data = []
        for node in self.nodes:
            ino_contents = node.get_text_contents()
            prototypes += self._parse_prototypes(ino_contents)

            item = (basename(node.get_path()), ino_contents)
            if self.is_main_node(ino_contents):
                data = [item] + data
            else:
                data.append(item)

        if not data:
            return None

        result = ["#include <Arduino.h>"]
        is_first = True

        for name, contents in data:
            if is_first and prototypes:
                result += self.append_prototypes(name, contents, prototypes)
            else:
                result.append('#line 1 "%s"' % name)
                result.append(contents)
            is_first = False

        return "\n".join(result)


def ConvertInoToCpp(env):

    def delete_tmpcpp_file(file_):
        try:
            remove(file_)
        except:  # pylint: disable=bare-except
            if isfile(file_):
                print ("Warning: Could not remove temporary file '%s'. "
                       "Please remove it manually." % file_)

    ino_nodes = (env.Glob(join("$PROJECTSRC_DIR", "*.ino")) +
                 env.Glob(join("$PROJECTSRC_DIR", "*.pde")))

    c = InoToCPPConverter(ino_nodes)
    data = c.convert()

    if not data:
        return

    tmpcpp_file = join(env.subst("$PROJECTSRC_DIR"), "tmp_ino_to.cpp")
    with open(tmpcpp_file, "w") as f:
        f.write(data)

    atexit.register(delete_tmpcpp_file, tmpcpp_file)


def DumpIDEData(env):

    BOARD_CORE = env.get("BOARD_OPTIONS", {}).get("build", {}).get("core")

    def get_includes(env_):
        includes = []
        # includes from used framework and libs
        for item in env_.get("VARIANT_DIRS", []):
            if "$BUILDSRC_DIR" in item[0]:
                continue
            includes.append(env_.subst(item[1]))

        # custom includes
        for item in env_.get("CPPPATH", []):
            if item.startswith("$BUILD_DIR"):
                continue
            includes.append(env_.subst(item))

        # installed libs
        for d in env_.get("LIBSOURCE_DIRS", []):
            lsd_dir = env_.subst(d)
            _append_lib_includes(env_, lsd_dir, includes)

        # includes from toolchain
        toolchain_dir = env_.subst(
            join("$PIOPACKAGES_DIR", "$PIOPACKAGE_TOOLCHAIN"))
        toolchain_incglobs = [
            join(toolchain_dir, "*", "include*"),
            join(toolchain_dir, "lib", "gcc", "*", "*", "include*")
        ]
        for g in toolchain_incglobs:
            includes.extend(glob(g))

        return includes

    def _append_lib_includes(env_, libs_dir, includes):
        if not isdir(libs_dir):
            return
        for name in env_.get("LIB_USE", []) + sorted(listdir(libs_dir)):
            if not isdir(join(libs_dir, name)):
                continue
            # ignore user's specified libs
            if name in env_.get("LIB_IGNORE", []):
                continue
            if name == "__cores__":
                if isdir(join(libs_dir, name, BOARD_CORE)):
                    _append_lib_includes(
                        env_, join(libs_dir, name, BOARD_CORE), includes)
                return

            include = (
                join(libs_dir, name, "src")
                if isdir(join(libs_dir, name, "src"))
                else join(libs_dir, name)
            )
            if include not in includes:
                includes.append(include)

    def get_defines(env_):
        defines = []
        # global symbols
        for item in env_.get("CPPDEFINES", []):
            if isinstance(item, list):
                item = "=".join(item)
            defines.append(env_.subst(item).replace('\\"', '"'))

        # special symbol for Atmel AVR MCU
        board = env_.get("BOARD_OPTIONS", {})
        if board and board['platform'] == "atmelavr":
            defines.append(
                "__AVR_%s__" % board['build']['mcu'].upper()
                .replace("ATMEGA", "ATmega")
                .replace("ATTINY", "ATtiny")
            )
        return defines

    LINTCCOM = "$CFLAGS $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS"
    LINTCXXCOM = "$CXXFLAGS $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS"
    env_ = env.Clone()

    data = {
        "defines": get_defines(env_),
        "includes": get_includes(env_),
        "cc_flags": env_.subst(LINTCCOM),
        "cxx_flags": env_.subst(LINTCXXCOM),
        "cxx_path": where_is_program(
            env_.subst("$CXX"), env_.subst("${ENV['PATH']}"))
    }

    # https://github.com/platformio/platformio-atom-ide/issues/34
    _new_defines = []
    for item in env_.get("CPPDEFINES", []):
        if isinstance(item, list):
            item = "=".join(item)
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


def GetCompilerType(env):
    try:
        sysenv = environ.copy()
        sysenv['PATH'] = str(env['ENV']['PATH'])
        result = exec_command([env.subst("$CC"), "-v"], env=sysenv)
    except OSError:
        return None
    if result['returncode'] != 0:
        return None
    output = "".join([result['out'], result['err']]).lower()
    if "clang" in output and "LLVM" in output:
        return "clang"
    elif "gcc" in output:
        return "gcc"
    return None


def GetActualLDScript(env):
    script = None
    for f in env.get("LINKFLAGS", []):
        if f.startswith("-Wl,-T"):
            script = env.subst(f[6:].replace('"', "").strip())
            if isfile(script):
                return script
            for d in env.get("LIBPATH", []):
                path = join(env.subst(d), script)
                if isfile(path):
                    return path

    if script:
        env.Exit("Error: Could not find '%s' LD script in LDPATH '%s'" % (
            script, env.subst("$LIBPATH")))

    return None


def exists(_):
    return True


def generate(env):
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(DumpIDEData)
    env.AddMethod(GetCompilerType)
    env.AddMethod(GetActualLDScript)
    return env

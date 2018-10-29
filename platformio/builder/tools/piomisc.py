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

import atexit
import re
import sys
from os import environ, remove, walk
from os.path import basename, isdir, isfile, join, realpath, relpath, sep
from tempfile import mkstemp

from SCons.Action import Action
from SCons.Script import ARGUMENTS

from platformio import util
from platformio.managers.core import get_core_package_dir


class InoToCPPConverter(object):

    PROTOTYPE_RE = re.compile(
        r"""^(
        (?:template\<.*\>\s*)?      # template
        ([a-z_\d\&]+\*?\s+){1,2}      # return type
        ([a-z_\d]+\s*)              # name of prototype
        \([a-z_,\.\*\&\[\]\s\d]*\)  # arguments
        )\s*\{                      # must end with {
        """, re.X | re.M | re.I)
    DETECTMAIN_RE = re.compile(r"void\s+(setup|loop)\s*\(", re.M | re.I)
    PROTOPTRS_TPLRE = r"\([^&\(]*&(%s)[^\)]*\)"

    def __init__(self, env):
        self.env = env
        self._main_ino = None

    def is_main_node(self, contents):
        return self.DETECTMAIN_RE.search(contents)

    def convert(self, nodes):
        contents = self.merge(nodes)
        if not contents:
            return None
        return self.process(contents)

    def merge(self, nodes):
        assert nodes
        lines = []
        for node in nodes:
            contents = node.get_text_contents()
            _lines = [
                '# 1 "%s"' % node.get_path().replace("\\", "/"), contents
            ]
            if self.is_main_node(contents):
                lines = _lines + lines
                self._main_ino = node.get_path()
            else:
                lines.extend(_lines)

        if not self._main_ino:
            self._main_ino = nodes[0].get_path()

        return "\n".join(["#include <Arduino.h>"] + lines) if lines else None

    def process(self, contents):
        out_file = self._main_ino + ".cpp"
        assert self._gcc_preprocess(contents, out_file)
        with open(out_file) as fp:
            contents = fp.read()
        contents = self._join_multiline_strings(contents)
        with open(out_file, "w") as fp:
            fp.write(self.append_prototypes(contents))
        return out_file

    def _gcc_preprocess(self, contents, out_file):
        tmp_path = mkstemp()[1]
        with open(tmp_path, "w") as fp:
            fp.write(contents)
        self.env.Execute(
            self.env.VerboseAction(
                '$CXX -o "{0}" -x c++ -fpreprocessed -dD -E "{1}"'.format(
                    out_file, tmp_path),
                "Converting " + basename(out_file[:-4])))
        atexit.register(_delete_file, tmp_path)
        return isfile(out_file)

    def _join_multiline_strings(self, contents):
        if "\\\n" not in contents:
            return contents
        newlines = []
        linenum = 0
        stropen = False
        for line in contents.split("\n"):
            _linenum = self._parse_preproc_line_num(line)
            if _linenum is not None:
                linenum = _linenum
            else:
                linenum += 1

            if line.endswith("\\"):
                if line.startswith('"'):
                    stropen = True
                    newlines.append(line[:-1])
                    continue
                elif stropen:
                    newlines[len(newlines) - 1] += line[:-1]
                    continue
            elif stropen and line.endswith(('",', '";')):
                newlines[len(newlines) - 1] += line
                stropen = False
                newlines.append('#line %d "%s"' %
                                (linenum, self._main_ino.replace("\\", "/")))
                continue

            newlines.append(line)

        return "\n".join(newlines)

    @staticmethod
    def _parse_preproc_line_num(line):
        if not line.startswith("#"):
            return None
        tokens = line.split(" ", 3)
        if len(tokens) > 2 and tokens[1].isdigit():
            return int(tokens[1])
        return None

    def _parse_prototypes(self, contents):
        prototypes = []
        reserved_keywords = set(["if", "else", "while"])
        for match in self.PROTOTYPE_RE.finditer(contents):
            if (set([match.group(2).strip(),
                     match.group(3).strip()]) & reserved_keywords):
                continue
            prototypes.append(match)
        return prototypes

    def _get_total_lines(self, contents):
        total = 0
        if contents.endswith("\n"):
            contents = contents[:-1]
        for line in contents.split("\n")[::-1]:
            linenum = self._parse_preproc_line_num(line)
            if linenum is not None:
                return total + linenum
            total += 1
        return total

    def append_prototypes(self, contents):
        prototypes = self._parse_prototypes(contents)
        if not prototypes:
            return contents

        prototype_names = set([m.group(3).strip() for m in prototypes])
        split_pos = prototypes[0].start()
        match_ptrs = re.search(
            self.PROTOPTRS_TPLRE % ("|".join(prototype_names)),
            contents[:split_pos], re.M)
        if match_ptrs:
            split_pos = contents.rfind("\n", 0, match_ptrs.start()) + 1

        result = []
        result.append(contents[:split_pos].strip())
        result.append("%s;" % ";\n".join([m.group(1) for m in prototypes]))
        result.append('#line %d "%s"' % (self._get_total_lines(
            contents[:split_pos]), self._main_ino.replace("\\", "/")))
        result.append(contents[split_pos:].strip())
        return "\n".join(result)


def ConvertInoToCpp(env):
    src_dir = util.glob_escape(env.subst("$PROJECTSRC_DIR"))
    ino_nodes = (
        env.Glob(join(src_dir, "*.ino")) + env.Glob(join(src_dir, "*.pde")))
    if not ino_nodes:
        return
    c = InoToCPPConverter(env)
    out_file = c.convert(ino_nodes)

    atexit.register(_delete_file, out_file)


def _delete_file(path):
    try:
        if isfile(path):
            remove(path)
    except:  # pylint: disable=bare-except
        pass


@util.memoized()
def _get_compiler_type(env):
    try:
        sysenv = environ.copy()
        sysenv['PATH'] = str(env['ENV']['PATH'])
        result = util.exec_command([env.subst("$CC"), "-v"], env=sysenv)
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


def GetCompilerType(env):
    return _get_compiler_type(env)


def GetActualLDScript(env):

    def _lookup_in_ldpath(script):
        for d in env.get("LIBPATH", []):
            path = join(env.subst(d), script)
            if isfile(path):
                return path
        return None

    script = None
    script_in_next = False
    for f in env.get("LINKFLAGS", []):
        raw_script = None
        if f == "-T":
            script_in_next = True
            continue
        elif script_in_next:
            script_in_next = False
            raw_script = f
        elif f.startswith("-Wl,-T"):
            raw_script = f[6:]
        else:
            continue
        script = env.subst(raw_script.replace('"', "").strip())
        if isfile(script):
            return script
        path = _lookup_in_ldpath(script)
        if path:
            return path

    if script:
        sys.stderr.write(
            "Error: Could not find '%s' LD script in LDPATH '%s'\n" %
            (script, env.subst("$LIBPATH")))
        env.Exit(1)

    if not script and "LDSCRIPT_PATH" in env:
        path = _lookup_in_ldpath(env['LDSCRIPT_PATH'])
        if path:
            return path

    sys.stderr.write("Error: Could not find LD script\n")
    env.Exit(1)


def VerboseAction(_, act, actstr):
    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        return act
    return Action(act, actstr)


def PioClean(env, clean_dir):
    if not isdir(clean_dir):
        print("Build environment is clean")
        env.Exit(0)
    for root, _, files in walk(clean_dir):
        for file_ in files:
            remove(join(root, file_))
            print("Removed %s" % relpath(join(root, file_)))
    print("Done cleaning")
    util.rmtree_(clean_dir)
    env.Exit(0)


def ProcessDebug(env):
    if not env.subst("$PIODEBUGFLAGS"):
        env.Replace(PIODEBUGFLAGS=["-Og", "-g3", "-ggdb3"])
    env.Append(
        PIODEBUGFLAGS=["-D__PLATFORMIO_DEBUG__"],
        BUILD_FLAGS=env.get("PIODEBUGFLAGS", []))
    unflags = ["-Os"]
    for level in [0, 1, 2]:
        for flag in ("O", "g", "ggdb"):
            unflags.append("-%s%d" % (flag, level))
    env.Append(BUILD_UNFLAGS=unflags)


def ProcessTest(env):
    env.Append(
        CPPDEFINES=["UNIT_TEST", "UNITY_INCLUDE_CONFIG_H"],
        CPPPATH=[join("$BUILD_DIR", "UnityTestLib")])
    unitylib = env.BuildLibrary(
        join("$BUILD_DIR", "UnityTestLib"), get_core_package_dir("tool-unity"))
    env.Prepend(LIBS=[unitylib])

    src_filter = ["+<*.cpp>", "+<*.c>"]
    if "PIOTEST" in env:
        src_filter.append("+<%s%s>" % (env['PIOTEST'], sep))
    env.Replace(PIOTEST_SRC_FILTER=src_filter)


def GetExtraScripts(env, scope):
    items = []
    for item in env.get("EXTRA_SCRIPTS", []):
        if scope == "post" and ":" not in item:
            items.append(item)
        elif item.startswith("%s:" % scope):
            items.append(item[len(scope) + 1:])
    if not items:
        return items
    with util.cd(env.subst("$PROJECT_DIR")):
        return [realpath(item) for item in items]


def exists(_):
    return True


def generate(env):
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(GetCompilerType)
    env.AddMethod(GetActualLDScript)
    env.AddMethod(VerboseAction)
    env.AddMethod(PioClean)
    env.AddMethod(ProcessDebug)
    env.AddMethod(ProcessTest)
    env.AddMethod(GetExtraScripts)
    return env

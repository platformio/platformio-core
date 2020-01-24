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

from SCons.Action import Action  # pylint: disable=import-error
from SCons.Script import ARGUMENTS  # pylint: disable=import-error

from platformio import fs, util
from platformio.compat import glob_escape
from platformio.managers.core import get_core_package_dir
from platformio.proc import exec_command


class InoToCPPConverter(object):

    PROTOTYPE_RE = re.compile(
        r"""^(
        (?:template\<.*\>\s*)?      # template
        ([a-z_\d\&]+\*?\s+){1,2}    # return type
        ([a-z_\d]+\s*)              # name of prototype
        \([a-z_,\.\*\&\[\]\s\d]*\)  # arguments
        )\s*(\{|;)                  # must end with `{` or `;`
        """,
        re.X | re.M | re.I,
    )
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
            contents = fs.get_file_contents(node.get_path())
            _lines = ['# 1 "%s"' % node.get_path().replace("\\", "/"), contents]
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
        contents = fs.get_file_contents(out_file)
        contents = self._join_multiline_strings(contents)
        fs.write_file_contents(
            out_file, self.append_prototypes(contents), errors="backslashreplace"
        )
        return out_file

    def _gcc_preprocess(self, contents, out_file):
        tmp_path = mkstemp()[1]
        fs.write_file_contents(tmp_path, contents, errors="backslashreplace")
        self.env.Execute(
            self.env.VerboseAction(
                '$CXX -o "{0}" -x c++ -fpreprocessed -dD -E "{1}"'.format(
                    out_file, tmp_path
                ),
                "Converting " + basename(out_file[:-4]),
            )
        )
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
                if stropen:
                    newlines[len(newlines) - 1] += line[:-1]
                    continue
            elif stropen and line.endswith(('",', '";')):
                newlines[len(newlines) - 1] += line
                stropen = False
                newlines.append(
                    '#line %d "%s"' % (linenum, self._main_ino.replace("\\", "/"))
                )
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
            if (
                set([match.group(2).strip(), match.group(3).strip()])
                & reserved_keywords
            ):
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
        prototypes = self._parse_prototypes(contents) or []

        # skip already declared prototypes
        declared = set(m.group(1).strip() for m in prototypes if m.group(4) == ";")
        prototypes = [m for m in prototypes if m.group(1).strip() not in declared]

        if not prototypes:
            return contents

        prototype_names = set(m.group(3).strip() for m in prototypes)
        split_pos = prototypes[0].start()
        match_ptrs = re.search(
            self.PROTOPTRS_TPLRE % ("|".join(prototype_names)),
            contents[:split_pos],
            re.M,
        )
        if match_ptrs:
            split_pos = contents.rfind("\n", 0, match_ptrs.start()) + 1

        result = []
        result.append(contents[:split_pos].strip())
        result.append("%s;" % ";\n".join([m.group(1) for m in prototypes]))
        result.append(
            '#line %d "%s"'
            % (
                self._get_total_lines(contents[:split_pos]),
                self._main_ino.replace("\\", "/"),
            )
        )
        result.append(contents[split_pos:].strip())
        return "\n".join(result)


def ConvertInoToCpp(env):
    src_dir = glob_escape(env.subst("$PROJECT_SRC_DIR"))
    ino_nodes = env.Glob(join(src_dir, "*.ino")) + env.Glob(join(src_dir, "*.pde"))
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
    if env.subst("$CC").endswith("-gcc"):
        return "gcc"
    try:
        sysenv = environ.copy()
        sysenv["PATH"] = str(env["ENV"]["PATH"])
        result = exec_command([env.subst("$CC"), "-v"], env=sysenv)
    except OSError:
        return None
    if result["returncode"] != 0:
        return None
    output = "".join([result["out"], result["err"]]).lower()
    if "clang" in output and "LLVM" in output:
        return "clang"
    if "gcc" in output:
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
        if script_in_next:
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
            "Error: Could not find '%s' LD script in LDPATH '%s'\n"
            % (script, env.subst("$LIBPATH"))
        )
        env.Exit(1)

    if not script and "LDSCRIPT_PATH" in env:
        path = _lookup_in_ldpath(env["LDSCRIPT_PATH"])
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
    clean_rel_path = relpath(clean_dir)
    for root, _, files in walk(clean_dir):
        for f in files:
            dst = join(root, f)
            remove(dst)
            print(
                "Removed %s" % (dst if clean_rel_path.startswith(".") else relpath(dst))
            )
    print("Done cleaning")
    fs.rmtree(clean_dir)
    env.Exit(0)


def ConfigureDebugFlags(env):
    def _cleanup_debug_flags(scope):
        if scope not in env:
            return
        unflags = ["-Os", "-g"]
        for level in [0, 1, 2, 3]:
            for flag in ("O", "g", "ggdb"):
                unflags.append("-%s%d" % (flag, level))
        env[scope] = [f for f in env.get(scope, []) if f not in unflags]

    env.Append(CPPDEFINES=["__PLATFORMIO_BUILD_DEBUG__"])

    for scope in ("ASFLAGS", "CCFLAGS", "LINKFLAGS"):
        _cleanup_debug_flags(scope)

    debug_flags = env.ParseFlags(env.GetProjectOption("debug_build_flags"))
    env.MergeFlags(debug_flags)
    optimization_flags = [
        f for f in debug_flags.get("CCFLAGS", []) if f.startswith(("-O", "-g"))
    ]

    if optimization_flags:
        env.AppendUnique(ASFLAGS=optimization_flags, LINKFLAGS=optimization_flags)


def ConfigureTestTarget(env):
    env.Append(
        CPPDEFINES=["UNIT_TEST", "UNITY_INCLUDE_CONFIG_H"],
        CPPPATH=[join("$BUILD_DIR", "UnityTestLib")],
    )
    unitylib = env.BuildLibrary(
        join("$BUILD_DIR", "UnityTestLib"), get_core_package_dir("tool-unity")
    )
    env.Prepend(LIBS=[unitylib])

    src_filter = ["+<*.cpp>", "+<*.c>"]
    if "PIOTEST_RUNNING_NAME" in env:
        src_filter.append("+<%s%s>" % (env["PIOTEST_RUNNING_NAME"], sep))
    env.Replace(PIOTEST_SRC_FILTER=src_filter)


def GetExtraScripts(env, scope):
    items = []
    for item in env.GetProjectOption("extra_scripts", []):
        if scope == "post" and ":" not in item:
            items.append(item)
        elif item.startswith("%s:" % scope):
            items.append(item[len(scope) + 1 :])
    if not items:
        return items
    with fs.cd(env.subst("$PROJECT_DIR")):
        return [realpath(item) for item in items]


def exists(_):
    return True


def generate(env):
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(GetCompilerType)
    env.AddMethod(GetActualLDScript)
    env.AddMethod(VerboseAction)
    env.AddMethod(PioClean)
    env.AddMethod(ConfigureDebugFlags)
    env.AddMethod(ConfigureTestTarget)
    env.AddMethod(GetExtraScripts)
    return env

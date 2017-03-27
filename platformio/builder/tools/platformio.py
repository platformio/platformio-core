# Copyright 2014-present PlatformIO <contact@platformio.org>
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

import re
import sys
from glob import glob
from os import sep, walk
from os.path import basename, dirname, isdir, join, realpath

from SCons.Action import Action
from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild,
                          DefaultEnvironment, SConscript)
from SCons.Util import case_sensitive_suffixes, is_Sequence

from platformio.util import glob_escape, pioversion_to_intstr

SRC_BUILD_EXT = ["c", "cpp", "S", "spp", "SPP", "sx", "s", "asm", "ASM"]
SRC_HEADER_EXT = ["h", "hpp"]
SRC_FILTER_DEFAULT = ["+<*>", "-<.git%s>" % sep, "-<svn%s>" % sep]


def BuildProgram(env):

    def _append_pio_macros():
        env.AppendUnique(CPPDEFINES=[(
            "PLATFORMIO",
            int("{0:02d}{1:02d}{2:02d}".format(*pioversion_to_intstr())))])

    _append_pio_macros()

    # fix ASM handling under non-casitive OS
    if not case_sensitive_suffixes(".s", ".S"):
        env.Replace(AS="$CC", ASCOM="$ASPPCOM")

    # process extra flags from board
    if "BOARD" in env and "build.extra_flags" in env.BoardConfig():
        env.ProcessFlags(env.BoardConfig().get("build.extra_flags"))
    # remove base flags
    env.ProcessUnFlags(env.get("BUILD_UNFLAGS"))
    # apply user flags
    env.ProcessFlags(env.get("BUILD_FLAGS"))

    env.BuildFrameworks(env.get("PIOFRAMEWORK"))

    # restore PIO macros if it was deleted by framework
    _append_pio_macros()

    # build dependent libs
    deplibs = env.BuildDependentLibraries("$PROJECTSRC_DIR")

    # append specified LD_SCRIPT
    if ("LDSCRIPT_PATH" in env and
            not any(["-Wl,-T" in f for f in env['LINKFLAGS']])):
        env.Append(LINKFLAGS=['-Wl,-T"$LDSCRIPT_PATH"'])

    # enable "cyclic reference" for linker
    if env.get("LIBS", deplibs) and env.GetCompilerType() == "gcc":
        env.Prepend(_LIBFLAGS="-Wl,--start-group ")
        env.Append(_LIBFLAGS=" -Wl,--end-group")

    # Handle SRC_BUILD_FLAGS
    env.ProcessFlags(env.get("SRC_BUILD_FLAGS"))

    env.Append(
        CPPPATH=["$PROJECTSRC_DIR"],
        LIBS=deplibs,
        LIBPATH=["$BUILD_DIR"],
        PIOBUILDFILES=env.CollectBuildFiles(
            "$BUILDSRC_DIR",
            "$PROJECTSRC_DIR",
            src_filter=env.get("SRC_FILTER"),
            duplicate=False))

    if "__test" in COMMAND_LINE_TARGETS:
        env.Append(PIOBUILDFILES=env.ProcessTest())

    if not env['PIOBUILDFILES'] and not COMMAND_LINE_TARGETS:
        sys.stderr.write(
            "Error: Nothing to build. Please put your source code files "
            "to '%s' folder\n" % env.subst("$PROJECTSRC_DIR"))
        env.Exit(1)

    program = env.Program(
        join("$BUILD_DIR", env.subst("$PROGNAME")), env['PIOBUILDFILES'])

    checksize_action = Action(env.CheckUploadSize, "Checking program size")
    AlwaysBuild(env.Alias("checkprogsize", program, checksize_action))
    if set(["upload", "program"]) & set(COMMAND_LINE_TARGETS):
        env.AddPostAction(program, checksize_action)

    return program


def ProcessFlags(env, flags):  # pylint: disable=too-many-branches
    if not flags:
        return
    if isinstance(flags, list):
        flags = " ".join(flags)
    parsed_flags = env.ParseFlags(str(flags))
    for flag in parsed_flags.pop("CPPDEFINES"):
        if not is_Sequence(flag):
            env.Append(CPPDEFINES=flag)
            continue
        _key, _value = flag[:2]
        if '\"' in _value:
            _value = _value.replace('\"', '\\\"')
        elif _value.isdigit():
            _value = int(_value)
        elif _value.replace(".", "", 1).isdigit():
            _value = float(_value)
        env.Append(CPPDEFINES=(_key, _value))
    env.Append(**parsed_flags)

    # fix relative CPPPATH & LIBPATH
    for k in ("CPPPATH", "LIBPATH"):
        for i, p in enumerate(env.get(k, [])):
            if isdir(p):
                env[k][i] = realpath(p)
    # fix relative path for "-include"
    for i, f in enumerate(env.get("CCFLAGS", [])):
        if isinstance(f, tuple) and f[0] == "-include":
            env['CCFLAGS'][i] = (f[0], env.File(realpath(f[1].get_path())))

    # Cancel any previous definition of name, either built in or
    # provided with a -D option // Issue #191
    undefines = [
        u for u in env.get("CCFLAGS", [])
        if isinstance(u, basestring) and u.startswith("-U")
    ]
    if undefines:
        for undef in undefines:
            env['CCFLAGS'].remove(undef)
        env.Append(_CPPDEFFLAGS=" %s" % " ".join(undefines))


def ProcessUnFlags(env, flags):
    if not flags:
        return
    if isinstance(flags, list):
        flags = " ".join(flags)
    parsed_flags = env.ParseFlags(str(flags))
    all_flags = []
    for items in parsed_flags.values():
        all_flags.extend(items)
    all_flags = set(all_flags)

    for key in parsed_flags:
        cur_flags = set(env.Flatten(env.get(key, [])))
        for item in cur_flags & all_flags:
            while item in env[key]:
                env[key].remove(item)


def IsFileWithExt(env, file_, ext):  # pylint: disable=W0613
    if basename(file_).startswith("."):
        return False
    for e in ext:
        if file_.endswith(".%s" % e):
            return True
    return False


def MatchSourceFiles(env, src_dir, src_filter=None):

    SRC_FILTER_PATTERNS_RE = re.compile(r"(\+|\-)<([^>]+)>")

    def _append_build_item(items, item, src_dir):
        if env.IsFileWithExt(item, SRC_BUILD_EXT + SRC_HEADER_EXT):
            items.add(item.replace(src_dir + sep, ""))

    src_dir = env.subst(src_dir)
    src_filter = src_filter or SRC_FILTER_DEFAULT
    if isinstance(src_filter, list) or isinstance(src_filter, tuple):
        src_filter = " ".join(src_filter)

    matches = set()
    # correct fs directory separator
    src_filter = src_filter.replace("/", sep).replace("\\", sep)
    for (action, pattern) in SRC_FILTER_PATTERNS_RE.findall(src_filter):
        items = set()
        for item in glob(join(glob_escape(src_dir), pattern)):
            if isdir(item):
                for root, _, files in walk(item, followlinks=True):
                    for f in files:
                        _append_build_item(items, join(root, f), src_dir)
            else:
                _append_build_item(items, item, src_dir)
        if action == "+":
            matches |= items
        else:
            matches -= items
    return sorted(list(matches))


def CollectBuildFiles(env,
                      variant_dir,
                      src_dir,
                      src_filter=None,
                      duplicate=False):
    sources = []
    variants = []

    src_dir = env.subst(src_dir)
    if src_dir.endswith(sep):
        src_dir = src_dir[:-1]

    for item in env.MatchSourceFiles(src_dir, src_filter):
        _reldir = dirname(item)
        _src_dir = join(src_dir, _reldir) if _reldir else src_dir
        _var_dir = join(variant_dir, _reldir) if _reldir else variant_dir

        if _var_dir not in variants:
            variants.append(_var_dir)
            env.VariantDir(_var_dir, _src_dir, duplicate)

        if env.IsFileWithExt(item, SRC_BUILD_EXT):
            sources.append(env.File(join(_var_dir, basename(item))))

    return sources


def BuildFrameworks(env, frameworks):
    if not frameworks:
        return

    if "BOARD" not in env:
        sys.stderr.write("Please specify `board` in `platformio.ini` to use "
                         "with '%s' framework\n" % ", ".join(frameworks))
        env.Exit(1)

    board_frameworks = env.BoardConfig().get("frameworks", [])
    if frameworks == ["platformio"]:
        if board_frameworks:
            frameworks.insert(0, board_frameworks[0])
        else:
            sys.stderr.write(
                "Error: Please specify `board` in `platformio.ini`\n")
            env.Exit(1)

    for f in frameworks:
        if f in ("arduino", "energia"):
            env.ConvertInoToCpp()

        if f in board_frameworks:
            SConscript(env.GetFrameworkScript(f))
        else:
            sys.stderr.write(
                "Error: This board doesn't support %s framework!\n" % f)
            env.Exit(1)


def BuildLibrary(env, variant_dir, src_dir, src_filter=None):
    lib = env.Clone()
    return lib.StaticLibrary(
        lib.subst(variant_dir),
        lib.CollectBuildFiles(variant_dir, src_dir, src_filter=src_filter))


def BuildSources(env, variant_dir, src_dir, src_filter=None):
    DefaultEnvironment().Append(PIOBUILDFILES=env.Clone().CollectBuildFiles(
        variant_dir, src_dir, src_filter=src_filter))


def exists(_):
    return True


def generate(env):
    env.AddMethod(BuildProgram)
    env.AddMethod(ProcessFlags)
    env.AddMethod(ProcessUnFlags)
    env.AddMethod(IsFileWithExt)
    env.AddMethod(MatchSourceFiles)
    env.AddMethod(CollectBuildFiles)
    env.AddMethod(BuildFrameworks)
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildSources)
    return env

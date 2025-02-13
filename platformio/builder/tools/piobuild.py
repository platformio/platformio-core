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

import fnmatch
import os
import sys

from SCons import Builder, Util  # pylint: disable=import-error
from SCons.Node import FS  # pylint: disable=import-error
from SCons.Script import COMMAND_LINE_TARGETS  # pylint: disable=import-error
from SCons.Script import AlwaysBuild  # pylint: disable=import-error
from SCons.Script import DefaultEnvironment  # pylint: disable=import-error
from SCons.Script import SConscript  # pylint: disable=import-error

from platformio import __version__, fs
from platformio.compat import IS_MACOS, string_types
from platformio.package.version import pepver_to_semver
from platformio.proc import where_is_program

SRC_HEADER_EXT = ["h", "hpp"]
SRC_ASM_EXT = ["S", "spp", "SPP", "sx", "s", "asm", "ASM"]
SRC_C_EXT = ["c"]
SRC_CXX_EXT = ["cc", "cpp", "cxx", "c++"]
SRC_BUILD_EXT = SRC_C_EXT + SRC_CXX_EXT + SRC_ASM_EXT
SRC_FILTER_DEFAULT = ["+<*>", "-<.git%s>" % os.sep, "-<.svn%s>" % os.sep]


def scons_patched_match_splitext(path, suffixes=None):
    """Patch SCons Builder, append $OBJSUFFIX to the end of each target"""
    tokens = Util.splitext(path)
    if suffixes and tokens[1] and tokens[1] in suffixes:
        return (path, tokens[1])
    return tokens


def GetBuildType(env):
    modes = []
    if (
        set(["__debug", "sizedata"])  # sizedata = for memory inspection
        & set(COMMAND_LINE_TARGETS)
        or env.GetProjectOption("build_type") == "debug"
    ):
        modes.append("debug")
    if "__test" in COMMAND_LINE_TARGETS or env.GetProjectOption("build_type") == "test":
        modes.append("test")
    return ", ".join(modes or ["release"])


def BuildProgram(env):
    env.ProcessCompileDbToolchainOption()
    env.ProcessProgramDeps()
    env.ProcessProjectDeps()

    # append into the beginning a main LD script
    if env.get("LDSCRIPT_PATH") and not any("-Wl,-T" in f for f in env["LINKFLAGS"]):
        env.Prepend(LINKFLAGS=["-T", env.subst("$LDSCRIPT_PATH")])

    # enable "cyclic reference" for linker
    if (
        env.get("LIBS")
        and env.GetCompilerType() == "gcc"
        and (env.PioPlatform().is_embedded() or not IS_MACOS)
    ):
        env.Prepend(_LIBFLAGS="-Wl,--start-group ")
        env.Append(_LIBFLAGS=" -Wl,--end-group")

    program = env.Program(env.subst("$PROGPATH"), env["PIOBUILDFILES"])
    env.Replace(PIOMAINPROG=program)

    AlwaysBuild(
        env.Alias(
            "checkprogsize",
            program,
            env.VerboseAction(env.CheckUploadSize, "Checking size $PIOMAINPROG"),
        )
    )

    print("Building in %s mode" % env["BUILD_TYPE"])

    return program


def ProcessCompileDbToolchainOption(env):
    if "compiledb" not in COMMAND_LINE_TARGETS:
        return
    # Resolve absolute path of toolchain
    for cmd in ("CC", "CXX", "AS"):
        if cmd not in env:
            continue
        if os.path.isabs(env[cmd]) or '"' in env[cmd]:
            continue
        env[cmd] = where_is_program(env.subst("$%s" % cmd), env.subst("${ENV['PATH']}"))
        if " " in env[cmd]:  # issue #4998: Space in compilator path
            env[cmd] = f'"{env[cmd]}"'

    if env.get("COMPILATIONDB_INCLUDE_TOOLCHAIN"):
        print("Warning! `COMPILATIONDB_INCLUDE_TOOLCHAIN` is scoping")
        for scope, includes in env.DumpIntegrationIncludes().items():
            if scope in ("toolchain",):
                env.Append(CPPPATH=includes)


def ProcessProgramDeps(env):
    def _append_pio_macros():
        core_version = pepver_to_semver(__version__)
        env.AppendUnique(
            CPPDEFINES=[
                (
                    "PLATFORMIO",
                    int(
                        "{0:02d}{1:02d}{2:02d}".format(
                            core_version.major, core_version.minor, core_version.patch
                        )
                    ),
                )
            ]
        )

    _append_pio_macros()

    env.PrintConfiguration()

    # process extra flags from board
    if "BOARD" in env and "build.extra_flags" in env.BoardConfig():
        env.ProcessFlags(env.BoardConfig().get("build.extra_flags"))

    # apply user flags
    env.ProcessFlags(env.get("BUILD_FLAGS"))

    # process framework scripts
    env.BuildFrameworks(env.get("PIOFRAMEWORK"))

    if "debug" in env["BUILD_TYPE"]:
        env.ConfigureDebugTarget()

    # remove specified flags
    env.ProcessUnFlags(env.get("BUILD_UNFLAGS"))


def ProcessProjectDeps(env):
    plb = env.ConfigureProjectLibBuilder()

    # prepend project libs to the beginning of list
    env.Prepend(LIBS=plb.build())
    # prepend extra linker related options from libs
    env.PrependUnique(
        **{
            key: plb.env.get(key)
            for key in ("LIBS", "LIBPATH", "LINKFLAGS")
            if plb.env.get(key)
        }
    )

    if "test" in env["BUILD_TYPE"]:
        build_files_before_nums = len(env.get("PIOBUILDFILES", []))
        plb.env.BuildSources(
            "$BUILD_TEST_DIR", "$PROJECT_TEST_DIR", "$PIOTEST_SRC_FILTER"
        )
        if len(env.get("PIOBUILDFILES", [])) - build_files_before_nums < 1:
            sys.stderr.write(
                "Error: Nothing to build. Please put your test suites "
                "to the '%s' folder\n" % env.subst("$PROJECT_TEST_DIR")
            )
            env.Exit(1)

    if "test" not in env["BUILD_TYPE"] or env.GetProjectOption("test_build_src"):
        plb.env.BuildSources(
            "$BUILD_SRC_DIR", "$PROJECT_SRC_DIR", env.get("SRC_FILTER")
        )

    if not env.get("PIOBUILDFILES") and not COMMAND_LINE_TARGETS:
        sys.stderr.write(
            "Error: Nothing to build. Please put your source code files "
            "to the '%s' folder\n" % env.subst("$PROJECT_SRC_DIR")
        )
        env.Exit(1)


def ParseFlagsExtended(env, flags):  # pylint: disable=too-many-branches
    if not isinstance(flags, list):
        flags = [flags]
    result = {}
    for raw in flags:
        for key, value in env.ParseFlags(str(raw)).items():
            if key not in result:
                result[key] = []
            result[key].extend(value)

    cppdefines = []
    for item in result["CPPDEFINES"]:
        if not Util.is_Sequence(item):
            cppdefines.append(item)
            continue
        name, value = item[:2]
        if '"' in value:
            value = value.replace('"', '\\"')
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "", 1).isdigit():
            value = float(value)
        cppdefines.append((name, value))
    result["CPPDEFINES"] = cppdefines

    # fix relative CPPPATH & LIBPATH
    for k in ("CPPPATH", "LIBPATH"):
        for i, p in enumerate(result.get(k, [])):
            p = env.subst(p)
            if os.path.isdir(p):
                result[k][i] = os.path.abspath(p)

    # fix relative LIBs
    for i, l in enumerate(result.get("LIBS", [])):
        if isinstance(l, FS.File):
            result["LIBS"][i] = os.path.abspath(l.get_path())

    # fix relative path for "-include"
    for i, f in enumerate(result.get("CCFLAGS", [])):
        if isinstance(f, tuple) and f[0] == "-include":
            result["CCFLAGS"][i] = (f[0], env.subst(f[1].get_path()))

    return result


def ProcessFlags(env, flags):  # pylint: disable=too-many-branches
    if not flags:
        return
    env.Append(**env.ParseFlagsExtended(flags))

    # Cancel any previous definition of name, either built in or
    # provided with a -U option // Issue #191
    undefines = [
        u
        for u in env.get("CCFLAGS", [])
        if isinstance(u, string_types) and u.startswith("-U")
    ]
    if undefines:
        for undef in undefines:
            env["CCFLAGS"].remove(undef)
            if undef[2:] in env["CPPDEFINES"]:
                env["CPPDEFINES"].remove(undef[2:])
        env.Append(_CPPDEFFLAGS=" %s" % " ".join(undefines))


def ProcessUnFlags(env, flags):
    if not flags:
        return
    parsed = env.ParseFlagsExtended(flags)
    unflag_scopes = tuple(set(["ASPPFLAGS"] + list(parsed.keys())))
    for scope in unflag_scopes:
        for unflags in parsed.values():
            for unflag in unflags:
                for current in list(env.get(scope, [])):
                    conditions = [
                        unflag == current,
                        not isinstance(unflag, (tuple, list))
                        and isinstance(current, (tuple, list))
                        and unflag == current[0],
                    ]
                    if any(conditions):
                        env[scope].remove(current)


def StringifyMacro(env, value):  # pylint: disable=unused-argument
    return '\\"%s\\"' % value.replace('"', '\\\\\\"')


def MatchSourceFiles(env, src_dir, src_filter=None, src_exts=None):
    src_filter = env.subst(src_filter) if src_filter else None
    src_filter = src_filter or SRC_FILTER_DEFAULT
    src_exts = src_exts or (SRC_BUILD_EXT + SRC_HEADER_EXT)
    return fs.match_src_files(env.subst(src_dir), src_filter, src_exts)


def CollectBuildFiles(
    env, variant_dir, src_dir, src_filter=None, duplicate=False
):  # pylint: disable=too-many-locals
    sources = []
    variants = []

    src_dir = env.subst(src_dir)
    if src_dir.endswith(os.sep):
        src_dir = src_dir[:-1]

    for item in env.MatchSourceFiles(src_dir, src_filter, SRC_BUILD_EXT):
        _reldir = os.path.dirname(item)
        _src_dir = os.path.join(src_dir, _reldir) if _reldir else src_dir
        _var_dir = os.path.join(variant_dir, _reldir) if _reldir else variant_dir

        if _var_dir not in variants:
            variants.append(_var_dir)
            env.VariantDir(_var_dir, _src_dir, duplicate)

        sources.append(env.File(os.path.join(_var_dir, os.path.basename(item))))

    middlewares = env.get("__PIO_BUILD_MIDDLEWARES")
    if not middlewares:
        return sources

    new_sources = []
    for node in sources:
        new_node = node
        for callback, pattern in middlewares:
            if pattern and not fnmatch.fnmatch(node.srcnode().get_path(), pattern):
                continue
            if callback.__code__.co_argcount == 2:
                new_node = callback(env, new_node)
            else:
                new_node = callback(new_node)
            if not new_node:
                break
        if new_node:
            new_sources.append(new_node)

    return new_sources


def AddBuildMiddleware(env, callback, pattern=None):
    env.Append(__PIO_BUILD_MIDDLEWARES=[(callback, pattern)])


def BuildFrameworks(env, frameworks):
    if not frameworks:
        return

    if "BOARD" not in env:
        sys.stderr.write(
            "Please specify `board` in `platformio.ini` to use "
            "with '%s' framework\n" % ", ".join(frameworks)
        )
        env.Exit(1)

    supported_frameworks = env.BoardConfig().get("frameworks", [])
    for name in frameworks:
        if name == "arduino":
            # Arduino IDE appends .o to the end of filename
            Builder.match_splitext = scons_patched_match_splitext
            if "nobuild" not in COMMAND_LINE_TARGETS:
                env.ConvertInoToCpp()

        if name in supported_frameworks:
            SConscript(env.GetFrameworkScript(name), exports="env")
        else:
            sys.stderr.write("Error: This board doesn't support %s framework!\n" % name)
            env.Exit(1)


def BuildLibrary(env, variant_dir, src_dir, src_filter=None, nodes=None):
    env.ProcessUnFlags(env.get("BUILD_UNFLAGS"))
    nodes = nodes or env.CollectBuildFiles(variant_dir, src_dir, src_filter)
    return env.StaticLibrary(env.subst(variant_dir), nodes)


def BuildSources(env, variant_dir, src_dir, src_filter=None):
    if env.get("PIOMAINPROG"):
        sys.stderr.write(
            "Error: The main program is already constructed and the inline "
            "source files are not allowed. Please use `env.BuildLibrary(...)` "
            "or PRE-type script instead."
        )
        env.Exit(1)

    nodes = env.CollectBuildFiles(variant_dir, src_dir, src_filter)
    DefaultEnvironment().Append(
        PIOBUILDFILES=[
            env.Object(node) if isinstance(node, FS.File) else node for node in nodes
        ]
    )


def exists(_):
    return True


def generate(env):
    env.AddMethod(GetBuildType)
    env.AddMethod(BuildProgram)
    env.AddMethod(ProcessProgramDeps)
    env.AddMethod(ProcessCompileDbToolchainOption)
    env.AddMethod(ProcessProjectDeps)
    env.AddMethod(ParseFlagsExtended)
    env.AddMethod(ProcessFlags)
    env.AddMethod(ProcessUnFlags)
    env.AddMethod(StringifyMacro)
    env.AddMethod(MatchSourceFiles)
    env.AddMethod(CollectBuildFiles)
    env.AddMethod(AddBuildMiddleware)
    env.AddMethod(BuildFrameworks)
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildSources)
    return env

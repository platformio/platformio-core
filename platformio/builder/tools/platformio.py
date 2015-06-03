# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
import json
import re
from glob import glob
from os import getenv, listdir, remove, sep, walk
from os.path import basename, dirname, isdir, isfile, join, normpath

from SCons.Script import (COMMAND_LINE_TARGETS, DefaultEnvironment, Exit,
                          SConscript, SConscriptChdir)
from SCons.Util import case_sensitive_suffixes

from platformio.util import pioversion_to_intstr


def BuildFirmware(env):

    # fix ASM handling under non-casitive OS
    if not case_sensitive_suffixes(".s", ".S"):
        env.Replace(
            AS="$CC",
            ASCOM="$ASPPCOM"
        )

    env.ProcessFlags()
    env.BuildFramework()

    firmenv = env.Clone()
    vdirs = firmenv.VariantDirRecursive(
        join("$BUILD_DIR", "src"), "$PROJECTSRC_DIR", duplicate=False)

    # build dependent libs
    deplibs = firmenv.BuildDependentLibraries("$PROJECTSRC_DIR")

    # append specified LD_SCRIPT
    if "LDSCRIPT_PATH" in firmenv:
        firmenv.Append(
            LINKFLAGS=["-T", "$LDSCRIPT_PATH"]
        )

    # enable "cyclic reference" for linker
    firmenv.Prepend(
        _LIBFLAGS="-Wl,--start-group "
    )
    firmenv.Append(
        _LIBFLAGS=" -Wl,--end-group"
    )

    # Handle SRCBUILD_FLAGS
    if getenv("PLATFORMIO_SRCBUILD_FLAGS", None):
        firmenv.MergeFlags(getenv("PLATFORMIO_SRCBUILD_FLAGS"))
    if "SRCBUILD_FLAGS" in env:
        firmenv.MergeFlags(env['SRCBUILD_FLAGS'])

    firmenv.Append(
        CPPDEFINES=["PLATFORMIO={0:02d}{1:02d}{2:02d}".format(
            *pioversion_to_intstr())]
    )

    if "envdump" in COMMAND_LINE_TARGETS:
        print env.Dump()
        Exit()

    if "idedata" in COMMAND_LINE_TARGETS:
        print json.dumps(env.DumpIDEData())
        Exit()

    return firmenv.Program(
        join("$BUILD_DIR", "firmware"),
        [firmenv.GlobCXXFiles(vdir) for vdir in vdirs],
        LIBS=env.get("LIBS", []) + deplibs,
        LIBPATH=env.get("LIBPATH", []) + ["$BUILD_DIR"],
        PROGSUFFIX=".elf"
    )


def ProcessFlags(env):
    if "extra_flags" in env.get("BOARD_OPTIONS", {}).get("build", {}):
        env.MergeFlags(env.subst("${BOARD_OPTIONS['build']['extra_flags']}"))

    # Handle BUILD_FLAGS
    if getenv("PLATFORMIO_BUILD_FLAGS", None):
        env.MergeFlags(getenv("PLATFORMIO_BUILD_FLAGS"))
    if "BUILD_FLAGS" in env:
        env.MergeFlags(env['BUILD_FLAGS'])

    # Cancel any previous definition of name, either built in or
    # provided with a -D option // Issue #191
    undefines = [f for f in env.get("CCFLAGS", []) if f.startswith("-U")]
    if undefines:
        for undef in undefines:
            env['CCFLAGS'].remove(undef)
        env.Append(_CPPDEFFLAGS=" %s" % " ".join(undefines))


def GlobCXXFiles(env, path):
    files = []
    for suff in ["c", "cpp", "S", "spp", "SPP", "sx", "s", "asm", "ASM"]:
        _list = env.Glob(join(path, "*.%s" % suff))
        if _list:
            files += _list
    return files


def VariantDirWrap(env, variant_dir, src_dir, duplicate=True):
    DefaultEnvironment().Append(VARIANT_DIRS=[(variant_dir, src_dir)])
    env.VariantDir(variant_dir, src_dir, duplicate)


def VariantDirRecursive(env, variant_dir, src_dir, duplicate=True,
                        ignore_pattern=None):
    if not ignore_pattern:
        ignore_pattern = (".git", ".svn")
    variants = []
    src_dir = env.subst(src_dir)
    for root, _, _ in walk(src_dir, followlinks=True):
        _src_dir = root
        _var_dir = variant_dir + root.replace(src_dir, "")
        if any([s in _var_dir.lower() for s in ignore_pattern]):
            continue
        env.VariantDirWrap(_var_dir, _src_dir, duplicate)
        variants.append(_var_dir)
    return variants


def BuildFramework(env):
    if "FRAMEWORK" not in env:
        return

    if env['FRAMEWORK'].lower() in ("arduino", "energia"):
        env.ConvertInoToCpp()

    for f in env['FRAMEWORK'].split(","):
        framework = f.strip().lower()
        if framework in env.get("BOARD_OPTIONS", {}).get("frameworks"):
            SConscriptChdir(0)
            SConscript(
                env.subst(join("$PIOBUILDER_DIR", "scripts", "frameworks",
                               "%s.py" % framework))
            )
        else:
            Exit("Error: This board doesn't support %s framework!" %
                 framework)


def BuildLibrary(env, variant_dir, library_dir, ignore_files=None):
    lib = env.Clone()
    vdirs = lib.VariantDirRecursive(
        variant_dir, library_dir, ignore_pattern=(".git", ".svn", "examples"))
    srcfiles = []
    for vdir in vdirs:
        for item in lib.GlobCXXFiles(vdir):
            if not ignore_files or item.name not in ignore_files:
                srcfiles.append(item)
    return lib.Library(
        lib.subst(variant_dir),
        srcfiles
    )


def BuildDependentLibraries(env, src_dir):  # pylint: disable=R0914

    INCLUDES_RE = re.compile(
        r"^\s*#include\s+(\<|\")([^\>\"\']+)(?:\>|\")", re.M)
    LIBSOURCE_DIRS = [env.subst(d) for d in env.get("LIBSOURCE_DIRS", [])]
    USE_LIBS = [l.strip() for l in env.get("USE_LIBS", "").split(",")
                if l.strip()]

    # start internal prototypes

    class IncludeFinder(object):

        def __init__(self, base_dir, name, is_system=False):
            self.base_dir = base_dir
            self.name = name
            self.is_system = is_system

            self._inc_path = None
            self._lib_dir = None
            self._lib_name = None

        def getIncPath(self):
            return self._inc_path

        def getLibDir(self):
            return self._lib_dir

        def getLibName(self):
            return self._lib_name

        def run(self):
            if not self.is_system and self._find_in_local():
                return True
            return self._find_in_system()

        def _find_in_local(self):
            if isfile(join(self.base_dir, self.name)):
                self._inc_path = join(self.base_dir, self.name)
                return True
            else:
                return False

        def _find_in_system(self):
            for lsd_dir in LIBSOURCE_DIRS:
                if not isdir(lsd_dir):
                    continue

                for ld in USE_LIBS + sorted(listdir(lsd_dir)):
                    if not isdir(join(lsd_dir, ld)):
                        continue

                    inc_path = normpath(join(lsd_dir, ld, self.name))
                    try:
                        lib_dir = inc_path[:inc_path.index(
                            sep, len(lsd_dir) + 1)]
                    except ValueError:
                        continue
                    lib_name = basename(lib_dir)

                    # ignore user's specified libs
                    if "IGNORE_LIBS" in env and lib_name in env['IGNORE_LIBS']:
                        continue

                    if not isfile(inc_path):
                        # if source code is in "src" dir
                        lib_dir = join(lsd_dir, lib_name, "src")
                        inc_path = join(lib_dir, self.name)

                    if isfile(inc_path):
                        self._lib_dir = lib_dir
                        self._lib_name = lib_name
                        self._inc_path = inc_path
                        return True
            return False

    def _get_dep_libs(src_dir):
        state = {
            "paths": set(),
            "libs": set(),
            "ordered": set()
        }

        state = _process_src_dir(state, env.subst(src_dir))

        result = []
        for item in sorted(state['ordered'], key=lambda s: s[0]):
            result.append((item[1], item[2]))
        return result

    def _process_src_dir(state, src_dir):
        for root, _, _ in walk(src_dir, followlinks=True):
            for node in (env.GlobCXXFiles(root) +
                         env.Glob(join(root, "*.h"))):
                state = _parse_includes(state, node)
        return state

    def _parse_includes(state, node):
        skip_includes = ("arduino.h", "energia.h")
        matches = INCLUDES_RE.findall(node.get_text_contents())
        for (inc_type, inc_name) in matches:
            base_dir = dirname(node.get_abspath())
            if inc_name.lower() in skip_includes:
                continue
            if join(base_dir, inc_name) in state['paths']:
                continue
            else:
                state['paths'].add(join(base_dir, inc_name))

            finder = IncludeFinder(base_dir, inc_name, inc_type == "<")
            if finder.run():
                _parse_includes(state, env.File(finder.getIncPath()))

                _lib_dir = finder.getLibDir()
                if _lib_dir and _lib_dir not in state['libs']:
                    state['ordered'].add((
                        len(state['ordered']) + 1, finder.getLibName(),
                        _lib_dir))
                    state['libs'].add(_lib_dir)

                    if getenv("PLATFORMIO_LDF_CYCLIC",
                              env.subst("$LDF_CYCLIC")).lower() == "true":
                        state = _process_src_dir(state, _lib_dir)
        return state

    # end internal prototypes

    deplibs = _get_dep_libs(src_dir)
    for l, ld in deplibs:
        env.Append(
            CPPPATH=[join("$BUILD_DIR", l)]
        )
        # add automatically "utility" dir from the lib (Arduino issue)
        if isdir(join(ld, "utility")):
            env.Append(
                CPPPATH=[join("$BUILD_DIR", l, "utility")]
            )

    libs = []
    for (libname, inc_dir) in deplibs:
        lib = env.BuildLibrary(
            join("$BUILD_DIR", libname), inc_dir)
        env.Clean(libname, lib)
        libs.append(lib)
    return libs


class InoToCPPConverter(object):

    PROTOTYPE_RE = re.compile(
        r"""^(
        (\s*[a-z_\d]+){1,2}         # return type
        (\s+[a-z_\d]+\s*)           # name of prototype
        \([a-z_,\.\*\&\[\]\s\d]*\)  # arguments
        )\s*\{                      # must end with {
        """,
        re.X | re.M | re.I
    )

    DETECTMAIN_RE = re.compile(r"void\s+(setup|loop)\s*\(", re.M | re.I)

    STRIPCOMMENTS_RE = re.compile(r"(/\*.*?\*/|(^|\s+)//[^\r\n]*$)",
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
        remove(file_)

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
    data = {
        "defines": [],
        "includes": []
    }

    # includes from framework and libs
    for item in env.get("VARIANT_DIRS", []):
        data['includes'].append(env.subst(item[1]))

    # includes from toolchain
    toolchain_dir = env.subst(
        join("$PIOPACKAGES_DIR", "$PIOPACKAGE_TOOLCHAIN"))
    toolchain_incglobs = [
        join(toolchain_dir, "*", "include"),
        join(toolchain_dir, "lib", "gcc", "*", "*", "include")
    ]
    for g in toolchain_incglobs:
        data['includes'].extend(glob(g))

    # global symbols
    for item in env.get("CPPDEFINES", []):
        data['defines'].append(env.subst(item))

    # special symbol for Atmel AVR MCU
    board = env.get("BOARD_OPTIONS", {})
    if board and board['platform'] == "atmelavr":
        data['defines'].append(
            "__AVR_%s__" % board['build']['mcu'].upper()
            .replace("ATMEGA", "ATmega")
            .replace("ATTINY", "ATtiny")
        )

    return data


def exists(_):
    return True


def generate(env):
    env.AddMethod(BuildFirmware)
    env.AddMethod(ProcessFlags)
    env.AddMethod(GlobCXXFiles)
    env.AddMethod(VariantDirWrap)
    env.AddMethod(VariantDirRecursive)
    env.AddMethod(BuildFramework)
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildDependentLibraries)
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(DumpIDEData)
    return env

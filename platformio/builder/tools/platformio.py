# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import re
from glob import glob
from os import getenv, listdir, sep, walk
from os.path import basename, dirname, isdir, isfile, join, normpath

from SCons.Script import (COMMAND_LINE_TARGETS, DefaultEnvironment, Exit,
                          SConscript)
from SCons.Util import case_sensitive_suffixes

from platformio.util import pioversion_to_intstr

SRC_BUILD_EXT = ["c", "cpp", "S", "spp", "SPP", "sx", "s", "asm", "ASM"]
SRC_HEADER_EXT = ["h", "hpp"]
SRC_DEFAULT_FILTER = " ".join([
    "+<*>", "-<.git%s>" % sep, "-<svn%s>" % sep, "-<examples%s>" % sep
])


def BuildProgram(env):

    # fix ASM handling under non-casitive OS
    if not case_sensitive_suffixes(".s", ".S"):
        env.Replace(
            AS="$CC",
            ASCOM="$ASPPCOM"
        )

    env.ProcessFlags()
    env.BuildFramework()

    # build dependent libs
    deplibs = env.BuildDependentLibraries("$PROJECTSRC_DIR")

    # append specified LD_SCRIPT
    if ("LDSCRIPT_PATH" in env and
            not any(["-Wl,-T" in f for f in env['LINKFLAGS']])):
        env.Append(
            LINKFLAGS=["-Wl,-T", "$LDSCRIPT_PATH"]
        )

    # enable "cyclic reference" for linker
    if env.get("LIBS", deplibs) and env.GetCompilerType() == "gcc":
        env.Prepend(
            _LIBFLAGS="-Wl,--start-group "
        )
        env.Append(
            _LIBFLAGS=" -Wl,--end-group"
        )

    # Handle SRC_BUILD_FLAGS
    if getenv("PLATFORMIO_SRC_BUILD_FLAGS", None):
        env.MergeFlags(getenv("PLATFORMIO_SRC_BUILD_FLAGS"))
    if "SRC_BUILD_FLAGS" in env:
        env.MergeFlags(env['SRC_BUILD_FLAGS'])

    env.Append(
        CPPDEFINES=["PLATFORMIO={0:02d}{1:02d}{2:02d}".format(
            *pioversion_to_intstr())]
    )

    return env.Program(
        join("$BUILD_DIR", env.subst("$PROGNAME")),
        env.LookupSources(
            "$BUILDSRC_DIR", "$PROJECTSRC_DIR", duplicate=False,
            src_filter=getenv("PLATFORMIO_SRC_FILTER",
                              env.get("SRC_FILTER", None))),
        LIBS=env.get("LIBS", []) + deplibs,
        LIBPATH=env.get("LIBPATH", []) + ["$BUILD_DIR"]
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


def IsFileWithExt(env, file_, ext):  # pylint: disable=W0613
    if basename(file_).startswith("."):
        return False
    for e in ext:
        if file_.endswith(".%s" % e):
            return True
    return False


def VariantDirWrap(env, variant_dir, src_dir, duplicate=True):
    DefaultEnvironment().Append(VARIANT_DIRS=[(variant_dir, src_dir)])
    env.VariantDir(variant_dir, src_dir, duplicate)


def LookupSources(env, variant_dir, src_dir, duplicate=True, src_filter=None):

    SRC_FILTER_PATTERNS_RE = re.compile(r"(\+|\-)<([^>]+)>")

    def _append_build_item(items, item, src_dir):
        if env.IsFileWithExt(item, SRC_BUILD_EXT + SRC_HEADER_EXT):
            items.add(item.replace(src_dir + sep, ""))

    def _match_sources(src_dir, src_filter):
        matches = set()
        # correct fs directory separator
        src_filter = src_filter.replace("/", sep).replace("\\", sep)
        for (action, pattern) in SRC_FILTER_PATTERNS_RE.findall(src_filter):
            items = set()
            for item in glob(join(src_dir, pattern)):
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

    sources = []
    variants = []

    src_dir = env.subst(src_dir)
    if src_dir.endswith(sep):
        src_dir = src_dir[:-1]

    for item in _match_sources(src_dir, src_filter or SRC_DEFAULT_FILTER):
        _reldir = dirname(item)
        _src_dir = join(src_dir, _reldir) if _reldir else src_dir
        _var_dir = join(variant_dir, _reldir) if _reldir else variant_dir

        if _var_dir not in variants:
            variants.append(_var_dir)
            env.VariantDirWrap(_var_dir, _src_dir, duplicate)

        if env.IsFileWithExt(item, SRC_BUILD_EXT):
            sources.append(env.File(join(_var_dir, basename(item))))

    return sources


def BuildFramework(env):
    if "FRAMEWORK" not in env or "uploadlazy" in COMMAND_LINE_TARGETS:
        return

    if env['FRAMEWORK'].lower() in ("arduino", "energia"):
        env.ConvertInoToCpp()

    for f in env['FRAMEWORK'].split(","):
        framework = f.strip().lower()
        if framework in env.get("BOARD_OPTIONS", {}).get("frameworks"):
            SConscript(
                env.subst(join("$PIOBUILDER_DIR", "scripts", "frameworks",
                               "%s.py" % framework))
            )
        else:
            Exit("Error: This board doesn't support %s framework!" %
                 framework)


def BuildLibrary(env, variant_dir, src_dir, src_filter=None):
    lib = env.Clone()
    return lib.Library(
        lib.subst(variant_dir),
        lib.LookupSources(variant_dir, src_dir, src_filter=src_filter)
    )


def BuildDependentLibraries(env, src_dir):  # pylint: disable=R0914

    INCLUDES_RE = re.compile(
        r"^\s*#include\s+(\<|\")([^\>\"\']+)(?:\>|\")", re.M)
    LIBSOURCE_DIRS = [env.subst(d) for d in env.get("LIBSOURCE_DIRS", [])]

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

                for ld in env.get("LIB_USE", []) + sorted(listdir(lsd_dir)):
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
                    if lib_name in env.get("LIB_IGNORE", []):
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
        for root, _, files in walk(src_dir, followlinks=True):
            for f in files:
                if env.IsFileWithExt(f, SRC_BUILD_EXT + SRC_HEADER_EXT):
                    state = _parse_includes(state, env.File(join(root, f)))
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

                    if env.subst("$LIB_DFCYCLIC").lower() == "true":
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


def exists(_):
    return True


def generate(env):
    env.AddMethod(BuildProgram)
    env.AddMethod(ProcessFlags)
    env.AddMethod(IsFileWithExt)
    env.AddMethod(VariantDirWrap)
    env.AddMethod(LookupSources)
    env.AddMethod(BuildFramework)
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildDependentLibraries)
    return env

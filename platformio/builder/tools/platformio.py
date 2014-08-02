# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import re
from os import getenv, listdir, walk
from os.path import isdir, isfile, join

from SCons.Script import SConscript, SConscriptChdir


def ProcessGeneral(env):
    corelibs = []
    if "BUILD_FLAGS" in env:
        env.MergeFlags(env['BUILD_FLAGS'])

    env.PrependENVPath(
        "PATH",
        join(env.subst("$PLATFORMTOOLS_DIR"), "toolchain", "bin")
    )

    if "FRAMEWORK" in env:
        SConscriptChdir(0)
        corelibs = SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts",
                                             "frameworks", "${FRAMEWORK}.py")),
                              exports="env")
    return corelibs


def BuildFirmware(env, corelibs):
    src = env.Clone()
    vdirs = src.VariantDirRecursive(
        join("$BUILD_DIR", "src"), join("$PROJECT_DIR", "src"))

    # build source's dependent libs
    deplibs = []
    for vdir in vdirs:
        deplibs += src.BuildDependentLibraries(vdir)

    src.MergeFlags(getenv("PIOSRCBUILD_FLAGS", "$SRCBUILD_FLAGS"))

    return src.Program(
        join("$BUILD_DIR", "firmware"),
        [src.GlobCXXFiles(vdir) for vdir in vdirs],
        LIBS=deplibs + corelibs,
        LIBPATH="$BUILD_DIR",
        PROGSUFFIX=".elf")


def GlobCXXFiles(env, path):
    files = []
    for suff in ["*.c", "*.cpp", "*.S"]:
        _list = env.Glob(join(path, suff))
        if _list:
            files += _list
    return files


def BuildLibrary(env, variant_dir, library_dir):
    lib = env.Clone()
    vdirs = lib.VariantDirRecursive(variant_dir, library_dir)
    return lib.Library(
        lib.subst(variant_dir),
        [lib.GlobCXXFiles(vdir) for vdir in vdirs]
    )


def BuildDependentLibraries(env, src_dir):
    libs = []
    deplibs = env.GetDependentLibraries(src_dir)
    env.Append(CPPPATH=[join("$BUILD_DIR", l) for (l, _) in deplibs])

    for (libname, lsd_dir) in deplibs:
        lib = env.BuildLibrary(
            join("$BUILD_DIR", libname), join(lsd_dir, libname))
        env.Clean(libname, lib)
        libs.append(lib)
    return libs


def GetDependentLibraries(env, src_dir):
    includes = {}
    regexp = re.compile(r"^\s?#include\s+(?:\<|\"|\')([^\>\"\']+)(?:\>|\"|\')",
                        re.M)
    for node in env.GlobCXXFiles(src_dir):
        env.ParseIncludesRecurive(regexp, node, includes)

    includes = sorted(includes.items(), key=lambda s: s[0])
    return set([(i[1][1], i[1][2]) for i in includes])


def ParseIncludesRecurive(env, regexp, source_file, includes):
    matches = regexp.findall(source_file.get_text_contents())
    for inc_name in matches:
        if inc_name in includes:
            continue
        for lsd_dir in env['LIBSOURCE_DIRS']:
            lsd_dir = env.subst(lsd_dir)
            if not isdir(lsd_dir):
                continue
            for libname in listdir(lsd_dir):
                inc_path = join(lsd_dir, libname, inc_name)
                if not isfile(inc_path):
                    continue
                includes[inc_name] = (len(includes) + 1, libname, lsd_dir)
                env.ParseIncludesRecurive(regexp, env.File(inc_path), includes)


def VariantDirRecursive(env, variant_dir, src_dir, duplicate=True):
    # add root dir by default
    variants = [variant_dir]
    env.VariantDir(variant_dir, src_dir, duplicate)
    for root, dirnames, _ in walk(env.subst(src_dir)):
        if not dirnames:
            continue
        for dn in dirnames:
            env.VariantDir(join(variant_dir, dn), join(root, dn), duplicate)
            variants.append(join(variant_dir, dn))
    return variants


def ParseBoardOptions(env, path, name):
    path = env.subst(path)
    name = env.subst(name)
    if not isfile(path):
        env.Exit("Invalid path to boards.txt -> %s" % path)

    data = {}
    with open(path) as f:
        for line in f:
            if not line.strip() or line[0] == "#":
                continue

            _group = line[:line.index(".")]
            _cpu = name[len(_group):]
            line = line[len(_group)+1:].strip()
            if _group != name[:len(_group)]:
                continue
            elif "menu.cpu." in line:
                if _cpu not in line:
                    continue
                else:
                    line = line[len(_cpu)+10:]

            if "=" in line:
                opt, value = line.split("=", 1)
                data[opt] = value
    if not data:
        env.Exit("Unknown Board '%s'" % name)
    else:
        return data


def exists(_):
    return True


def generate(env):
    env.AddMethod(ProcessGeneral)
    env.AddMethod(BuildFirmware)
    env.AddMethod(GlobCXXFiles)
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildDependentLibraries)
    env.AddMethod(GetDependentLibraries)
    env.AddMethod(ParseIncludesRecurive)
    env.AddMethod(VariantDirRecursive)
    env.AddMethod(ParseBoardOptions)
    return env

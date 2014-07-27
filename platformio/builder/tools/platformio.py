# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import re
from os.path import isdir, isfile, join



def BuildLibrary(env, variant_dir, library_dir):
    lib = env.Clone()
    vdirs = lib.VariantDirRecursive(variant_dir, library_dir)
    return lib.Library(
        lib.subst(variant_dir),
        [lib.GlobCXXFiles(vdir) for vdir in vdirs]
    )


def BuildDependentLibraries(env, src_dir):
    libs = []
    for deplibfile in env.GetDependentLibraries(src_dir):
        for lsd_dir in env['LIBSOURCE_DIRS']:
            lsd_dir = env.subst(lsd_dir)
            if not isdir(lsd_dir):
                continue
            for libname in listdir(lsd_dir):
                if not isfile(join(lsd_dir, libname, deplibfile)):
                    continue
                _libbuild_dir = join("$BUILD_DIR", libname)
                env.Append(CPPPATH=[_libbuild_dir])
                libs.append(
                    env.BuildLibrary(_libbuild_dir, join(lsd_dir, libname)))
    return libs


def BuildFirmware(env, libslist):
    src = env.Clone()
    vdirs = src.VariantDirRecursive(
        join("$BUILD_DIR", "src"), join("$PROJECT_DIR", "src"))

    # build source's dependent libs
    for vdir in vdirs:
        _libs = src.BuildDependentLibraries(vdir)
        if _libs:
            libslist += _libs

    src.MergeFlags(getenv("PIOSRCBUILD_FLAGS", "$SRCBUILD_FLAGS"))

    return src.Program(
        join("$BUILD_DIR", "firmware"),
        [src.GlobCXXFiles(vdir) for vdir in vdirs],
        LIBS=libslist,
        LIBPATH="$BUILD_DIR",
        PROGSUFFIX=".elf")


def GlobCXXFiles(env, path):
    files = []
    for suff in ["*.c", "*.cpp", "*.S"]:
        _list = env.Glob(join(path, suff))
        if _list:
            files += _list
    return files


def GetDependentLibraries(env, src_dir):
    deplibs = []
    regexp = re.compile(r"^#include\s+<([^>]+)>", re.M)
    for node in env.GlobCXXFiles(src_dir):
        deplibs += regexp.findall(node.get_text_contents())
    return deplibs


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
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildDependentLibraries)
    env.AddMethod(BuildFirmware)
    env.AddMethod(GlobCXXFiles)
    env.AddMethod(GetDependentLibraries)
    env.AddMethod(VariantDirRecursive)
    env.AddMethod(ParseBoardOptions)
    return env

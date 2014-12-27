# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
import re
from os import getenv, listdir, remove, walk
from os.path import basename, isdir, isfile, join
from time import sleep

from SCons.Script import SConscript, SConscriptChdir
from serial import Serial


def ProcessGeneral(env):
    corelibs = []
    if "BUILD_FLAGS" in env:
        env.MergeFlags(env['BUILD_FLAGS'])

    if "FRAMEWORK" in env:
        if env['FRAMEWORK'] in ("arduino", "energia"):
            env.ConvertInoToCpp()
        SConscriptChdir(0)
        corelibs = SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts",
                                             "frameworks", "${FRAMEWORK}.py")),
                              exports="env")
    return corelibs


def BuildFirmware(env, corelibs):
    src = env.Clone()
    vdirs = src.VariantDirRecursive(
        join("$BUILD_DIR", "src"), join("$PROJECT_DIR", "src"))

    # build dependent libs
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

    for (libname, inc_dir) in deplibs:
        lib = env.BuildLibrary(
            join("$BUILD_DIR", libname), inc_dir)
        env.Clean(libname, lib)
        libs.append(lib)
    return libs


def GetDependentLibraries(env, src_dir):
    includes = {}
    regexp = re.compile(r"^\s*#include\s+(?:\<|\")([^\>\"\']+)(?:\>|\")", re.M)
    for node in env.GlobCXXFiles(src_dir):
        env.ParseIncludesRecurive(regexp, node, includes)
    includes = sorted(includes.items(), key=lambda s: s[0])

    result = []
    for i in includes:
        item = (i[1][1], i[1][2])
        if item in result:
            continue
        result.append(item)
    return result


def ParseIncludesRecurive(env, regexp, source_file, includes):
    matches = regexp.findall(source_file.get_text_contents())
    for inc_fname in matches:
        if inc_fname in includes:
            continue
        for lsd_dir in env['LIBSOURCE_DIRS']:
            lsd_dir = env.subst(lsd_dir)
            if not isdir(lsd_dir):
                continue
            for libname in listdir(lsd_dir):
                inc_dir = join(lsd_dir, libname)
                inc_file = join(inc_dir, inc_fname)
                if not isfile(inc_file):
                    # if source code is in "src" dir
                    inc_dir = join(lsd_dir, libname, "src")
                    inc_file = join(inc_dir, inc_fname)
                if not isfile(inc_file):
                    continue
                includes[inc_fname] = (len(includes) + 1, libname, inc_dir)
                env.ParseIncludesRecurive(regexp, env.File(inc_file), includes)


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


def ConvertInoToCpp(env):

    def delete_tmpcpp(files):
        for f in files:
            remove(f)

    tmpcpp = []
    items = (env.Glob(join("$PROJECT_DIR", "src", "*.ino")) +
             env.Glob(join("$PROJECT_DIR", "src", "*.pde")))
    for item in items:
        cppfile = item.get_path()[:-3] + "cpp"
        if isfile(cppfile):
            continue
        ino_contents = item.get_text_contents()

        re_includes = re.compile(r"^(#include\s+(?:\<|\")[^\r\n]+)",
                                 re.M | re.I)
        includes = re_includes.findall(ino_contents)
        prototypes = re.findall(
            r"""^(
            (?:\s*[a-z_\d]+){1,2}       # return type
            \s+[a-z_\d]+\s*             # name of prototype
            \([a-z_,\.\*\&\[\]\s\d]*\)  # args
            )\s*\{                      # must end with {
            """,
            ino_contents,
            re.X | re.M | re.I
        )
        # print includes, prototypes

        # disable previous includes
        ino_contents = re_includes.sub(r"//\1", ino_contents)

        # create new temporary C++ valid file
        with open(cppfile, "w") as f:
            f.write("#include <Arduino.h>\n")
            if includes:
                f.write("%s\n" % "\n".join(includes))
            if prototypes:
                f.write("%s;\n" % ";\n".join(prototypes))
            f.write("#line 1 \"%s\"\n" % basename(item.path))
            f.write(ino_contents)
        tmpcpp.append(cppfile)

    if tmpcpp:
        atexit.register(delete_tmpcpp, tmpcpp)


def FlushSerialBuffer(env, port):
    s = Serial(env.subst(port))
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


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
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(FlushSerialBuffer)
    return env

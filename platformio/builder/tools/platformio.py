# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import walk
from os.path import isfile, join
from time import sleep

from serial import Serial


def BuildCoreLibrary(env):
    corelib = env.Clone()
    vdirs = corelib.VariantDirRecursive("$BUILDCORE_DIR", "$PLATFORMCORE_DIR")
    return corelib.Library(
        corelib.subst("$BUILDCORE_DIR"),
        [corelib.GlobCXXFiles(vdir) for vdir in vdirs]
    )


def BuildFirmware(env, liblist):
    src = env.Clone()
    vdirs = src.VariantDirRecursive("$BUILDSRC_DIR",
                                    join("$PROJECT_DIR", "src"))
    return src.Program(
        join("$BUILD_DIR", "firmware"),
        [src.GlobCXXFiles(vdir) for vdir in vdirs],
        LIBS=liblist,
        LIBPATH="$BUILD_DIR",
        PROGSUFFIX=".elf")


def GlobCXXFiles(env, path):
    files = []
    for suff in ["*.c", "*.cpp", "*.S"]:
        _list = env.Glob(join(path, suff))
        if _list:
            files += _list
    return files


def VariantDirRecursive(env, variant_dir, src_dir, duplicate=True):
    # add root dir by default
    variants = [variant_dir]
    env.VariantDir(variant_dir, src_dir, duplicate)
    for root, dirnames, filenames in walk(env.subst(src_dir)):
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
    _namelen = len(name) + 1
    with open(path) as f:
        for line in f:
            if line[0:_namelen] != name + ".":
                continue
            line = line[_namelen:].strip()
            opt, value = line.split("=", 1)
            data[opt] = value
    if not data:
        env.Exit("Unknown Board '%s'" % name)
    else:
        return data


def ResetDevice(env):
    """ Pulse the DTR line and flush serial buffer """
    s = Serial(env.subst("$UPLOAD_PORT"))
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


def exists(env):
    return True


def generate(env):
    env.AddMethod(BuildCoreLibrary)
    env.AddMethod(BuildFirmware)
    env.AddMethod(GlobCXXFiles)
    env.AddMethod(VariantDirRecursive)
    env.AddMethod(ParseBoardOptions)
    env.AddMethod(ResetDevice)
    return env

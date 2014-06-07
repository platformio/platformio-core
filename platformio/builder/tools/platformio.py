# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import walk
from os.path import isfile, join
from time import sleep

from serial import Serial


def BuildLibrary(env, variant_dir, library_dir):
    lib = env.Clone()
    vdirs = lib.VariantDirRecursive(variant_dir, library_dir)
    return lib.Library(
        lib.subst(variant_dir),
        [lib.GlobCXXFiles(vdir) for vdir in vdirs]
    )


def BuildFirmware(env, libslist):
    src = env.Clone()
    vdirs = src.VariantDirRecursive(join("$BUILD_DIR", "src"),
                                    join("$PROJECT_DIR", "src"))
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


def exists(_):
    return True


def generate(env):
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildFirmware)
    env.AddMethod(GlobCXXFiles)
    env.AddMethod(VariantDirRecursive)
    env.AddMethod(ParseBoardOptions)
    env.AddMethod(ResetDevice)
    return env

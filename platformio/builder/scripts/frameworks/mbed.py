# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
mbed

The mbed framework The mbed SDK has been designed to provide enough
hardware abstraction to be intuitive and concise, yet powerful enough to
build complex projects. It is built on the low-level ARM CMSIS APIs,
allowing you to code down to the metal if needed. In addition to RTOS,
USB and Networking libraries, a cookbook of hundreds of reusable
peripheral and module libraries have been built on top of the SDK by
the mbed Developer Community.

http://mbed.org/
"""

import re
import xml.etree.ElementTree as ElementTree
from binascii import crc32
from os import walk
from os.path import basename, isfile, join, normpath

from SCons.Script import DefaultEnvironment, Exit

env = DefaultEnvironment()

BOARD_OPTS = env.get("BOARD_OPTIONS", {}).get("build", {})

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-mbed")
)

MBED_VARIANTS = {
    "blueboard_lpc11u24": "LPC11U24",
    "dipcortexm0": "LPC11U24",
    "seeeduinoArchPro": "ARCH_PRO",
    "ubloxc027": "UBLOX_C027",
    "lpc1114fn28": "LPC1114",
    "lpc11u35": "LPC11U35_401",
    "mbuino": "LPC11U24",
    "nrf51_mkit": "NRF51822",
    "seeedTinyBLE": "SEEED_TINY_BLE",
    "redBearLab": "RBLAB_NRF51822",
    "nrf51-dt": "NRF51_DK",
    "redBearLabBLENano": "RBLAB_NRF51822",
    "wallBotBLE": "NRF51822",
    "frdm_kl25z": "KL25Z",
    "frdm_kl46z": "KL46Z",
    "frdm_k64f": "K64F",
    "frdm_kl05z": "KL05Z",
    "frdm_k20d50m": "K20D50M",
    "frdm_k22f": "K22F",
    "teensy31": "TEENSY3_1",
    "dfcm_nnn40": "DELTA_DFCM_NNN40"
}

MBED_LIBS_MAP = {
    "dsp": {"ar": ["dsp", "cmsis_dsp"]},
    "eth": {"ar": ["eth"], "deps": ["rtos"]},
    "fat": {"ar": ["fat"]},
    "rtos": {"ar": ["rtos", "rtx"]},
    "usb": {"ar": ["USBDevice"]},
    "usb_host": {"ar": ["USBHost"]}
}


def get_mbedlib_includes():
    result = []
    for lib in MBED_LIBS_MAP.keys():
        includes = []
        lib_dir = join(env.subst("$PLATFORMFW_DIR"), "libs", lib)
        for _, _, files in walk(lib_dir):
            for libfile in files:
                if libfile.endswith(".h"):
                    includes.append(libfile)
        result.append((lib, set(includes)))
    return result


def get_used_mbedlibs():
    re_includes = re.compile(r"^(#include\s+(?:\<|\")([^\r\n\"]+))",
                             re.M | re.I)
    srcincs = []
    for root, _, files in walk(env.get("PROJECTSRC_DIR")):
        for pfile in files:
            if not any([pfile.endswith(ext) for ext in (".h", ".c", ".cpp")]):
                continue
            with open(join(root, pfile)) as fp:
                srcincs.extend([i[1] for i in re_includes.findall(fp.read())])
    srcincs = set(srcincs)

    result = {}
    for libname, libincs in get_mbedlib_includes():
        if libincs & srcincs and libname not in result:
            result[libname] = MBED_LIBS_MAP[libname]

    return result


def add_mbedlib(libname, libar):
    if libar in env.get("LIBS"):
        return

    lib_dir = join(env.subst("$PLATFORMFW_DIR"), "libs", libname)
    if not isfile(join(lib_dir, "TARGET_%s" % variant,
                       "TOOLCHAIN_GCC_ARM", "lib%s.a" % libar)):
        Exit("Error: %s board doesn't support %s library!" %
             (env.get("BOARD"), libname))

    env.Append(
        LIBPATH=[
            join(env.subst("$PLATFORMFW_DIR"), "libs", libname,
                 "TARGET_%s" % variant, "TOOLCHAIN_GCC_ARM")
        ],
        LIBS=[libar]
    )

    sysincdirs = (
        "eth",
        "include",
        "ipv4",
        "lwip-eth",
        "lwip-sys"
    )

    for root, _, files in walk(lib_dir):
        if (not any(f.endswith(".h") for f in files) and
                basename(root) not in sysincdirs):
            continue
        var_dir = join("$BUILD_DIR", "FrameworkMbed%sInc%d" %
                       (libname.upper(), crc32(root)))
        if var_dir in env.get("CPPPATH"):
            continue
        env.VariantDirWrap(var_dir, root)
        env.Append(CPPPATH=[var_dir])


def parse_eix_file(filename):
    result = {}
    paths = (
        ("CFLAGS", "./Target/Source/CC/Switch"),
        ("CXXFLAGS", "./Target/Source/CPPC/Switch"),
        ("CPPDEFINES", "./Target/Source/Symbols/Symbol"),
        ("FILES", "./Target/Files/File"),
        ("LINKFLAGS", "./Target/Source/LD/Switch"),
        ("OBJFILES", "./Target/Source/Addobjects/Addobject"),
        ("LIBPATH", "./Target/Linker/Librarypaths/Librarypath"),
        ("STDLIBS", "./Target/Source/Syslibs/Library"),
        ("LDSCRIPT_PATH", "./Target/Source/Scriptfile"),
        ("CPPPATH", "./Target/Compiler/Includepaths/Includepath")
    )

    tree = ElementTree.parse(filename)

    for (key, path) in paths:
        if key not in result:
            result[key] = []

        for node in tree.findall(path):
            _nkeys = node.keys()
            result[key].append(
                node.get(_nkeys[0]) if len(_nkeys) == 1 else node.attrib)

    return result


def get_build_flags(data):
    flags = {}
    cflags = set(data.get("CFLAGS", []))
    cxxflags = set(data.get("CXXFLAGS", []))
    cppflags = set(cflags & cxxflags)
    flags['CPPFLAGS'] = list(cppflags)
    flags['CXXFLAGS'] = list(cxxflags - cppflags)
    flags['CFLAGS'] = list(cflags - cppflags)
    return flags


def _mbed_whole_archive_hook(flags):
    if (not isinstance(flags, list) or
            env.get("BOARD_OPTIONS", {}).get("platform") != "ststm32"):
        return flags

    for pos, flag in enumerate(flags[:]):
        if isinstance(flag, basestring):
            continue
        flags.insert(pos, "-Wl,-whole-archive")
        flags.insert(pos + 2, "-Wl,-no-whole-archive")

    return flags


board_type = env.subst("$BOARD")
variant = MBED_VARIANTS[
    board_type] if board_type in MBED_VARIANTS else board_type.upper()
eixdata = parse_eix_file(
    join(env.subst("$PLATFORMFW_DIR"), "variant", variant, "%s.eix" % variant))

build_flags = get_build_flags(eixdata)
variant_dir = join("$PLATFORMFW_DIR", "variant", variant)

env.Replace(
    _mbed_whole_archive_hook=_mbed_whole_archive_hook,
    _LIBFLAGS="${_mbed_whole_archive_hook(%s)}" % env.get("_LIBFLAGS")[2:-1],
    CPPFLAGS=build_flags.get("CPPFLAGS", []),
    CFLAGS=build_flags.get("CFLAGS", []),
    CXXFLAGS=build_flags.get("CXXFLAGS", []),
    LINKFLAGS=eixdata.get("LINKFLAGS", []),
    CPPDEFINES=[define for define in eixdata.get("CPPDEFINES", [])],
    LDSCRIPT_PATH=normpath(
        join(variant_dir, eixdata.get("LDSCRIPT_PATH")[0]))
)

# restore external build flags
env.ProcessFlags()

# Hook for K64F and K22F
if board_type in ("frdm_k22f", "frdm_k64f"):
    env.Append(
        LINKFLAGS=["-Wl,--start-group"]
    )

for lib_path in eixdata.get("CPPPATH"):
    _vdir = join("$BUILD_DIR", "FrameworkMbedInc%d" % crc32(lib_path))
    env.VariantDirWrap(_vdir, join(variant_dir, lib_path))
    env.Append(CPPPATH=[_vdir])

env.Append(
    LIBPATH=[join(variant_dir, lib_path)
             for lib_path in eixdata.get("LIBPATH", [])
             if lib_path.startswith("mbed")]
)

#
# Target: Build mbed Library
#

libs = [l for l in eixdata.get("STDLIBS", []) if l not in env.get("LIBS")]
libs.extend(["mbed", "c", "gcc"])

libs.append(env.Library(
    join("$BUILD_DIR", "FrameworkMbed"),
    [join(variant_dir, f)
     for f in eixdata.get("OBJFILES", [])]
))

env.Append(LIBS=libs)

for _libname, _libdata in get_used_mbedlibs().iteritems():
    for _libar in _libdata['ar']:
        add_mbedlib(_libname, _libar)
    if "deps" not in _libdata:
        continue
    for libdep in _libdata['deps']:
        for _libar in MBED_LIBS_MAP[libdep]['ar']:
            add_mbedlib(libdep, _libar)

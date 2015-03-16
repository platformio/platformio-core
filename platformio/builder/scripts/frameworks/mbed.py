# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
The mbed framework The mbed SDK has been designed to provide enough
hardware abstraction to be intuitive and concise, yet powerful enough to
build complex projects. It is built on the low-level ARM CMSIS APIs,
allowing you to code down to the metal if needed. In addition to RTOS,
USB and Networking libraries, a cookbook of hundreds of reusable
peripheral and module libraries have been built on top of the SDK by
the mbed Developer Community.

http://mbed.org/
"""

import xml.etree.ElementTree as ElementTree
from binascii import crc32
from os.path import join, normpath

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

BOARD_OPTS = env.get("BOARD_OPTIONS", {}).get("build", {})

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-mbed")
)

MBED_VARIANTS = {
    "stm32f3discovery": "DISCO_F303VC",
    "stm32f4discovery": "DISCO_F407VG",
    "stm32f429discovery": "DISCO_F429ZI",
    "blueboard_lpc11u24": "LPC11U24",
    "dipcortexm0": "LPC11U24",
    "seeeduinoArchPro": "ARCH_PRO",
    "ubloxc027": "UBLOX_C027",
    "lpc1114fn28": "LPC1114",
    "lpc11u35": "LPC11U35_401",
    "mbuino": "LPC11U24",
    "nrf51_mkit": "NRF51822",
    "redBearLab": "NRF51822",
    "nrf51-dt": "NRF51_DK",
    "redBearLabBLENano": "NRF51822",
    "wallBotBLE": "NRF51822",
    "frdm_kl25z": "KL25Z",
    "frdm_kl46z": "KL46Z",
    "frdm_k64f": "K64F",
    "frdm_kl05z": "KL05Z",
    "frdm_k20d50m": "K20D50M",
    "frdm_k22f": "K22F"
}


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

board_type = env.subst("$BOARD")
variant = MBED_VARIANTS[
    board_type] if board_type in MBED_VARIANTS else board_type.upper()
eixdata = parse_eix_file(
    join(env.subst("$PLATFORMFW_DIR"), "variant", variant, "%s.eix" % variant))

build_flags = get_build_flags(eixdata)
variant_dir = join("$PLATFORMFW_DIR", "variant", variant)

env.Replace(
    CPPFLAGS=build_flags.get("CPPFLAGS", []),
    CFLAGS=build_flags.get("CFLAGS", []),
    CXXFLAGS=build_flags.get("CXXFLAGS", []),
    LINKFLAGS=eixdata.get("LINKFLAGS", []),
    CPPDEFINES=[define for define in eixdata.get("CPPDEFINES", [])],
    LDSCRIPT_PATH=normpath(
        join(variant_dir, eixdata.get("LDSCRIPT_PATH")[0]))
)

# Hook for K64F and K22F
if board_type in ("frdm_k22f", "frdm_k64f"):
    env.Append(
        LINKFLAGS=["-Wl,--start-group"]
    )

for lib_path in eixdata.get("CPPPATH"):
    _vdir = join("$BUILD_DIR", "FrameworkMbedInc%d" % crc32(lib_path))
    env.VariantDir(_vdir, join(variant_dir, lib_path))
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
libs.append("mbed")

libs.append(env.Library(
    join("$BUILD_DIR", "FrameworkMbed"),
    [join(variant_dir, f)
     for f in eixdata.get("OBJFILES", [])]
))

env.Append(LIBS=libs)

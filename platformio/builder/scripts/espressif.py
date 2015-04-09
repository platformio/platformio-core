# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Espressif MCUs
"""

import os
from os.path import join
from platform import system

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()


env = DefaultEnvironment()

env.Replace(
    AR="xtensa-lx106-elf-ar",
    AS="xtensa-lx106-elf-as",
    CC="xtensa-lx106-elf-gcc",
    CXX="xtensa-lx106-elf-g++",
    OBJCOPY="xtensa-lx106-elf-objcopy",
    RANLIB="xtensa-lx106-elf-ranlib",
    SIZETOOL="xtensa-lx106-elf-size",

    ARFLAGS=["rcs"],

    ASPPFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=[
        "-std=c99",
        "-Wpointer-arith",
        "-Wno-implicit-function-declaration",
        "-Wl,-EL",
        "-fno-inline-functions",
        "-nostdlib"
    ],

    CPPFLAGS=[
        "-Os",  # optimize for size
        "-mlongcalls",
        "-mtext-section-literals",
        "-MMD"  # output dependancy info
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=c++11"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU",
        "__ets__",
        "ICACHE_FLASH"
    ],

    LINKFLAGS=[
        "-nostdlib",
        "-Wl,--no-check-sections",
        "-u", "call_user_start",
        "-Wl,-static"
    ],

    SIZEPRINTCMD='"$SIZETOOL" -B -d $SOURCES',

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-esptool", "esptool.py"),
    UPLOADERFLAGS=[
        "--port", "$UPLOAD_PORT",
        "--baud", "$UPLOAD_SPEED",
        "write_flash",
        "0x00000", join("$BUILD_DIR", "firmware.elf-0x00000.bin"),
        "0x40000", join("$BUILD_DIR", "firmware.elf-0x40000.bin")
    ],
    UPLOADCMD='python $UPLOADER $UPLOADERFLAGS'
)

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "python", "$UPLOADER", "elf2image", "$SOURCES"
            ]),
            suffix=".bin"
        )
    )
)

if system() == "Windows":
    paths = []
    for path in os.environ['PATH'].split(";"):
        if "python" in path.lower():
            paths.append(path)

    env.AppendENVPath(
        "PATH", ";".join(paths)
    )

#
# Configure SDK
#

if "FRAMEWORK" not in env:
    env.Append(
        CPPPATH=[
            join("$PIOPACKAGES_DIR", "sdk-esp8266", "include"),
            "$PROJECTSRC_DIR"
        ],
        LIBPATH=[join("$PIOPACKAGES_DIR", "sdk-esp8266", "lib")]
    )
    env.Replace(
        LDSCRIPT_PATH=join(
            "$PIOPACKAGES_DIR", "sdk-esp8266", "ld", "eagle.app.v6.ld"),
        LIBS=["c", "gcc", "phy", "pp", "net80211", "lwip", "wpa", "main",
              "json", "upgrade", "smartconfig", "at", "ssl"]
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware()

#
# Target: Build the .hex
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.bin")
else:
    target_firm = env.ElfToBin(target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload firmware
#

upload = env.Alias(["upload", "uploadlazy"], target_firm,
                   [BeforeUpload, "$UPLOADCMD"])
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])

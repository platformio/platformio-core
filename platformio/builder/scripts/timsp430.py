# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Texas Instruments
    MSP430 Ultra-Low Power 16-bit microcontrollers
"""

from os.path import join

from SCons.Script import (AlwaysBuild, Builder, Default, DefaultEnvironment,
                          SConscript, SConscriptChdir)

from platformio.util import get_system

env = DefaultEnvironment()

env.Replace(
    AR="msp430-ar",
    AS="msp430-gcc",
    CC="msp430-gcc",
    CXX="msp430-g++",
    OBJCOPY="msp430-objcopy",
    RANLIB="msp430-ranlib",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "-assembler-with-cpp",
        "-mmcu=$BOARD_MCU"
    ],

    CCFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-MMD",  # output dependancy info
        "-mmcu=$BOARD_MCU"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU"
    ],

    LINK="$CC",
    LINKFLAGS=[
        "-Os",
        "-mmcu=$BOARD_MCU",
        "-Wl,-gc-sections,-u,main"
    ],

    UPLOADER=join("$PLATFORMTOOLS_DIR", "mspdebug", "mspdebug"),
    UPLOADERFLAGS=[
        "$UPLOAD_PROTOCOL" if get_system() != "windows32" else "tilib",
        "--force-reset"
    ],
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS "prog $SOURCES"'
)

if "BUILD_FLAGS" in env:
    env.MergeFlags(env['BUILD_FLAGS'])

env.Append(
    BUILDERS=dict(
        ElfToHex=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "-R",
                ".eeprom",
                "$SOURCES",
                "$TARGET"]),
            suffix=".hex"
        )
    )
)

env.PrependENVPath(
    "PATH",
    join(env.subst("$PLATFORMTOOLS_DIR"), "toolchain", "bin")
)

BUILT_LIBS = []

#
# Process framework script
#

if "FRAMEWORK" in env:
    SConscriptChdir(0)
    flibs = SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts",
                                      "frameworks", "${FRAMEWORK}.py")),
                       exports="env")
    BUILT_LIBS += flibs


#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(BUILT_LIBS + ["m"])

#
# Target: Build the .hex
#

target_hex = env.ElfToHex(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Upload firmware
#

upload = env.Alias("upload", target_hex, ["$UPLOADCMD"])
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_elf, target_hex])

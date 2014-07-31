# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Texas Instruments
    MSP430 Ultra-Low Power 16-bit microcontrollers
"""

from os.path import join
from platform import system

from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default,
                          DefaultEnvironment)

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
        "$UPLOAD_PROTOCOL" if system() != "Windows" else "tilib",
        "--force-reset"
    ],
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS "prog $SOURCES"'
)

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

BUILT_LIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(BUILT_LIBS + ["m"])

#
# Target: Build the .hex
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_hex = join("$BUILD_DIR", "firmware.hex")
else:
    target_hex = env.ElfToHex(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Upload firmware
#

upload = env.Alias(["upload", "uploadlazy"], target_hex, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#

Default(target_hex)

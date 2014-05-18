# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Texas Instruments
    MSP430 Ultra-Low Power 16-bit microcontrollers

    Fully compatible with Energia programming language (based on Wiring).
"""

from os.path import join

from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

#
# SETUP ENVIRONMENT
#

env = DefaultEnvironment()

BOARD_OPTIONS = env.ParseBoardOptions(join("$PLATFORM_DIR", "boards.txt"),
                                      "${BOARD}")
env.Replace(
    # See https://github.com/energia/Energia/blob/master/app/src/
    # processing/app/Base.java#L45
    ARDUINO_VERSION="101",
    ENERGIA_VERSION="12",

    BOARD_MCU=BOARD_OPTIONS['build.mcu'],
    BOARD_F_CPU=BOARD_OPTIONS['build.f_cpu'],

    AR="msp430-ar",
    AS="msp430-as",
    CC="msp430-gcc",
    CXX="msp430-g++",
    OBJCOPY="msp430-objcopy",
    RANLIB="msp430-ranlib",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-assembler-with-cpp",
        "-mmcu=$BOARD_MCU",
        "-DF_CPU=$BOARD_F_CPU",
        "-DARDUINO=$ARDUINO_VERSION",
        "-DENERGIA=$ENERGIA_VERSION"
    ],
    CCFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-mmcu=$BOARD_MCU",
        "-DF_CPU=$BOARD_F_CPU",
        "-MMD",  # output dependancy info
        "-DARDUINO=$ARDUINO_VERSION",
        "-DENERGIA=$ENERGIA_VERSION"
    ],

    LINK="$CC",
    LINKFLAGS=[
        "-Os",
        "-mmcu=$BOARD_MCU",
        "-Wl,-gc-sections,-u,main"
    ],

    CPPPATH=[
        "$PLATFORMCORE_DIR",
        join("$PLATFORM_DIR", "variants", BOARD_OPTIONS['build.variant'])
    ],

    UPLOADER=(join("$PLATFORMTOOLS_DIR", "msp430", "mspdebug", "mspdebug")),
    UPLOADERFLAGS=[
        BOARD_OPTIONS['upload.protocol'],
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

env.PrependENVPath(
    "PATH",
    join(env.subst("$PLATFORMTOOLS_DIR"), "msp430", "bin")
)


#
# Target: Build Core Library
#

target_corelib = env.BuildCoreLibrary()


#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware([target_corelib, "m"])


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

Default([target_corelib, target_elf, target_hex])

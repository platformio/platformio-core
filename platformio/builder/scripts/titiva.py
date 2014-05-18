# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Texas Instruments
    Tiva C Series ARM Cortex-M4 microcontrollers.

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
    ARDUINO_VERSION="101",
    ENERGIA_VERSION="12",

    BOARD_MCU=BOARD_OPTIONS['build.mcu'],
    BOARD_F_CPU=BOARD_OPTIONS['build.f_cpu'],

    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-assembler-with-cpp",
        "-Wall",
        "-mthumb",
        "-mcpu=cortex-m4",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fsingle-precision-constant",
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
        "-Wall",
        "-mthumb",
        "-mcpu=cortex-m4",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fsingle-precision-constant",
        "-DF_CPU=$BOARD_F_CPU",
        "-MMD",  # output dependancy info
        "-DARDUINO=$ARDUINO_VERSION",
        "-DENERGIA=$ENERGIA_VERSION"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions"
    ],

    LINKFLAGS=[
        "-Os",
        "-nostartfiles",
        "-nostdlib",
        "-Wl,--gc-sections",
        "-T", join("$PLATFORMCORE_DIR", BOARD_OPTIONS['ldscript']),
        "-Wl,--entry=ResetISR",
        "-mthumb",
        "-mcpu=cortex-m4",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fsingle-precision-constant"
    ],

    CPPPATH=[
        "$PLATFORMCORE_DIR",
        join("$PLATFORM_DIR", "variants", BOARD_OPTIONS['build.variant'])
    ],

    UPLOADER="lm4flash",
    UPLOADCMD="$UPLOADER $SOURCES"
)

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"]),
            suffix=".hex"
        )
    )
)

env.PrependENVPath(
    "PATH",
    join(env.subst("$PLATFORMTOOLS_DIR"), "lm4f", "bin")
)


#
# Target: Build Core Library
#

target_corelib = env.BuildCoreLibrary()


#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware([target_corelib, "c", "gcc", "m"])


#
# Target: Build the .bin file
#

target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)


#
# Target: Upload firmware
#

upload = env.Alias("upload", target_bin, ["$UPLOADCMD"])
AlwaysBuild(upload)


#
# Target: Define targets
#

Default([target_corelib, target_elf, target_bin])

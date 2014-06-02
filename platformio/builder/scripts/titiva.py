# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Texas Instruments
    Tiva C Series ARM Cortex-M4 microcontrollers.
"""

from os.path import join

from SCons.Script import (AlwaysBuild, Builder, Default, DefaultEnvironment,
                          SConscript, SConscriptChdir)


env = DefaultEnvironment()

env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "-assembler-with-cpp",
        "-Wall",
        "-mthumb",
        "-mcpu=cortex-m4",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fsingle-precision-constant",
        "-DF_CPU=$BOARD_F_CPU"
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
        "-MMD",  # output dependancy info
        "-DF_CPU=$BOARD_F_CPU"
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
        "-Wl,--entry=ResetISR",
        "-mthumb",
        "-mcpu=cortex-m4",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fsingle-precision-constant"
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

target_elf = env.BuildFirmware(BUILT_LIBS + ["c", "gcc", "m"])


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

Default([target_elf, target_bin])

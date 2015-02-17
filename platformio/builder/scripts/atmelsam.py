# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel SAM series of microcontrollers
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)

from platformio.util import get_serialports

env = DefaultEnvironment()

env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-gcc",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-c",
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "assembler-with-cpp",
        "-Wall",
        "-mthumb",
        "-mcpu=${BOARD_OPTIONS['build']['mcu']}"
    ],

    CPPFLAGS=[
        "-g",   # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-fdata-sections",
        "-ffunction-sections",  # place each function in its own section
        "-Wall",
        "-MMD",  # output dependancy info
        "-mcpu=${BOARD_OPTIONS['build']['mcu']}",
        "-mthumb",
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-nostdlib"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-felide-constructors",
        "-fno-exceptions"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU",
        "printf=iprintf"
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections",
        "-mcpu=${BOARD_OPTIONS['build']['mcu']}",
        "-mthumb",
        "-Wl,--entry=Reset_Handler",
        "-Wl,--start-group"
    ],

    SIZEPRINTCMD='"$SIZETOOL" -B -d $SOURCES',

    UPLOADER=join("$PIOPACKAGES_DIR", "$PIOPACKAGE_UPLOADER", "bossac"),
    UPLOADERFLAGS=[
        "--info",
        "--debug",
        "--port", "$UPLOAD_PORT",
        "--erase",
        "--write",
        "--verify",
        "--boot"
    ],
    UPLOADBINCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
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
            suffix=".bin"
        )
    )
)

CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(CORELIBS + ["m", "gcc"])

#
# Target: Build the .bin file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_bin = join("$BUILD_DIR", "firmware.bin")
else:
    target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

upload = env.Alias(["upload", "uploadlazy"], target_bin, ("$UPLOADBINCMD"))
AlwaysBuild(upload)

#
# Check for $UPLOAD_PORT variable
#

is_uptarget = (set(["upload", "uploadlazy"]) & set(COMMAND_LINE_TARGETS))

if is_uptarget:
    # try autodetect upload port
    if "UPLOAD_PORT" not in env:
        for item in get_serialports():
            if "VID:PID" in item['hwid']:
                print "Auto-detected UPLOAD_PORT: %s" % item['port']
                env.Replace(UPLOAD_PORT=item['port'])
                break

    if "UPLOAD_PORT" not in env:
        print("WARNING!!! Please specify environment 'upload_port' or use "
              "global --upload-port option.\n")

#
# Setup default targets
#

Default([target_bin, target_size])

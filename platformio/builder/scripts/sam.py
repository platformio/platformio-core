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

    ARFLAGS=["rcs"],

    ASFLAGS=[
        "-c",
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "assembler-with-cpp",
        "-mmcu=$BOARD_MCU"
    ],

    CCFLAGS=[
        "-g",  # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        # "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-MMD",  # output dependency info
        "-mmcu=$BOARD_MCU"
    ],

    CXXFLAGS=[
        "-fno-exceptions",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU"
    ],

    LINKFLAGS=[
        "-Os",
        "-mmcu=$BOARD_MCU",
        "-Wl,--gc-sections",
        "-Wl,--start-group"
    ],

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-sam", "bossac"),
    UPLOADERFLAGS=[
        "-i",
        "-d",
        "--port", "$UPLOAD_PORT",
        "-U false",  # @TODO "Native USB"?
        "-e",
        "-w",
        "-v",
        "-b"
    ],
    UPLOADBINCMD='"$UPLOADER" $UPLOADERFLAGS -U flash:w:$SOURCES:i',
    UPLOADEEPCMD='"$UPLOADER" $UPLOADERFLAGS -U eeprom:w:$SOURCES:i'
)

env.Append(
    BUILDERS=dict(
        ElfToEep=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "-j",
                ".eeprom",
                '--set-section-flags=.eeprom="alloc,load"',
                "--no-change-warnings",
                "--change-section-lma",
                ".eeprom=0",
                "$SOURCES",
                "$TARGET"]),
            suffix=".eep"
        ),

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
)

CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(CORELIBS + ["m"])

#
# Target: Build the .bin file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_bin = join("$BUILD_DIR", "firmware.bin")
else:
    target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Extract EEPROM data (from EEMEM directive) to .eep file
#

target_eep = env.Alias("eep", env.ElfToEep(join("$BUILD_DIR", "firmware"),
                                           target_elf))

#
# Target: Upload by default .bin file
#

upload = env.Alias(["upload", "uploadlazy"], target_bin, ("$UPLOADBINCMD"))
AlwaysBuild(upload)

#
# Target: Upload .eep file
#

uploadeep = env.Alias(["uploadeep"], target_eep, ("$UPLOADEEPCMD"))
AlwaysBuild(uploadeep)


#
# Check for $UPLOAD_PORT variable
#

is_uptarget = (set(["upload", "uploadlazy", "uploadeep"]) &
               set(COMMAND_LINE_TARGETS))

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

Default(target_bin)

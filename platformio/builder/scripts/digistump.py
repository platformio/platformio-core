# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Digistump boards
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment)

env = DefaultEnvironment()

if env.get("BOARD_OPTIONS", {}).get("build", {}).get("mcu") != "cortex-m3":
    env.Replace(
        AR="avr-ar",
        AS="avr-gcc",
        CC="avr-gcc",
        CXX="avr-g++",
        OBJCOPY="avr-objcopy",
        RANLIB="avr-ranlib",
        SIZETOOL="avr-size",

        ARFLAGS=["rcs"],

        CPPFLAGS=[
            "-mmcu=$BOARD_MCU"
        ],

        LINKFLAGS=[
            "-mmcu=$BOARD_MCU"
        ],

        SIZEPRINTCMD='"$SIZETOOL" --mcu=$BOARD_MCU -C -d $SOURCES'
    )

else:
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
            "-mcpu=${BOARD_OPTIONS['build']['mcu']}",
            "-mthumb"
            # "-nostdlib"
        ],

        CXXFLAGS=[
            "-fno-rtti",
        ],

        CPPFLAGS=[
            "-mcpu=${BOARD_OPTIONS['build']['mcu']}",
            "-mthumb",
            "-ffunction-sections",  # place each function in its own section
            "-fdata-sections"
            # "-nostdlib"
        ],

        CPPDEFINES=[
            "printf=iprintf"
        ],

        LINKFLAGS=[
            "-mcpu=cortex-m3",
            "-mthumb",
            "-Wl,--gc-sections",
            "-Wl,--entry=Reset_Handler"
            # "-nostartfiles",
            # "-nostdlib",
        ],

        SIZEPRINTCMD='"$SIZETOOL" -B -d $SOURCES'
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
    ),

    ASFLAGS=[
        "-c",
        "-g",  # include debugging info (so errors include line numbers)
        "-x", "assembler-with-cpp",
        "-Wall"
    ],

    CPPFLAGS=[
        "-g",   # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-fdata-sections",
        "-ffunction-sections",  # place each function in its own section
        "-Wall",
        "-MMD"  # output dependancy info
    ],

    CPPDEFINES=[
        "F_CPU=$BOARD_F_CPU"
    ],

    CXXFLAGS=[
        "-felide-constructors",
        "-fno-exceptions"
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--start-group"

    ]
)

if env.get("BOARD_OPTIONS", {}).get("build", {}).get("mcu") == "cortex-m3":
    env.Append(
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
        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
    )
else:
    env.Append(
        UPLOADER=join("$PIOPACKAGES_DIR", "tool-avrdude", "avrdude"),
        UPLOADERFLAGS=[
            "-q",  # suppress progress output
            "-D",  # disable auto erase for flash memory
            "-p", "$BOARD_MCU",
            "-C", '"%s"' % join("$PIOPACKAGES_DIR",
                                "tool-avrdude", "avrdude.conf"),
            "-c", "$UPLOAD_PROTOCOL",
            "-b", "$UPLOAD_SPEED",
            "-P", "$UPLOAD_PORT"
        ],
        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS -U flash:w:$SOURCES:i'
    )

CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(CORELIBS + ["m"])

#
# Target: Build the .hex file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_hex = join("$BUILD_DIR", "firmware.hex")
else:
    target_hex = env.ElfToHex(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .hex file
#

upload = env.Alias(["upload", "uploadlazy"], target_hex, ("$UPLOADCMD"))
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_hex, target_size])

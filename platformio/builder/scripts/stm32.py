# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for STMicroelectronics
    STM32 Series ARM microcontrollers.
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

env.Replace(
    UPLOADER=join("$PIOPACKAGES_DIR", "tool-stlink", "st-flash"),
    UPLOADERFLAGS=[
        "write",        # write in flash
        "$SOURCES",     # firmware path to flash
        "0x08000000"    # flash start adress
    ],

    UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
)


env.Append(
    CPPDEFINES=[
        "${BOARD_OPTIONS['build']['variant'].upper()}"
    ],

    LINKFLAGS=[
        "-nostartfiles",
        "-nostdlib"
    ]
)

CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(["c", "gcc", "m", "nosys"] + CORELIBS)

#
# Target: Build the .bin file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.bin")
else:
    target_firm = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

upload = env.Alias(["upload", "uploadlazy"], target_firm, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])

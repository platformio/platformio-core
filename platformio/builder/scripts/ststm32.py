# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for ST STM32 Series ARM microcontrollers.
"""

import platform
from os.path import isfile, join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, Exit, SConscript)

env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

if env.subst("$UPLOAD_PROTOCOL") == "gdb":
    if not isfile(join(env.subst("$PROJECT_DIR"), "upload.gdb")):
        Exit(
            "You are using GDB as firmware uploader. "
            "Please specify upload commands in upload.gdb "
            "file in project directory!"
        )
    env.Replace(
        UPLOADER=join(
            "$PIOPACKAGES_DIR", "toolchain-gccarmnoneeabi",
            "bin", "arm-none-eabi-gdb"
        ),
        UPLOADERFLAGS=[
            join("$BUILD_DIR", "firmware.elf"),
            "-batch",
            "-x", join("$PROJECT_DIR", "upload.gdb")
        ],

        UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
    )
else:
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
        env.get("BOARD_OPTIONS", {}).get(
            "build", {}).get("variant", "").upper()
    ],

    LIBS=["stdc++", "nosys"],

    LINKFLAGS=[
        "-nostartfiles",
        "-nostdlib"
    ]
)

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

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

disable_msd = (
    (platform.system() == "Darwin" and platform.release().startswith("14.")) or
    env.subst("$UPLOAD_PROTOCOL"))
if "mbed" in env.subst("$FRAMEWORK") and not disable_msd:
    upload = env.Alias(["upload", "uploadlazy"],
                       target_firm, env.UploadToDisk)
else:
    upload = env.Alias(["upload", "uploadlazy"], target_firm, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])

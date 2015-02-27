# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel SAM series of microcontrollers
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()


env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

env.Replace(
    UPLOADER=join("$PIOPACKAGES_DIR", "$PIOPACKAGE_UPLOADER", "bossac"),
    UPLOADERFLAGS=[
        "--info",
        "--debug",
        "--port", "$UPLOAD_PORT",
        "--erase",
        "--write",
        "--verify",
        "--boot",
        "--reset"
    ],
    UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
)

env.Append(
    CPPDEFINES=[
        "printf=iprintf"
    ],

    LINKFLAGS=[
        "-Wl,--entry=Reset_Handler",
        "-Wl,--start-group"
    ]
)

CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(["m", "gcc"] + CORELIBS)

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

upload = env.Alias(["upload", "uploadlazy"], target_firm,
                   [BeforeUpload, "$UPLOADCMD"])
AlwaysBuild(upload)

#
# Setup default targets
#

Default([target_firm, target_size])

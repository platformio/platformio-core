# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Texas Instruments
    Tiva C Series ARM Cortex-M4 microcontrollers.
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

env = DefaultEnvironment()
env = SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")),
                 exports="env")

env.Replace(
    UPLOADER=join("$PIOPACKAGES_DIR", "tool-lm4flash", "lm4flash"),
    UPLOADCMD="$UPLOADER $SOURCES"
)

env.Append(
    LINKFLAGS=[
        "-nostartfiles",
        "-nostdlib"
    ]
)

CORELIBS = env.ProcessGeneral()

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildFirmware(["c", "gcc", "m"] + CORELIBS)

#
# Target: Build the .bin file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_file = join("$BUILD_DIR", "firmware.bin")
else:
    target_file = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload firmware
#

upload = env.Alias(["upload", "uploadlazy"], target_file, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_file, target_size])

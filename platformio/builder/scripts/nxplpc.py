# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for NXP LPC series ARM microcontrollers.
"""

from os.path import join
from shutil import copyfile

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)


def UploadToDisk(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()
    copyfile(join(env.subst("$BUILD_DIR"), "firmware.bin"),
             join(env.subst("$UPLOAD_PORT"), "firmware.bin"))
    print ("Firmware has been successfully uploaded.\n"
           "Please restart your board.")

env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

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

upload = env.Alias(["upload", "uploadlazy"], target_firm, UploadToDisk)
AlwaysBuild(upload)

#
# Target: Define targets
#

Default([target_firm, target_size])

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel SAM series of microcontrollers
"""

from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

from platformio.util import get_serialports

env = DefaultEnvironment()
env = SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")),
                 exports="env")

env.Replace(
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
    target_firmware = join("$BUILD_DIR", "firmware.bin")
else:
    target_firmware = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

upload = env.Alias(
    ["upload", "uploadlazy"], target_firmware, ("$UPLOADBINCMD"))
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

Default([target_firmware, target_size])

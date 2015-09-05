# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Atmel SAM series of microcontrollers
"""

from os.path import basename, join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

from platformio.util import get_serialports


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()

    board_type = env.subst("$BOARD")
    env.Append(
        UPLOADERFLAGS=[
            "-U",
            "true" if ("usb" in board_type.lower(
            ) or board_type == "digix") else "false"
        ])

    upload_options = env.get("BOARD_OPTIONS", {}).get("upload", {})

    if not upload_options.get("disable_flushing", False):
        env.FlushSerialBuffer("$UPLOAD_PORT")

    before_ports = [i['port'] for i in get_serialports()]

    if upload_options.get("use_1200bps_touch", False):
        env.TouchSerialPort("$UPLOAD_PORT", 1200)

    if upload_options.get("wait_for_upload_port", False):
        env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))

    # use only port name for BOSSA
    if "/" in env.subst("$UPLOAD_PORT"):
        env.Replace(UPLOAD_PORT=basename(env.subst("$UPLOAD_PORT")))


env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

env.Replace(
    UPLOADER=join("$PIOPACKAGES_DIR", "$PIOPACKAGE_UPLOADER", "bossac"),
    UPLOADERFLAGS=[
        "--info",
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
        "printf=iprintf",
        "USBCON",
        'USB_MANUFACTURER="PlatformIO"'
    ],

    LINKFLAGS=[
        "-Wl,--entry=Reset_Handler",
        "-Wl,--start-group"
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

upload = env.Alias(["upload", "uploadlazy"], target_firm,
                   [BeforeUpload, "$UPLOADCMD"])
AlwaysBuild(upload)

#
# Setup default targets
#

Default([target_firm, target_size])

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for Android Framework (based on Wiring).
"""

from os.path import join

from SCons.Script import Import, Return

env = None
Import("env")

BOARD_OPTIONS = env.ParseBoardOptions(
    join("$PLATFORMFW_DIR", "boards.txt"),
    "${BOARD}"
)
ARDUINO_VERSION = int(
    open(join(env.subst("$PLATFORMFW_DIR"),
              "version.txt")).read().replace(".", "").strip())
ARDUINO_FLAGS = [
    "-DARDUINO=%d" % ARDUINO_VERSION,
    "-DARDUINO_%s" % BOARD_OPTIONS['build.board']
]
# usb flags
if "build.usb_product" in BOARD_OPTIONS:
    ARDUINO_FLAGS += [
        "-DUSB_VID=%s" % BOARD_OPTIONS['build.vid'],
        "-DUSB_PID=%s" % BOARD_OPTIONS['build.pid'],
        "-DUSB_PRODUCT=%s" % BOARD_OPTIONS['build.usb_product'].replace(
            '"', "")
    ]

env.Append(
    ASFLAGS=ARDUINO_FLAGS,
    CCFLAGS=ARDUINO_FLAGS,
    CPPPATH=[
        join("$BUILD_DIR", "core"),
        join("$PLATFORMFW_DIR", "variants", BOARD_OPTIONS['build.variant'])
    ]
)

if "BOARD_MCU" not in env:
    env.Replace(BOARD_MCU=BOARD_OPTIONS['build.mcu'])
if "BOARD_F_CPU" not in env:
    env.Replace(BOARD_F_CPU=BOARD_OPTIONS['build.f_cpu'])
if "UPLOAD_PROTOCOL" not in env:
    env.Replace(UPLOAD_PROTOCOL=BOARD_OPTIONS['upload.protocol'])
if "UPLOAD_SPEED" not in env:
    env.Replace(UPLOAD_SPEED=BOARD_OPTIONS['upload.speed'])


libs = []

#
# Target: Build Core Library
#

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "core"),
    join("$PLATFORMFW_DIR", "cores", BOARD_OPTIONS['build.core'])
))

Return("libs")

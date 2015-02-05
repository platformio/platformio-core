# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for Android Framework (based on Wiring).
"""

from os.path import join

from SCons.Script import Import, Return

env = None
Import("env")

ARDUINO_VERSION = int(
    open(join(env.subst("$PLATFORMFW_DIR"),
              "version.txt")).read().replace(".", "").strip())

# usb flags
ARDUINO_USBDEFINES = []
if "usb_product" in env.subst("${BOARD_OPTIONS['build']}"):
    ARDUINO_USBDEFINES = [
        "USB_VID=${BOARD_OPTIONS['build']['vid']}",
        "USB_PID=${BOARD_OPTIONS['build']['pid']}",
        'USB_PRODUCT=\\"%s\\"' % (env.subst(
            "${BOARD_OPTIONS['build']['usb_product']}").replace('"', ""))
    ]

env.Append(
    CPPDEFINES=[
        "ARDUINO=%d" % ARDUINO_VERSION
    ] + ARDUINO_USBDEFINES,

    CPPPATH=[
        join("$BUILD_DIR", "FrameworkArduino")
    ]
)

# include board variant
if "variant" in env.get("BOARD_OPTIONS", {}).get("build", {}):
    env.VariantDir(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join("$PLATFORMFW_DIR", "variants",
             "${BOARD_OPTIONS['build']['variant']}")
    )
    env.Append(
        CPPPATH=[
            join("$BUILD_DIR", "FrameworkArduinoVariant")
        ]
    )

#
# Target: Build Core Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join("$PLATFORMFW_DIR", "cores", "${BOARD_OPTIONS['build']['core']}")
))

Return("env libs")

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for Android Framework (based on Wiring).
"""

from os import listdir
from os.path import isfile, join

from SCons.Script import Import, Return

env = None
Import("env")
BOARD_BUILDOPTS = env.get("BOARD_OPTIONS", {}).get("build", {})

ARDUINO_VERSION = int(
    open(join(env.subst("$PLATFORMFW_DIR"),
              "version.txt")).read().replace(".", "").strip())

# usb flags
ARDUINO_USBDEFINES = []
if "usb_product" in BOARD_BUILDOPTS:
    ARDUINO_USBDEFINES = [
        "USB_VID=${BOARD_OPTIONS['build']['vid']}",
        "USB_PID=${BOARD_OPTIONS['build']['pid']}",
        'USB_PRODUCT=\\"%s\\"' % (env.subst(
            "${BOARD_OPTIONS['build']['usb_product']}").replace('"', ""))
    ]

if env.get("BOARD_OPTIONS", {}).get("platform", None) == "teensy":
    ARDUINO_USBDEFINES += [
        "ARDUINO=106",
        "TEENSYDUINO=%d" % ARDUINO_VERSION
    ]
else:
    ARDUINO_USBDEFINES += ["ARDUINO=%d" % ARDUINO_VERSION]

env.Append(
    CPPDEFINES=ARDUINO_USBDEFINES,

    CPPPATH=[
        join("$BUILD_DIR", "FrameworkArduino")
    ]
)

if "variant" in BOARD_BUILDOPTS:
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

if BOARD_BUILDOPTS.get("core", None) == "teensy":
    # search relative includes in teensy directories
    core_dir = join(env.get("PIOHOME_DIR"), "packages",
                    "framework-arduinoteensy", "cores", "teensy")
    for item in listdir(core_dir):
        file_path = join(core_dir, item)
        if not isfile(file_path):
            continue
        content = None
        content_changed = False
        with open(file_path) as fp:
            content = fp.read()
            if '#include "../' in content:
                content_changed = True
                content = content.replace('#include "../', '#include "')
        if not content_changed:
            continue
        with open(file_path, "w") as fp:
            fp.write(content)

#
# Target: Build Core Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join("$PLATFORMFW_DIR", "cores", "${BOARD_OPTIONS['build']['core']}")
))

Return("env libs")

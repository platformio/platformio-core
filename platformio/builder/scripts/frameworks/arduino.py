# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for Arduino Framework (based on Wiring).
"""

from os import listdir, walk
from os.path import isfile, join

from SCons.Script import DefaultEnvironment, Return

env = DefaultEnvironment()

BOARD_OPTS = env.get("BOARD_OPTIONS", {})
BOARD_BUILDOPTS = BOARD_OPTS.get("build", {})

#
# Determine framework directory
# based on development platform
#

PLATFORMFW_DIR = join("$PIOPACKAGES_DIR",
                      "framework-arduino${PLATFORM.replace('atmel', '')}")

if env.get("PLATFORM") == "digistump":
    PLATFORMFW_DIR = join(
        "$PIOPACKAGES_DIR",
        "framework-arduino%s" % (
            "sam" if BOARD_BUILDOPTS.get("cpu") == "cortex-m3" else "avr")
    )

env.Replace(PLATFORMFW_DIR=PLATFORMFW_DIR)

#
# Base
#

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

if env.get("PLATFORM") == "teensy":
    ARDUINO_USBDEFINES += [
        "ARDUINO=10600",
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

#
# Atmel SAM platform
#

if env.subst("${PLATFORMFW_DIR}")[-3:] == "sam":
    env.VariantDir(
        join("$BUILD_DIR", "FrameworkCMSISInc"),
        join("$PLATFORMFW_DIR", "system", "CMSIS", "CMSIS", "Include")
    )
    env.VariantDir(
        join("$BUILD_DIR", "FrameworkDeviceInc"),
        join("$PLATFORMFW_DIR", "system", "CMSIS", "Device", "ATMEL")
    )
    env.VariantDir(
        join("$BUILD_DIR", "FrameworkLibSam"),
        join("$PLATFORMFW_DIR", "system", "libsam")
    )

    env.VariantDir(
        join("$BUILD_DIR", "FrameworkArduinoInc"),
        join("$PLATFORMFW_DIR", "cores", "digix")
    )
    env.Append(
        CPPPATH=[
            join("$BUILD_DIR", "FrameworkCMSISInc"),
            join("$BUILD_DIR", "FrameworkLibSam"),
            join("$BUILD_DIR", "FrameworkLibSam", "include"),
            join("$BUILD_DIR", "FrameworkDeviceInc"),
            join("$BUILD_DIR", "FrameworkDeviceInc", "sam3xa", "include")
        ]
    )

    # search relative includes in lib SAM directories
    core_dir = join(env.subst("$PLATFORMFW_DIR"), "system", "libsam")
    for root, _, files in walk(core_dir):
        for lib_file in files:
            file_path = join(root, lib_file)
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
# Teensy platform
#

# Teensy 2.x Core
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

if "variant" in BOARD_BUILDOPTS:
    env.Append(
        CPPPATH=[
            join("$BUILD_DIR", "FrameworkArduinoVariant")
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join("$PLATFORMFW_DIR", "variants",
             "${BOARD_OPTIONS['build']['variant']}")
    ))

envsafe = env.Clone()
libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join("$PLATFORMFW_DIR", "cores", "${BOARD_OPTIONS['build']['core']}")
))

if env.subst("${PLATFORMFW_DIR}")[-3:] == "sam":
    envsafe.Append(
        CFLAGS=[
            "-std=gnu99"
        ]
    )
    libs.append(envsafe.BuildLibrary(
        join("$BUILD_DIR", "SamLib"),
        join("$PLATFORMFW_DIR", "system", "libsam", "source")
    ))

Return("libs")

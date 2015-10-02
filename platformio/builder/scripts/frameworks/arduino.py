# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
Arduino

Arduino Framework allows writing cross-platform software to control
devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://arduino.cc/en/Reference/HomePage
"""

from os import listdir, walk
from os.path import isdir, isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

BOARD_OPTS = env.get("BOARD_OPTIONS", {})
BOARD_BUILDOPTS = BOARD_OPTS.get("build", {})
BOARD_CORELIBDIRNAME = BOARD_BUILDOPTS.get("core")

#
# Determine framework directory
# based on development platform
#

PLATFORMFW_DIR = join("$PIOPACKAGES_DIR",
                      "framework-arduino${PLATFORM.replace('atmel', '')}")

if "digispark" in BOARD_BUILDOPTS.get("core"):
    BOARD_CORELIBDIRNAME = "digispark"
    PLATFORMFW_DIR = join(
        "$PIOPACKAGES_DIR",
        "framework-arduino%s" % (
            "sam" if BOARD_BUILDOPTS.get("cpu") == "cortex-m3" else "avr")
    )
elif env.get("PLATFORM") == "timsp430":
    PLATFORMFW_DIR = join(
        "$PIOPACKAGES_DIR",
        "framework-arduinomsp430"
    )
elif env.get("PLATFORM") == "espressif":
    env.Prepend(
        CPPPATH=[join("$PLATFORMFW_DIR", "sdk", "include")],
        LIBPATH=[join("$PLATFORMFW_DIR", "sdk", "lib")],
        LIBS=["smartconfig", "pp", "main", "wpa", "lwip",
              "net80211", "wps", "crypto", "phy", "hal", "gcc", "m"]
    )

env.Replace(PLATFORMFW_DIR=PLATFORMFW_DIR)

#
# Lookup for specific core's libraries
#

if isdir(join(env.subst("$PLATFORMFW_DIR"), "libraries", "__cores__",
              BOARD_CORELIBDIRNAME)):
    lib_dirs = env.get("LIBSOURCE_DIRS")
    lib_dirs.insert(
        lib_dirs.index(join("$PLATFORMFW_DIR", "libraries")),
        join(PLATFORMFW_DIR, "libraries", "__cores__", BOARD_CORELIBDIRNAME)
    )
    env.Replace(
        LIBSOURCE_DIRS=lib_dirs
    )

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
    env.VariantDirWrap(
        join("$BUILD_DIR", "FrameworkCMSISInc"),
        join("$PLATFORMFW_DIR", "system", "CMSIS", "CMSIS", "Include")
    )
    env.VariantDirWrap(
        join("$BUILD_DIR", "FrameworkDeviceInc"),
        join("$PLATFORMFW_DIR", "system", "CMSIS", "Device", "ATMEL")
    )
    env.VariantDirWrap(
        join("$BUILD_DIR", "FrameworkLibSam"),
        join("$PLATFORMFW_DIR", "system", "libsam")
    )

    env.VariantDirWrap(
        join("$BUILD_DIR", "FrameworkArduinoInc"),
        join("$PLATFORMFW_DIR", "cores", "${BOARD_OPTIONS['build']['core']}")
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
    for item in sorted(listdir(core_dir)):
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
    env.Append(
        LIBPATH=[
            join("$PLATFORMFW_DIR", "variants",
                 "${BOARD_OPTIONS['build']['variant']}")
        ]
    )
    envsafe.Append(
        CFLAGS=[
            "-std=gnu99"
        ]
    )
    libs.append("sam_sam3x8e_gcc_rel")

env.Append(LIBS=libs)

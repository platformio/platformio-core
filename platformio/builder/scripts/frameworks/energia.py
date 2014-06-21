# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for Energia Framework (based on Wiring).
"""

from os.path import join

from SCons.Script import Import, Return

env = None
Import("env")

BOARD_OPTIONS = env.ParseBoardOptions(
    join("$PLATFORMFW_DIR", "boards.txt"),
    "${BOARD}"
)
ENERGIA_VERSION = int(
    open(join(env.subst("$PLATFORMFW_DIR"),
              "version.txt")).read().replace(".", "").strip())

# include board variant
env.VariantDir(
    join("$BUILD_DIR", "variant"),
    join("$PLATFORMFW_DIR", "variants", BOARD_OPTIONS['build.variant'])
)

env.Append(
    CPPDEFINES=[
        "ARDUINO=101",
        "ENERGIA=%d" % ENERGIA_VERSION
    ],
    CPPPATH=[
        join("$BUILD_DIR", "core"),
        join("$BUILD_DIR", "variant")
    ]
)

if "BOARD_MCU" not in env:
    env.Replace(BOARD_MCU=BOARD_OPTIONS['build.mcu'])
if "BOARD_F_CPU" not in env:
    env.Replace(BOARD_F_CPU=BOARD_OPTIONS['build.f_cpu'])
if "UPLOAD_PROTOCOL" not in env and "upload.protocol" in BOARD_OPTIONS:
    env.Replace(UPLOAD_PROTOCOL=BOARD_OPTIONS['upload.protocol'])

# specific linker script for TIVA devices
if "ldscript" in BOARD_OPTIONS:
    env.Append(
        LINKFLAGS=["-T", join("$PLATFORMFW_DIR", "cores",
                              BOARD_OPTIONS['build.core'],
                              BOARD_OPTIONS['ldscript'])]
    )


libs = []

#
# Target: Build Core Library
#

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "core"),
    join("$PLATFORMFW_DIR", "cores", BOARD_OPTIONS['build.core'])
))

Return("libs")

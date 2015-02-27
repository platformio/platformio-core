# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for Energia Framework (based on Wiring).
"""

from os.path import join

from SCons.Script import DefaultEnvironment, Return

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-energia${PLATFORM[2:]}")
)

ENERGIA_VERSION = int(
    open(join(env.subst("$PLATFORMFW_DIR"),
              "version.txt")).read().replace(".", "").strip())

# include board variant
env.VariantDir(
    join("$BUILD_DIR", "FrameworkEnergiaVariant"),
    join("$PLATFORMFW_DIR", "variants", "${BOARD_OPTIONS['build']['variant']}")
)

env.Append(
    CPPDEFINES=[
        "ARDUINO=101",
        "ENERGIA=%d" % ENERGIA_VERSION
    ],
    CPPPATH=[
        join("$BUILD_DIR", "FrameworkEnergia"),
        join("$BUILD_DIR", "FrameworkEnergiaVariant")
    ]
)

if env.get("BOARD_OPTIONS", {}).get("build", {}).get("core") == "lm4f":
    env.Append(
        LINKFLAGS=["-Wl,--entry=ResetISR"]
    )

#
# Target: Build Core Library
#

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkEnergia"),
    join("$PLATFORMFW_DIR", "cores", "${BOARD_OPTIONS['build']['core']}")
))

Return("libs")

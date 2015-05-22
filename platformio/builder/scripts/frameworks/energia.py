# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
Energia

Energia framework enables pretty much anyone to start easily creating
microcontroller-based projects and applications. Its easy-to-use libraries
and functions provide developers of all experience levels to start
blinking LEDs, buzzing buzzers and sensing sensors more quickly than ever
before.

http://energia.nu/reference/
"""

from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-energia${PLATFORM[2:]}")
)

ENERGIA_VERSION = int(
    open(join(env.subst("$PLATFORMFW_DIR"),
              "version.txt")).read().replace(".", "").strip())

# include board variant
env.VariantDirWrap(
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

env.Append(LIBS=libs)

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for CMSIS Framework.
"""

from os.path import join

from SCons.Script import Import, Return


env = None
Import("env")

env.VariantDir(
    join("$BUILD_DIR", "FrameworkCMSIS"),
    join("$PIOPACKAGES_DIR", "framework-cmsis",
         "cores", "${BOARD_OPTIONS['build']['core']}")
)

env.Append(
    CPPPATH=[
        join("$BUILD_DIR", "FrameworkCMSIS"),
        join("$BUILD_DIR", "FrameworkCMSISVariant")
    ]
)

envsafe = env.Clone()

#
# Target: Build Core Library
#

libs = []
libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join("$PIOPACKAGES_DIR", "framework-cmsis", "variants",
         "${BOARD_OPTIONS['build']['variant']}")
))

Return("env libs")

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Build script for SPL Framework
"""

from os.path import join

from SCons.Script import DefaultEnvironment, Return

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-spl")
)

env.VariantDir(
    join("$BUILD_DIR", "FrameworkSPLInc"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}",
         "variants", "${BOARD_OPTIONS['build']['variant']}", "inc")
)

env.Append(
    CPPPATH=[
        join("$BUILD_DIR", "FrameworkSPLInc"),
        join("$BUILD_DIR", "FrameworkSPL")
    ]
)

envsafe = env.Clone()

envsafe.Append(
    CPPPATH=[
        join("$BUILD_DIR", "src")
    ],

    CPPDEFINES=[
        "USE_STDPERIPH_DRIVER"
    ]
)

#
# Target: Build SPL Library
#

extra_flags = env.get("BOARD_OPTIONS", {}).get("build", {}).get("extra_flags")
ignore_files = []
if "STM32F40_41xxx" in extra_flags:
    ignore_files += ["stm32f4xx_fmc.c"]
elif "STM32F303xC" in extra_flags:
    ignore_files += ["stm32f30x_hrtim.c"]
elif "STM32L1XX_MD" in extra_flags:
    ignore_files += ["stm32l1xx_flash_ramfunc.c"]

libs = []
libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}", "variants",
         "${BOARD_OPTIONS['build']['variant']}", "src"),
    ignore_files
))

Return("libs")

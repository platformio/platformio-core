# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
SPL

The ST Standard Peripheral Library provides a set of functions for
handling the peripherals on the STM32 Cortex-M3 family.
The idea is to save the user (the new user, in particular) having to deal
directly with the registers.

http://www.st.com/web/en/catalog/tools/FM147/CL1794/SC961/SS1743?sc=stm32embeddedsoftware
"""

from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-spl")
)

env.VariantDirWrap(
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
    CPPPATH=["$BUILDSRC_DIR"],
    CPPDEFINES=[
        "USE_STDPERIPH_DRIVER"
    ]
)

#
# Target: Build SPL Library
#

extra_flags = env.get("BOARD_OPTIONS", {}).get("build", {}).get("extra_flags")
src_filter_patterns = ["+<*>"]
if "STM32F40_41xxx" in extra_flags:
    src_filter_patterns += ["-<stm32f4xx_fmc.c>"]
if "STM32F427_437xx" in extra_flags:
    src_filter_patterns += ["-<stm32f4xx_fsmc.c>"]
elif "STM32F303xC" in extra_flags:
    src_filter_patterns += ["-<stm32f30x_hrtim.c>"]
elif "STM32L1XX_MD" in extra_flags:
    src_filter_patterns += ["-<stm32l1xx_flash_ramfunc.c>"]

libs = []
libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}", "variants",
         "${BOARD_OPTIONS['build']['variant']}", "src"),
    src_filter=" ".join(src_filter_patterns)
))

env.Append(LIBS=libs)

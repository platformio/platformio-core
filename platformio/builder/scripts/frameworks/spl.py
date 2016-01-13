# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
SPL

The ST Standard Peripheral Library provides a set of functions for
handling the peripherals on the STM32 Cortex-M3 family.
The idea is to save the user (the new user, in particular) having to deal
directly with the registers.

http://www.st.com/web/en/catalog/tools/FM147/CL1794/SC961/SS1743?sc=stm32embeddedsoftware
"""

from os.path import isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-spl")
)

env.VariantDirWrap(
    join("$BUILD_DIR", "FrameworkCMSIS"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}",
         "cmsis", "cores", "${BOARD_OPTIONS['build']['core']}")
)

env.VariantDirWrap(
    join("$BUILD_DIR", "FrameworkSPLInc"),
    join(
        "$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}", "spl",
        "variants", env.subst("${BOARD_OPTIONS['build']['variant']}")[0:7],
        "inc"
    )
)

env.Append(
    CPPPATH=[
        join("$BUILD_DIR", "FrameworkCMSIS"),
        join("$BUILD_DIR", "FrameworkCMSISVariant"),
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

# use mbed ldscript with bootloader section
ldscript = env.get("BOARD_OPTIONS", {}).get("build", {}).get("ldscript")
if not isfile(join(env.subst("$PIOPACKAGES_DIR"), "ldscripts", ldscript)):
    if "mbed" in env.get("BOARD_OPTIONS", {}).get("frameworks", {}):
        env.Append(
            LINKFLAGS=[
                '-Wl,-T"%s"' %
                join(
                    "$PIOPACKAGES_DIR", "framework-mbed", "variant",
                    env.subst("$BOARD").upper(), "mbed",
                    "TARGET_%s" % env.subst(
                        "$BOARD").upper(), "TOOLCHAIN_GCC_ARM",
                    "%s.ld" % ldscript.upper()[:-3]
                )
            ]
        )

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
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(
        "$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}", "cmsis",
        "variants", env.subst("${BOARD_OPTIONS['build']['variant']}")[0:7]
    )
))

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}",
         "spl", "variants",
         env.subst("${BOARD_OPTIONS['build']['variant']}")[0:7], "src"),
    src_filter=" ".join(src_filter_patterns)
))

env.Append(LIBS=libs)

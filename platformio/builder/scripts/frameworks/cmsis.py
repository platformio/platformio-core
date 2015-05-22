# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
CMSIS

The ARM Cortex Microcontroller Software Interface Standard (CMSIS) is a
vendor-independent hardware abstraction layer for the Cortex-M processor
series and specifies debugger interfaces. The CMSIS enables consistent and
simple software interfaces to the processor for interface peripherals,
real-time operating systems, and middleware. It simplifies software
re-use, reducing the learning curve for new microcontroller developers
and cutting the time-to-market for devices.

http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php
"""

from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-cmsis")
)

env.VariantDirWrap(
    join("$BUILD_DIR", "FrameworkCMSIS"),
    join("$PLATFORMFW_DIR", "cores", "${BOARD_OPTIONS['build']['core']}")
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
    join("$PLATFORMFW_DIR", "variants", "${BOARD_OPTIONS['build']['variant']}")
))

env.Append(LIBS=libs)

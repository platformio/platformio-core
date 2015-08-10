# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Linux ARM
"""

from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

from platformio.util import get_systype

env = DefaultEnvironment()

env.Replace(
    _BINPREFIX="",
    AR="${_BINPREFIX}ar",
    AS="${_BINPREFIX}as",
    CC="${_BINPREFIX}gcc",
    CXX="${_BINPREFIX}g++",
    OBJCOPY="${_BINPREFIX}objcopy",
    RANLIB="${_BINPREFIX}ranlib",
    SIZETOOL="${_BINPREFIX}size",

    SIZEPRINTCMD='"$SIZETOOL" $SOURCES'
)

if get_systype() == "darwin_x86_64":
    env.Replace(
        _BINPREFIX="arm-linux-gnueabihf-"
    )

#
# Target: Build executable program
#

target_bin = env.BuildProgram()

#
# Target: Print binary size
#

target_size = env.Alias("size", target_bin, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Define targets
#

Default([target_bin])

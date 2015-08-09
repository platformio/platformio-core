# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Windows x86
"""

from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

from platformio.util import get_systype


env = DefaultEnvironment()

env.Replace(
    SIZEPRINTCMD="size $SOURCES",
    PROGSUFFIX=".exe"
)

if get_systype() == "darwin_x86_64":
    env.Replace(
        AR="i586-mingw32-ar",
        AS="i586-mingw32-as",
        CC="i586-mingw32-gcc",
        CXX="i586-mingw32-g++",
        OBJCOPY="i586-mingw32-objcopy",
        RANLIB="i586-mingw32-ranlib",
        SIZETOOL="i586-mingw32-size",
        SIZEPRINTCMD='"$SIZETOOL" $SOURCES'
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

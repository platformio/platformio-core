# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for Windows x86
"""

from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

from platformio.util import get_systype


env = DefaultEnvironment()

env.Replace(
    AR="$_MINGWPREFIX-ar",
    AS="$_MINGWPREFIX-as",
    CC="$_MINGWPREFIX-gcc",
    CXX="$_MINGWPREFIX-g++",
    OBJCOPY="$_MINGWPREFIX-objcopy",
    RANLIB="$_MINGWPREFIX-ranlib",
    SIZETOOL="$_MINGWPREFIX-size",

    SIZEPRINTCMD='"$SIZETOOL" $SOURCES',
    PROGSUFFIX=".exe"
)

if get_systype() == "darwin_x86_64":
    env.Replace(
        _MINGWPREFIX="i586-mingw32"
    )
elif get_systype() in ("linux_x86_64", "linux_i686"):
    env.Replace(
        _MINGWPREFIX="i686-w64-mingw32"
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

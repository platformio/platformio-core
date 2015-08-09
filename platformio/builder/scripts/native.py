# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
    Builder for native platform
"""

from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    SIZEPRINTCMD="size $SOURCES"
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

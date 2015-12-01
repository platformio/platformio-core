# Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
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
PlatformIO

PlatformIO Framework is an open source light-weight framework with
high-level API for cross-platform embedded programming. It lies above popular
middleware (HAL, SDK) and leverages all its benefits. This approach allowed to
incorporate different development platforms ranging from 8-bits AVR to powerful
32-bit ARM into the one embedded ecosystem.

http://platformio.org
"""

from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-platformio")
)

env.VariantDirWrap(
    join("$BUILD_DIR", "FrameworkPlatformIO"),
    join("$PLATFORMFW_DIR", "src", "api")
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

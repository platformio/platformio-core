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

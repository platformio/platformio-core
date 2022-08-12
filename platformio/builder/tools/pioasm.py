# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

import SCons.Tool.asm  # pylint: disable=import-error

#
# Resolve https://github.com/platformio/platformio-core/issues/3917
# Avoid forcing .S to bare assembly on Windows OS
#

if ".S" in SCons.Tool.asm.ASSuffixes:
    SCons.Tool.asm.ASSuffixes.remove(".S")
if ".S" not in SCons.Tool.asm.ASPPSuffixes:
    SCons.Tool.asm.ASPPSuffixes.append(".S")


generate = SCons.Tool.asm.generate
exists = SCons.Tool.asm.exists

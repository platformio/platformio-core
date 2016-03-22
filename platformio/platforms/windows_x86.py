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

from platformio.platforms.base import BasePlatform


class Windows_x86Platform(BasePlatform):

    """
        Windows x86 (32-bit) is a metafamily of graphical operating systems
        developed and marketed by Microsoft.
        Using host OS (Windows, Linux 32/64 or Mac OS X) you can build native
        application for Windows x86 platform.

        http://platformio.org/platforms/windows_x86
    """

    PACKAGES = {

        "toolchain-gccmingw32": {
            "alias": "toolchain",
            "default": True
        }
    }

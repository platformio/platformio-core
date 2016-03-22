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
from platformio.util import get_systype


class Linux_x86_64Platform(BasePlatform):

    """
        Linux x86_64 (64-bit) is a Unix-like and mostly POSIX-compliant
        computer operating system (OS) assembled under the model of free and
        open-source software development and distribution.

        Using host OS (Mac OS X or Linux 64-bit) you can build native
        application for Linux x86_64 platform.

        http://platformio.org/platforms/linux_i686
    """

    PACKAGES = {

        "toolchain-gcclinux64": {
            "alias": "toolchain",
            "default": True
        }
    }

    def __init__(self):
        if get_systype() == "linux_x86_64":
            del self.PACKAGES['toolchain-gcclinux64']
        BasePlatform.__init__(self)

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

from platformio import exception, util
from platformio.platforms.base import BasePlatform


class Linux_armPlatform(BasePlatform):

    """
        Linux ARM is a Unix-like and mostly POSIX-compliant computer
        operating system (OS) assembled under the model of free and open-source
        software development and distribution.

        Using host OS (Mac OS X, Linux ARM) you can build native application
        for Linux ARM platform.

        http://platformio.org/platforms/linux_arm
    """

    PACKAGES = {

        "toolchain-gccarmlinuxgnueabi": {
            "alias": "toolchain",
            "default": True
        },

        "framework-wiringpi": {
            "alias": "framework"
        }
    }

    def __init__(self):
        if "linux_arm" in util.get_systype():
            del self.PACKAGES['toolchain-gccarmlinuxgnueabi']
        BasePlatform.__init__(self)

    def configure_default_packages(self, envoptions, targets):
        if (envoptions.get("framework") == "wiringpi" and
                "linux_arm" not in util.get_systype()):
            raise exception.PlatformioException(
                "PlatformIO does not support temporary cross-compilation "
                "for WiringPi framework. Please run PlatformIO directly on "
                "Raspberry Pi"
            )

        return BasePlatform.configure_default_packages(
            self, envoptions, targets)

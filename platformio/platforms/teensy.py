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
from platformio.util import get_boards


class TeensyPlatform(BasePlatform):

    """
    Teensy is a complete USB-based microcontroller development system, in
    a very small footprint, capable of implementing many types of projects.
    All programming is done via the USB port. No special programmer is
    needed, only a standard USB cable and a PC or Macintosh with a USB port.

    https://www.pjrc.com/teensy
    """

    PACKAGES = {

        "toolchain-atmelavr": {
        },

        "toolchain-gccarmnoneeabi": {
        },

        "ldscripts": {
            "default": True
        },

        "framework-arduinoteensy": {
            "alias": "framework"
        },

        "framework-mbed": {
            "alias": "framework"
        },

        "tool-teensy": {
            "alias": "uploader"
        }
    }

    def get_name(self):
        return "Teensy"

    def configure_default_packages(self, envoptions, targets):
        if envoptions.get("board"):
            board = get_boards(envoptions.get("board"))
            if board['build']['core'] == "teensy":
                name = "toolchain-atmelavr"
            else:
                name = "toolchain-gccarmnoneeabi"
            self.PACKAGES[name]['alias'] = "toolchain"
            self.PACKAGES[name]['default'] = True

        return BasePlatform.configure_default_packages(
            self, envoptions, targets)

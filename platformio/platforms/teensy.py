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

from platformio.platforms.base import BasePlatform
from platformio.util import get_boards


class TeensyPlatform(BasePlatform):

    """
    Teensy is a complete USB-based microcontroller development system, in
    a very small footprint, capable of implementing many types of projects.
    All programming is done via the USB port. No special programmer is
    needed, only a standard "Mini-B" USB cable and a PC or Macintosh with
    a USB port.

    https://www.pjrc.com/teensy
    """

    PACKAGES = {

        "toolchain-atmelavr": {
            "default": True
        },

        "toolchain-gccarmnoneeabi": {
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "framework-arduinoteensy": {
            "default": True
        },

        "framework-mbed": {
            "default": True
        },

        "tool-teensy": {
            "alias": "uploader",
            "default": True
        }
    }

    def get_name(self):
        return "Teensy"

    def run(self, variables, targets, verbose):
        for v in variables:
            if "BOARD=" not in v:
                continue
            _, board = v.split("=")
            bdata = get_boards(board)
            if bdata['build']['core'] == "teensy":
                tpackage = "toolchain-atmelavr"
            else:
                tpackage = "toolchain-gccarmnoneeabi"
            self.PACKAGES[tpackage]['alias'] = "toolchain"
            break
        return BasePlatform.run(self, variables, targets, verbose)

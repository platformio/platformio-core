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


class Microchippic32Platform(BasePlatform):

    """
    Microchip's 32-bit portfolio with the MIPS microAptiv or M4K core offer
    high performance microcontrollers, and all the tools needed to develop
    your embedded projects. PIC32 MCUs gives your application the processing
    power, memory and peripherals your design needs!

    http://www.microchip.com/design-centers/32-bit
    """

    PACKAGES = {

        "toolchain-microchippic32": {
            "alias": "toolchain",
            "default": True
        },

        "framework-arduinomicrochippic32": {
            "alias": "framework"
        },

        "tool-pic32prog": {
            "alias": "uploader"
        }
    }

    def get_name(self):
        return "Microchip PIC32"

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


class Timsp430Platform(BasePlatform):

    """
    MSP430 microcontrollers (MCUs) from Texas Instruments (TI)
    are 16-bit, RISC-based, mixed-signal processors designed for ultra-low
    power. These MCUs offer the lowest power consumption and the perfect
    mix of integrated peripherals for thousands of applications.

    http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/msp/overview.page
    """

    PACKAGES = {

        "toolchain-timsp430": {
            "alias": "toolchain",
            "default": True
        },

        "tool-mspdebug": {
            "alias": "uploader"
        },

        "framework-energiamsp430": {
            "alias": "framework"
        },

        "framework-arduinomsp430": {
            "alias": "framework"
        }
    }

    def get_name(self):
        return "TI MSP430"

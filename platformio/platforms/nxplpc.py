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


class NxplpcPlatform(BasePlatform):

    """
    The NXP LPC is a family of 32-bit microcontroller integrated circuits
    by NXP Semiconductors. The LPC chips are grouped into related series
    that are based around the same 32-bit ARM processor core, such as the
    Cortex-M4F, Cortex-M3, Cortex-M0+, or Cortex-M0. Internally, each
    microcontroller consists of the processor core, static RAM memory,
    flash memory, debugging interface, and various peripherals.

    http://www.nxp.com/products/microcontrollers/
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "framework-mbed": {
            "alias": "framework"
        }
    }

    def get_name(self):
        return "NXP LPC"

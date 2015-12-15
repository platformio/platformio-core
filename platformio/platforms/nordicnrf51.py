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


class Nordicnrf51Platform(BasePlatform):

    """
    The Nordic nRF51 Series is a family of highly flexible,
    multi-protocol, system-on-chip (SoC) devices for ultra-low power
    wireless applications. nRF51 Series devices support a range of
    protocol stacks including Bluetooth Smart (previously called
    Bluetooth low energy), ANT and proprietary 2.4GHz protocols such as
    Gazell.

    https://www.nordicsemi.com/eng/Products/nRF51-Series-SoC
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
        return "Nordic nRF51"

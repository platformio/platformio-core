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


class Siliconlabsefm32Platform(BasePlatform):

    """
    Silicon Labs EFM32 Gecko 32-bit microcontroller (MCU) family includes
    devices that offer flash memory configurations up to 256 kB, 32 kB of
    RAM and CPU speeds up to 48 MHz.

    Based on the powerful ARM Cortex-M core, the Gecko family features
    innovative low energy techniques, short wake-up time from energy saving
    modes and a wide selection of peripherals, making it ideal for battery
    operated applications and other systems requiring high performance and
    low-energy consumption.

    http://www.silabs.com/products/mcu/32-bit/efm32-gecko/Pages/efm32-gecko.aspx
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
        return "Silicon Labs EFM32"

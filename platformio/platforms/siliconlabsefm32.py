# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
            "default": True
        }
    }

    def get_name(self):
        return "Silicon Labs EFM32"

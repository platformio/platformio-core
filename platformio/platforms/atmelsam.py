# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class AtmelsamPlatform(BasePlatform):

    """
    Atmel | SMART offers Flash- based ARM products based on the ARM
    Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB
    to 2MB of Flash including a rich peripheral and feature mix.

    http://www.atmel.com/products/microcontrollers/arm/default.aspx
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "framework-arduinosam": {
            "default": True
        },

        "tool-bossac": {
            "alias": "uploader",
            "default": True
        }
    }

    def get_name(self):
        return "Atmel SAM"

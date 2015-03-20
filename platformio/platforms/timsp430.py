# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
            "alias": "uploader",
            "default": True
        },

        "framework-energiamsp430": {
            "default": True
        },

        "framework-arduinomsp430": {
            "default": True
        }
    }

    def get_name(self):
        return "TI MSP430"

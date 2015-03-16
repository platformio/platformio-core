# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
            "default": True
        }
    }

    def get_name(self):
        return "NXP LPC"

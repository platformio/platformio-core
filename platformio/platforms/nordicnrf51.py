# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
            "default": True
        }
    }

    def get_name(self):
        return "Nordic nRF51"

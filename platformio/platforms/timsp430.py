# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import join

from platformio.platforms._base import BasePlatform


class Timsp430Platform(BasePlatform):
    """
        An embedded platform for TI MSP430 microcontrollers
        (with Energia Framework)
    """

    PACKAGES = {

        "toolchain-timsp430": {
            "path": join("tools", "toolchain"),
            "default": True
        },

        "tool-mspdebug": {
            "path": join("tools", "mspdebug"),
            "default": True,
        },

        "framework-energiamsp430": {
            "path": join("frameworks", "energia"),
            "default": False
        }
    }

    def get_name(self):
        return "timsp430"

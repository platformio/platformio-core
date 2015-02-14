# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class Timsp430Platform(BasePlatform):
    """
        An embedded platform for TI MSP430 microcontrollers
        (with Energia Framework)
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
        }
    }

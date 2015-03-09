# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class NxplpcPlatform(BasePlatform):

    """
        An embedded platform for NXP LPC series ARM microcontrollers
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

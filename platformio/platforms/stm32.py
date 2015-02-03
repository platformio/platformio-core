# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class Stm32Platform(BasePlatform):

    """
        An embedded platform for STMicroelectronics ARM microcontrollers
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "tool-stlink": {
            "alias": "uploader",
            "default": True
        },

        "framework-cmsis": {
            "default": True
        },

        "framework-spl": {
            "default": True
        },

        "framework-opencm3": {
            "default": True
        }
    }

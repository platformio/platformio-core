# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class AtmelsamPlatform(BasePlatform):

    """
        An embedded platform for Atmel SAM microcontrollers
        (with Arduino Framework)
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

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class SamPlatform(BasePlatform):

    """
        An embedded platform for Atmel SAM microcontrollers
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
            "alias": "framework",
            "default": True
        },

        "tool-sam": {
            "alias": "uploader",
            "default": True
        }
    }

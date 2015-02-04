# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class TeensyPlatform(BasePlatform):

    """
        An embedded platform for Teensy boards
        (with Arduino Framework)
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "framework-arduinoteensy": {
            "alias": "framework",
            "default": True
        }
    }

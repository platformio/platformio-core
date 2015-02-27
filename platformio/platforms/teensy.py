# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_boards


class TeensyPlatform(BasePlatform):

    """
        An embedded platform for Teensy boards
        (with Arduino Framework)
    """

    PACKAGES = {

        "toolchain-atmelavr": {
            "default": True
        },

        "toolchain-gccarmnoneeabi": {
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "framework-arduinoteensy": {
            "default": True
        },

        "tool-teensy": {
            "alias": "uploader",
            "default": True
        }
    }

    def run(self, variables, targets):
        for v in variables:
            if "BOARD=" not in v:
                continue
            _, board = v.split("=")
            bdata = get_boards(board)
            if bdata['build']['core'] == "teensy":
                tpackage = "toolchain-atmelavr"
            else:
                tpackage = "toolchain-gccarmnoneeabi"
            self.PACKAGES[tpackage]['alias'] = "toolchain"
            break
        return BasePlatform.run(self, variables, targets)

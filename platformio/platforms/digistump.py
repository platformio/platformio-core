# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_boards


class DigistumpPlatform(BasePlatform):

    """
        An embedded platform for Digistump boards
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

        "tool-bossac": {
            "default": True
        },

        "tool-avrdude": {
            "default": True
        },

        "framework-arduinoavr": {
            "default": True
        },

        "framework-arduinosam": {
            "default": True
        }
    }

    def run(self, variables, targets):
        for v in variables:
            if "BOARD=" not in v:
                continue
            _, board = v.split("=")
            bdata = get_boards(board)
            if "cpu" in bdata['build']:
                tpackage = "toolchain-gccarmnoneeabi"
                tuploader = "tool-bossac"
            else:
                tpackage = "toolchain-atmelavr"
                tuploader = "tool-avrdude"
            self.PACKAGES[tpackage]['alias'] = "toolchain"
            self.PACKAGES[tuploader]['alias'] = "uploader"
            break
        return BasePlatform.run(self, variables, targets)

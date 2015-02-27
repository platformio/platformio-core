# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_boards


class AtmelavrPlatform(BasePlatform):

    """
        An embedded platform for Atmel AVR microcontrollers
        (with Arduino Framework)
    """

    PACKAGES = {

        "toolchain-atmelavr": {
            "alias": "toolchain",
            "default": True
        },

        "tool-avrdude": {
            "default": True
        },

        "tool-micronucleus": {
            "default": True
        },

        "framework-arduinoavr": {
            "default": True
        }
    }

    def on_run_err(self, line):  # pylint: disable=R0201
        # fix STDERR "flash written" for avrdude
        if "avrdude" in line:
            self.on_run_out(line)
        else:
            BasePlatform.on_run_err(self, line)

    def run(self, variables, targets):
        for v in variables:
            if "BOARD=" not in v:
                continue
            tuploader = "tool-avrdude"
            _, board = v.split("=")
            bdata = get_boards(board)
            if "digispark" in bdata['build']['core']:
                tuploader = "tool-micronucleus"
            self.PACKAGES[tuploader]['alias'] = "uploader"
            break
        return BasePlatform.run(self, variables, targets)

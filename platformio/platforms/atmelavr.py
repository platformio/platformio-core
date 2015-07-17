# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_boards


class AtmelavrPlatform(BasePlatform):

    """
    Atmel AVR 8- and 32-bit MCUs deliver a unique combination of
    performance, power efficiency and design flexibility. Optimized to
    speed time to market-and easily adapt to new ones-they are based on
    the industrys most code-efficient architecture for C and assembly
    programming.

    http://www.atmel.com/products/microcontrollers/avr/default.aspx
    """

    PACKAGES = {

        "toolchain-atmelavr": {
            "alias": "toolchain",
            "default": True
        },

        "tool-avrdude": {
            "alias": "uploader",
            "default": True
        },

        "tool-micronucleus": {
            "alias": "uploader",
            "default": True
        },

        "framework-arduinoavr": {
            "default": True
        }
    }

    def get_name(self):
        return "Atmel AVR"

    def on_run_err(self, line):  # pylint: disable=R0201
        # fix STDERR "flash written" for avrdude
        if "avrdude" in line:
            self.on_run_out(line)
        else:
            BasePlatform.on_run_err(self, line)

    def run(self, variables, targets, verbose):
        for v in variables:
            if "BOARD=" not in v:
                continue
            disable_tool = "tool-micronucleus"
            _, board = v.split("=")
            bdata = get_boards(board)
            if "digispark" in bdata['build']['core']:
                disable_tool = "tool-avrdude"
            del self.PACKAGES[disable_tool]['alias']
            break
        return BasePlatform.run(self, variables, targets, verbose)

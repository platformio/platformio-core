# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_boards


class TeensyPlatform(BasePlatform):

    """
    Teensy is a complete USB-based microcontroller development system, in
    a very small footprint, capable of implementing many types of projects.
    All programming is done via the USB port. No special programmer is
    needed, only a standard "Mini-B" USB cable and a PC or Macintosh with
    a USB port.

    https://www.pjrc.com/teensy
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

    def get_name(self):
        return "Teensy"

    def run(self, variables, targets, verbose):
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
        return BasePlatform.run(self, variables, targets, verbose)

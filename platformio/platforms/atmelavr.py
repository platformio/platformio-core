# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


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
            "alias": "uploader",
            "default": True
        },

        "framework-arduinoavr": {
            "default": True
        }
    }

    def on_run_err(self, line):  # pylint: disable=R0201
        # fix STDERR "flash written" for avrdude
        if "flash written" in line:
            self.on_run_out(line)
        else:
            BasePlatform.on_run_err(self, line)

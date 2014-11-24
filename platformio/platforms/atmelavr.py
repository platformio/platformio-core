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
            "alias": "framework",
            "default": True
        }
    }

    def after_run(self, result):
        # fix STDERR "flash written" for avrdude
        if "flash written" in result['err']:
            result['out'] += "\n" + result['err']
            result['err'] = ""
        return result

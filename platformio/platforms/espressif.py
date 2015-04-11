# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class EspressifPlatform(BasePlatform):

    """
    Espressif Systems is a privately held fabless semiconductor company.
    They provide wireless communications and Wi-Fi chips which are widely
    used in mobile devices and the Internet of Things applications.

    https://espressif.com/
    """

    PACKAGES = {

        "toolchain-xtensa": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "tool-esptool": {
            "alias": "uploader",
            "default": True
        },

        "sdk-esp8266": {
            "default": True
        },

        "framework-arduinoespressif": {
            "default": True
        }
    }

    def get_name(self):
        return "Espressif"

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class TitivaPlatform(BasePlatform):
    """
        An embedded platform for TI TIVA C ARM microcontrollers
        (with Energia Framework)
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "tool-lm4flash": {
            "alias": "uploader",
            "default": True
        },

        "framework-energiativa": {
            "alias": "framework",
            "default": True
        }
    }

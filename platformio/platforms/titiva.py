# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import join

from platformio.platforms.base import BasePlatform


class TitivaPlatform(BasePlatform):

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "path": join("tools", "toolchain"),
            "default": True
        },

        "tool-lm4flash": {
            "path": join("tools", "lm4flash"),
            "default": True,
        },

        "framework-energiativa": {
            "path": join("frameworks", "energia"),
            "default": True
        }
    }

    def get_name(self):
        return "titiva"

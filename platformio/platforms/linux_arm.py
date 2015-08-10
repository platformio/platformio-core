# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_systype


class Linux_armPlatform(BasePlatform):

    """
        Linux ARM is a Unix-like and mostly POSIX-compliant computer
        operating system (OS) assembled under the model of free and open-source
        software development and distribution.

        Using host OS (Mac OS X, Linux ARM) you can build native application
        for Linux ARM platform.

        http://platformio.org/#!/platforms/linux_arm
    """

    PACKAGES = {

        "toolchain-gccarmlinuxgnueabi": {
            "alias": "toolchain",
            "default": True
        }
    }

    def __init__(self):
        if "linux_arm" in get_systype():
            del self.PACKAGES['toolchain-gccarmlinuxgnueabi']
        BasePlatform.__init__(self)

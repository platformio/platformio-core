# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_systype


class Linux_i686Platform(BasePlatform):

    """
        Linux i686 (32-bit) is a Unix-like and mostly POSIX-compliant
        computer operating system (OS) assembled under the model of free and
        open-source software development and distribution.

        Using host OS (Mac OS X or Linux 32-bit) you can build native
        application for Linux i686 platform.

        http://platformio.org/#!/platforms/linux_i686
    """

    PACKAGES = {

        "toolchain-gcclinux32": {
            "alias": "toolchain",
            "default": True
        }
    }

    def __init__(self):
        if get_systype() == "linux_i686":
            del self.PACKAGES['toolchain-gcclinux32']
        BasePlatform.__init__(self)

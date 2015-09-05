# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform
from platformio.util import get_systype


class Linux_x86_64Platform(BasePlatform):

    """
        Linux x86_64 (64-bit) is a Unix-like and mostly POSIX-compliant
        computer operating system (OS) assembled under the model of free and
        open-source software development and distribution.

        Using host OS (Mac OS X or Linux 64-bit) you can build native
        application for Linux x86_64 platform.

        http://platformio.org/#!/platforms/linux_i686
    """

    PACKAGES = {

        "toolchain-gcclinux64": {
            "alias": "toolchain",
            "default": True
        }
    }

    def __init__(self):
        if get_systype() == "linux_x86_64":
            del self.PACKAGES['toolchain-gcclinux64']
        BasePlatform.__init__(self)

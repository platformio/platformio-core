# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class Windows_x86Platform(BasePlatform):

    """
        Windows x86 (32-bit) is a metafamily of graphical operating systems
        developed and marketed by Microsoft.
        Using host OS (Windows, Linux 32/64 or Mac OS X) you can build native
        application for Windows x86 platform.

        http://platformio.org/#!/platforms/windows_x86
    """

    PACKAGES = {

        "toolchain-gccmingw32": {
            "alias": "toolchain",
            "default": True
        }
    }

# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class NativePlatform(BasePlatform):

    """
    Native development platform is intended to be used for desktop OS.
    This platform uses built-in tool chains (preferable based on GCC),
    frameworks, libs from particular OS where it will be run.

    http://platformio.org/#!/platforms/native
    """

    PACKAGES = {
    }

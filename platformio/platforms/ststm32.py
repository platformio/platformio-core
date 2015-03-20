# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class Ststm32Platform(BasePlatform):

    """
    The STM32 family of 32-bit Flash MCUs based on the ARM Cortex-M
    processor is designed to offer new degrees of freedom to MCU users.
    It offers a 32-bit product range that combines very high performance,
    real-time capabilities, digital signal processing, and low-power,
    low-voltage operation, while maintaining full integration and ease of
    development.

    http://www.st.com/web/en/catalog/mmc/FM141/SC1169?sc=stm32
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "tool-stlink": {
            "alias": "uploader",
            "default": True
        },

        "framework-cmsis": {
            "default": True
        },

        "framework-spl": {
            "default": True
        },

        "framework-libopencm3": {
            "default": True
        },

        "framework-mbed": {
            "default": True
        }
    }

    def get_name(self):
        return "ST STM32"

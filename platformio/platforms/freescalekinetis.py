# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class FreescalekinetisPlatform(BasePlatform):

    """
    Freescale Kinetis Microcontrollers is family of multiple hardware- and
    software-compatible ARM Cortex-M0+, Cortex-M4 and Cortex-M7-based MCU
    series. Kinetis MCUs offer exceptional low-power performance,
    scalability and feature integration.

    http://www.freescale.com/webapp/sps/site/homepage.jsp?code=KINETIS
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "framework-mbed": {
            "default": True
        }
    }

    def get_name(self):
        return "Freescale Kinetis"

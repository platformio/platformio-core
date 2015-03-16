# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platformio.platforms.base import BasePlatform


class TitivaPlatform(BasePlatform):

    """
    Texas Instruments TM4C12x MCUs offer the industrys most popular
    ARM Cortex-M4 core with scalable memory and package options, unparalleled
    connectivity peripherals, advanced application functions, industry-leading
    analog integration, and extensive software solutions.

    http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/c2000_performance/control_automation/tm4c12x/overview.page
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "tool-lm4flash": {
            "alias": "uploader",
            "default": True
        },

        "framework-energiativa": {
            "default": True
        },

        "framework-libopencm3": {
            "default": True
        }
    }

    def get_name(self):
        return "TI TIVA"

# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
            "alias": "uploader"
        },

        "framework-energiativa": {
            "alias": "framework"
        },

        "framework-libopencm3": {
            "alias": "framework"
        }
    }

    def get_name(self):
        return "TI TIVA"

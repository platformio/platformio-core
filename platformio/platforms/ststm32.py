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
            "alias": "uploader"
        },

        "framework-cmsis": {
            "alias": "framework"
        },

        "framework-spl": {
            "alias": "framework"
        },

        "framework-libopencm3": {
            "alias": "framework"
        },

        "framework-mbed": {
            "alias": "framework"
        }
    }

    def get_name(self):
        return "ST STM32"

    def configure_default_packages(self, envoptions, targets):
        if envoptions.get("framework") == "cmsis":
            self.PACKAGES['framework-mbed']['default'] = True

        return BasePlatform.configure_default_packages(
            self, envoptions, targets)

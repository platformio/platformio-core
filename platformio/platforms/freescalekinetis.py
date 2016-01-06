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
            "alias": "framework"
        }
    }

    def get_name(self):
        return "Freescale Kinetis"

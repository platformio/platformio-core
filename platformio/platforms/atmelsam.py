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
from platformio.util import get_boards


class AtmelsamPlatform(BasePlatform):

    """
    Atmel | SMART offers Flash- based ARM products based on the ARM
    Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB
    to 2MB of Flash including a rich peripheral and feature mix.

    http://www.atmel.com/products/microcontrollers/arm/default.aspx
    """

    PACKAGES = {

        "toolchain-gccarmnoneeabi": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "framework-arduinosam": {
            "alias": "framework"
        },

        "framework-mbed": {
            "alias": "framework"
        },

        "framework-simba": {
            "alias": "framework"
        },

        "tool-bossac": {
        },

        "tool-openocd": {
        },

        "tool-avrdude": {
        }
    }

    def get_name(self):
        return "Atmel SAM"

    def configure_default_packages(self, envoptions, targets):
        if envoptions.get("board"):
            board = get_boards(envoptions.get("board"))
            upload_protocol = board.get("upload", {}).get("protocol", None)
            upload_tool = None
            if upload_protocol == "openocd":
                upload_tool = "tool-openocd"
            elif upload_protocol == "sam-ba":
                upload_tool = "tool-bossac"
            elif upload_protocol == "stk500v2":
                upload_tool = "tool-avrdude"

            if upload_tool:
                self.PACKAGES[upload_tool]['alias'] = "uploader"

        return BasePlatform.configure_default_packages(
            self, envoptions, targets)

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


class AtmelavrPlatform(BasePlatform):

    """
    Atmel AVR 8- and 32-bit MCUs deliver a unique combination of
    performance, power efficiency and design flexibility. Optimized to
    speed time to market-and easily adapt to new ones-they are based on
    the industrys most code-efficient architecture for C and assembly
    programming.

    http://www.atmel.com/products/microcontrollers/avr/default.aspx
    """

    PACKAGES = {

        "toolchain-atmelavr": {
            "alias": "toolchain",
            "default": True
        },

        "tool-avrdude": {
            "alias": "uploader"
        },

        "tool-micronucleus": {
            "alias": "uploader"
        },

        "framework-arduinoavr": {
            "alias": "framework"
        },

        "framework-simba": {
            "alias": "framework"
        }
    }

    def get_name(self):
        return "Atmel AVR"

    def configure_default_packages(self, envoptions, targets):
        if envoptions.get("board"):
            board = get_boards(envoptions.get("board"))
            disable_tool = "tool-micronucleus"
            if "digispark" in board['build']['core']:
                disable_tool = "tool-avrdude"
            del self.PACKAGES[disable_tool]['alias']

        return BasePlatform.configure_default_packages(
            self, envoptions, targets)

    def on_run_err(self, line):  # pylint: disable=R0201
        # fix STDERR "flash written" for avrdude
        if "avrdude" in line:
            self.on_run_out(line)
        else:
            BasePlatform.on_run_err(self, line)

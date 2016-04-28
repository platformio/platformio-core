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


class EspressifPlatform(BasePlatform):

    """
    Espressif Systems is a privately held fabless semiconductor company.
    They provide wireless communications and Wi-Fi chips which are widely
    used in mobile devices and the Internet of Things applications.

    https://espressif.com/
    """

    PACKAGES = {

        "toolchain-xtensa": {
            "alias": "toolchain",
            "default": True
        },

        "ldscripts": {
            "default": True
        },

        "tool-esptool": {
            "alias": "uploader",
            "default": True
        },

        "tool-mkspiffs": {
            "alias": "uploader"
        },

        "sdk-esp8266": {
        },

        "framework-arduinoespressif": {
            "alias": "framework"
        },

        "framework-simba": {
            "alias": "framework"
        }
    }

    def get_name(self):
        return "Espressif"

    def configure_default_packages(self, envoptions, targets):
        if not envoptions.get("framework"):
            self.PACKAGES['sdk-esp8266']['default'] = True

        return BasePlatform.configure_default_packages(
            self, envoptions, targets)

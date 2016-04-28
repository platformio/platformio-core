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


class Intel_arc32Platform(BasePlatform):

    """
    ARC embedded processors are a family of 32-bit CPUs that are widely used
    in SoC devices for storage, home, mobile, automotive, and Internet of
    Things applications.

    http://www.intel.com/content/www/us/en/wearables/wearable-soc.html
    """

    PACKAGES = {

        "toolchain-intelarc32": {
            "alias": "toolchain",
            "default": True
        },

        "framework-arduinointel": {
            "alias": "framework"
        },

        "tool-arduino101load": {
            "alias": "uploader"
        },
    }

    def get_name(self):
        return "Intel ARC32"

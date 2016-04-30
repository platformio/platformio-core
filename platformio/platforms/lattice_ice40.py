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


class Lattice_ice40Platform(BasePlatform):

    """
    The iCE40 family of ultra-low power, non-volatile FPGAs has five devices
    with densities ranging from 384 to 7680 Look-Up Tables (LUTs). In addition
    to LUT-based,low-cost programmable logic, these devices feature Embedded
    Block RAM (EBR), Non-volatile Configuration Memory (NVCM) and Phase Locked
    Loops (PLLs). These features allow the devices to be used in low-cost,
    high-volume consumer and system applications.

    http://www.latticesemi.com/Products/FPGAandCPLD/iCE40.aspx
    """

    PACKAGES = {

        "toolchain-icestorm": {
            "alias": "toolchain",
            "default": True
        }
    }

    def get_name(self):
        return "Lattice iCE40"

    def is_embedded(self):
        return True

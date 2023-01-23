# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

import sys

VERSION = (6, 1, 6)
__version__ = ".".join([str(s) for s in VERSION])

__title__ = "platformio"
__description__ = (
    "A professional collaborative platform for embedded development. "
    "Cross-platform IDE and Unified Debugger. "
    "Static Code Analyzer and Remote Unit Testing. "
    "Multi-platform and Multi-architecture Build System. "
    "Firmware File Explorer and Memory Inspection. "
    "IoT, Arduino, CMSIS, ESP-IDF, FreeRTOS, libOpenCM3, mbedOS, Pulp OS, SPL, "
    "STM32Cube, Zephyr RTOS, ARM, AVR, Espressif (ESP8266/ESP32), FPGA, "
    "MCS-51 (8051), MSP430, Nordic (nRF51/nRF52), NXP i.MX RT, PIC32, RISC-V, "
    "STMicroelectronics (STM8/STM32), Teensy"
)
__url__ = "https://platformio.org"

__author__ = "PlatformIO Labs"
__email__ = "contact@piolabs.com"

__license__ = "Apache Software License"
__copyright__ = "Copyright 2014-present PlatformIO Labs"

__accounts_api__ = "https://api.accounts.platformio.org"
__registry_mirror_hosts__ = [
    "registry.platformio.org",
    "registry.nm1.platformio.org",
]
__pioremote_endpoint__ = "ssl:host=remote.platformio.org:port=4413"

__core_packages__ = {
    "contrib-piohome": "~3.4.2",
    "contrib-pysite": "~2.%d%d.0" % (sys.version_info.major, sys.version_info.minor),
    "tool-scons": "~4.40400.0",
    "tool-cppcheck": "~1.270.0",
    "tool-clangtidy": "~1.150005.0",
    "tool-pvs-studio": "~7.18.0",
}

__check_internet_hosts__ = [
    "185.199.110.153",  # Github.com
    "88.198.170.159",  # platformio.org
    "github.com",
] + __registry_mirror_hosts__

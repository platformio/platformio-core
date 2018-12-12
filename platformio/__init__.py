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

VERSION = (3, 6, 3)
__version__ = ".".join([str(s) for s in VERSION])

__title__ = "platformio"
__description__ = (
    "An open source ecosystem for IoT development. "
    "Cross-platform IDE and unified debugger. "
    "Remote unit testing and firmware updates. "
    "Arduino, ARM mbed, Espressif (ESP8266/ESP32), STM32, PIC32, nRF51/nRF52, "
    "FPGA, CMSIS, SPL, AVR, Samsung ARTIK, libOpenCM3")
__url__ = "https://platformio.org"

__author__ = "PlatformIO"
__email__ = "contact@platformio.org"

__license__ = "Apache Software License"
__copyright__ = "Copyright 2014-present PlatformIO"

__apiurl__ = "https://api.platformio.org"

if sys.version_info < (2, 7, 0) or sys.version_info >= (3, 0, 0):
    msg = ("PlatformIO Core v%s does not run under Python version %s.\n"
           "Minimum supported version is 2.7, please upgrade Python.\n"
           "Python 3 is not yet supported.\n")
    sys.stderr.write(msg % (__version__, sys.version))
    sys.exit(1)

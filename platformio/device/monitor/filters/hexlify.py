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

import serial

from platformio.device.monitor.filters.base import DeviceMonitorFilterBase


class Hexlify(DeviceMonitorFilterBase):
    NAME = "hexlify"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = 0

    def set_running_terminal(self, terminal):
        # force to Latin-1, issue #4732
        if terminal.input_encoding == "UTF-8":
            terminal.set_rx_encoding("Latin-1")
        super().set_running_terminal(terminal)

    def rx(self, text):
        result = ""
        for c in serial.iterbytes(text):
            if (self._counter % 16) == 0:
                result += "\n{:04X} | ".format(self._counter)
            asciicode = ord(c)
            if asciicode <= 255:
                result += "{:02X} ".format(asciicode)
            else:
                result += "?? "
            self._counter += 1
        return result

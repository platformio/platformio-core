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

from platformio.device.monitor.filters.base import DeviceMonitorFilterBase


class SendOnEnter(DeviceMonitorFilterBase):
    NAME = "send_on_enter"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer = ""

        if self.options.get("eol") == "CR":
            self._eol = "\r"
        elif self.options.get("eol") == "LF":
            self._eol = "\n"
        else:
            self._eol = "\r\n"

    def tx(self, text):
        self._buffer += text
        if self._buffer.endswith(self._eol):
            text = self._buffer
            self._buffer = ""
            return text
        return ""

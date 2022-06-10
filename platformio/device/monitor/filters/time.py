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

from datetime import datetime

from platformio.device.monitor.filters.base import DeviceMonitorFilterBase


class Timestamp(DeviceMonitorFilterBase):
    NAME = "time"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._line_started = False

    def rx(self, text):
        if self._line_started and "\n" not in text:
            return text
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if not self._line_started:
            self._line_started = True
            text = "%s > %s" % (timestamp, text)
        if text.endswith("\n"):
            self._line_started = False
            return text[:-1].replace("\n", "\n%s > " % timestamp) + "\n"
        return text.replace("\n", "\n%s > " % timestamp)

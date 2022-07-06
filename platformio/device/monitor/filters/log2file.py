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

import io
import os.path
from datetime import datetime

from platformio.device.monitor.filters.base import DeviceMonitorFilterBase


class LogToFile(DeviceMonitorFilterBase):
    NAME = "log2file"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_fp = None

    def __call__(self):
        log_file_name = "platformio-device-monitor-%s.log" % datetime.now().strftime(
            "%y%m%d-%H%M%S"
        )
        print("--- Logging an output to %s" % os.path.abspath(log_file_name))
        # pylint: disable=consider-using-with
        self._log_fp = io.open(log_file_name, "w", encoding="utf-8")
        return self

    def __del__(self):
        if self._log_fp:
            self._log_fp.close()

    def rx(self, text):
        self._log_fp.write(text)
        self._log_fp.flush()
        return text

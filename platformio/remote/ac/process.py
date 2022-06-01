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

import os

from twisted.internet import protocol, reactor  # pylint: disable=import-error

from platformio.remote.ac.base import AsyncCommandBase


class ProcessAsyncCmd(protocol.ProcessProtocol, AsyncCommandBase):
    def start(self):
        env = dict(os.environ).copy()
        env.update({"PLATFORMIO_FORCE_ANSI": "true"})
        reactor.spawnProcess(
            self, self.options["executable"], self.options["args"], env
        )

    def outReceived(self, data):
        self._ac_ondata(data)

    def errReceived(self, data):
        self._ac_ondata(data)

    def processExited(self, reason):
        self._return_code = reason.value.exitCode

    def processEnded(self, reason):
        if self._return_code is None:
            self._return_code = reason.value.exitCode
        self._ac_ended()

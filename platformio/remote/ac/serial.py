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

from time import sleep

from twisted.internet import protocol, reactor  # pylint: disable=import-error
from twisted.internet.serialport import SerialPort  # pylint: disable=import-error

from platformio.remote.ac.base import AsyncCommandBase


class SerialPortAsyncCmd(protocol.Protocol, AsyncCommandBase):
    def start(self):
        SerialPort(
            self,
            reactor=reactor,
            **{
                "deviceNameOrPortNumber": self.options["port"],
                "baudrate": self.options["baud"],
                "parity": self.options["parity"],
                "rtscts": 1 if self.options["rtscts"] else 0,
                "xonxoff": 1 if self.options["xonxoff"] else 0,
            }
        )

    def connectionMade(self):
        self.reset_device()
        if self.options.get("rts", None) is not None:
            self.transport.setRTS(self.options.get("rts"))
        if self.options.get("dtr", None) is not None:
            self.transport.setDTR(self.options.get("dtr"))

    def reset_device(self):
        self.transport.flushInput()
        self.transport.setDTR(False)
        self.transport.setRTS(False)
        sleep(0.1)
        self.transport.setDTR(True)
        self.transport.setRTS(True)
        sleep(0.1)

    def dataReceived(self, data):
        self._ac_ondata(data)

    def connectionLost(self, reason):  # pylint: disable=unused-argument
        if self._paused:
            return
        self._return_code = 0
        self._ac_ended()

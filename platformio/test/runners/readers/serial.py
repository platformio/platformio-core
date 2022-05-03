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

import click
import serial

from platformio import util
from platformio.exception import UserSideException


class SerialTestOutputReader:

    SERIAL_TIMEOUT = 600

    def __init__(self, test_runner):
        self.test_runner = test_runner

    def begin(self):
        click.echo(
            "If you don't see any output for the first 10 secs, "
            "please reset board (press reset button)"
        )
        click.echo()

        try:
            ser = serial.Serial(
                baudrate=self.test_runner.get_test_speed(), timeout=self.SERIAL_TIMEOUT
            )
            ser.port = self.get_test_port()
            ser.rts = self.test_runner.options.monitor_rts
            ser.dtr = self.test_runner.options.monitor_dtr
            ser.open()
        except serial.SerialException as e:
            click.secho(str(e), fg="red", err=True)
            return None

        if not self.test_runner.options.no_reset:
            ser.flushInput()
            ser.setDTR(False)
            ser.setRTS(False)
            sleep(0.1)
            ser.setDTR(True)
            ser.setRTS(True)
            sleep(0.1)

        while not self.test_runner.test_suite.is_finished():
            line = ser.readline().strip()

            # fix non-ascii output from device
            for i, c in enumerate(line[::-1]):
                if not isinstance(c, int):
                    c = ord(c)
                if c > 127:
                    line = line[-i:]
                    break

            if not line:
                continue
            if isinstance(line, bytes):
                line = line.decode("utf8", "ignore")
            self.test_runner.on_test_output(line)
        ser.close()

    def get_test_port(self):
        # if test port is specified manually or in config
        port = (
            self.test_runner.options.test_port
            or self.test_runner.project_config.get(
                f"env:{self.test_runner.test_suite.env_name}", "test_port"
            )
        )
        if port:
            return port

        board = self.test_runner.project_config.get(
            f"env:{self.test_runner.test_suite.env_name}", "board"
        )
        board_hwids = self.test_runner.platform.board_config(board).get(
            "build.hwids", []
        )
        port = None
        elapsed = 0
        while elapsed < 5 and not port:
            for item in util.get_serialports():
                port = item["port"]
                for hwid in board_hwids:
                    hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                    if hwid_str in item["hwid"] and self.is_serial_port_ready(port):
                        return port

            if port and not self.is_serial_port_ready(port):
                port = None

            if not port:
                sleep(0.25)
                elapsed += 0.25

        if not port:
            raise UserSideException(
                "Please specify `test_port` for environment or use "
                "global `--test-port` option."
            )
        return port

    @staticmethod
    def is_serial_port_ready(port, timeout=3):
        if not port:
            return False
        elapsed = 0
        while elapsed < timeout:
            try:
                serial.Serial(port, timeout=1).close()
                return True
            except:  # pylint: disable=bare-except
                pass
            sleep(1)
            elapsed += 1
        return False

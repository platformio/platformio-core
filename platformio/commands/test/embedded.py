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

from platformio import exception, util
from platformio.commands.test.processor import TestProcessorBase
from platformio.managers.platform import PlatformFactory


class EmbeddedTestProcessor(TestProcessorBase):

    SERIAL_TIMEOUT = 600

    def process(self):
        if not self.options["without_building"]:
            self.print_progress("Building...")
            target = ["__test"]
            if self.options["without_uploading"]:
                target.append("checkprogsize")
            if not self.build_or_upload(target):
                return False

        if not self.options["without_uploading"]:
            self.print_progress("Uploading...")
            target = ["upload"]
            if self.options["without_building"]:
                target.append("nobuild")
            else:
                target.append("__test")
            if not self.build_or_upload(target):
                return False

        if self.options["without_testing"]:
            return True

        self.print_progress("Testing...")
        return self.run()

    def run(self):
        click.echo(
            "If you don't see any output for the first 10 secs, "
            "please reset board (press reset button)"
        )
        click.echo()

        try:
            ser = serial.Serial(
                baudrate=self.get_baudrate(), timeout=self.SERIAL_TIMEOUT
            )
            ser.port = self.get_test_port()
            ser.rts = self.options["monitor_rts"]
            ser.dtr = self.options["monitor_dtr"]
            ser.open()
        except serial.SerialException as e:
            click.secho(str(e), fg="red", err=True)
            return False

        if not self.options["no_reset"]:
            ser.flushInput()
            ser.setDTR(False)
            ser.setRTS(False)
            sleep(0.1)
            ser.setDTR(True)
            ser.setRTS(True)
            sleep(0.1)

        while True:
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
            self.on_run_out(line)
            if all([l in line for l in ("Tests", "Failures", "Ignored")]):
                break
        ser.close()
        return not self._run_failed

    def get_test_port(self):
        # if test port is specified manually or in config
        if self.options.get("test_port"):
            return self.options.get("test_port")
        if self.env_options.get("test_port"):
            return self.env_options.get("test_port")

        assert set(["platform", "board"]) & set(self.env_options.keys())
        p = PlatformFactory.newPlatform(self.env_options["platform"])
        board_hwids = p.board_config(self.env_options["board"]).get("build.hwids", [])
        port = None
        elapsed = 0
        while elapsed < 5 and not port:
            for item in util.get_serialports():
                port = item["port"]
                for hwid in board_hwids:
                    hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                    if hwid_str in item["hwid"]:
                        return port

            # check if port is already configured
            try:
                serial.Serial(port, timeout=self.SERIAL_TIMEOUT).close()
            except serial.SerialException:
                port = None

            if not port:
                sleep(0.25)
                elapsed += 0.25

        if not port:
            raise exception.PlatformioException(
                "Please specify `test_port` for environment or use "
                "global `--test-port` option."
            )
        return port

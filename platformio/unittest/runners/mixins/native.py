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
import signal

from platformio import proc
from platformio.unittest.exception import UnitTestError


class TestRunnerNativeMixin:
    def stage_run_on_host(self):
        build_dir = self.project_config.get("platformio", "build_dir")
        result = proc.exec_command(
            [os.path.join(build_dir, self.test_suite.env_name, "program")],
            stdout=proc.LineBufferedAsyncPipe(self.on_run_output),
            stderr=proc.LineBufferedAsyncPipe(self.on_run_output),
        )
        if result["returncode"] == 0:
            return True
        try:
            sig = signal.Signals(abs(result["returncode"]))
            try:
                signal_description = signal.strsignal(sig)
            except AttributeError:
                signal_description = ""
            raise UnitTestError(
                f"Program received signal {sig.name} ({signal_description})"
            )
        except ValueError:
            raise UnitTestError("Program errored with %d code" % result["returncode"])

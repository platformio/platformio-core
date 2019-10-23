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

from os.path import join

from platformio import proc
from platformio.commands.test.processor import TestProcessorBase
from platformio.proc import LineBufferedAsyncPipe


class NativeTestProcessor(TestProcessorBase):
    def process(self):
        if not self.options["without_building"]:
            self.print_progress("Building...")
            if not self.build_or_upload(["__test"]):
                return False
        if self.options["without_testing"]:
            return None
        self.print_progress("Testing...")
        return self.run()

    def run(self):
        build_dir = self.options["project_config"].get_optional_dir("build")
        result = proc.exec_command(
            [join(build_dir, self.env_name, "program")],
            stdout=LineBufferedAsyncPipe(self.on_run_out),
            stderr=LineBufferedAsyncPipe(self.on_run_out),
        )
        assert "returncode" in result
        return result["returncode"] == 0 and not self._run_failed

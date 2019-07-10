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

from platformio import util
from platformio.commands.test.processor import TestProcessorBase
from platformio.proc import LineBufferedAsyncPipe
from platformio.project.helpers import get_project_build_dir


class NativeTestProcessor(TestProcessorBase):

    def process(self):
        if not self.options['without_building']:
            self.print_progress("Building... (1/2)")
            if not self.build_or_upload(["__test"]):
                return False
        if self.options['without_testing']:
            return None
        self.print_progress("Testing... (2/2)")
        return self.run()

    def run(self):
        with util.cd(self.options['project_dir']):
            build_dir = get_project_build_dir()
        result = util.exec_command(
            [join(build_dir, self.env_name, "program")],
            stdout=LineBufferedAsyncPipe(self.on_run_out),
            stderr=LineBufferedAsyncPipe(self.on_run_out))
        assert "returncode" in result
        return result['returncode'] == 0 and not self._run_failed

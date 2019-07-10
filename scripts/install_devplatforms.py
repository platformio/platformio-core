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

import json
import subprocess
import sys
from platformio import util


def main():
    platforms = json.loads(
        subprocess.check_output(
            ["platformio", "platform", "search", "--json-output"]).decode())
    for platform in platforms:
        if platform['forDesktop']:
            continue
        # RISC-V GAP does not support Windows 86
        if (util.get_systype() == "windows_x86"
                and platform['name'] == "riscv_gap"):
            continue
        # unknown issue on Linux
        if ("linux" in util.get_systype()
                and platform['name'] == "aceinna_imu"):
            continue
        subprocess.check_call(
            ["platformio", "platform", "install", platform['name']])


if __name__ == "__main__":
    sys.exit(main())

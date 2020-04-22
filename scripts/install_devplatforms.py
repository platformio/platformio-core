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
            ["platformio", "platform", "search", "--json-output"]
        ).decode()
    )
    for platform in platforms:
        skip = [
            platform["forDesktop"],
            platform["name"] in ("ststm8", "infineonxmc", "microchippic32"),
            # RISC-V GAP does not support Windows 86
            util.get_systype() == "windows_x86" and platform["name"] == "riscv_gap",
            # intel_mcs51: "version `CXXABI_1.3.9' not found (required by sdcc)"
            # microchippic32: GCC does not work on x64
            "linux" in util.get_systype()
            and platform["name"] in ("aceinna_imu", "intel_mcs51"),
            "darwin" in util.get_systype() and platform["name"] in ("gd32v", "nuclei"),
        ]
        if any(skip):
            continue
        subprocess.check_call(["platformio", "platform", "install", platform["name"]])


if __name__ == "__main__":
    sys.exit(main())

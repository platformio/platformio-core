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


def main():
    platforms = json.loads(
        subprocess.check_output(
            ["platformio", "platform", "search", "--json-output"]))
    for platform in platforms:
        if platform['forDesktop']:
            continue
        subprocess.check_call(
            ["platformio", "platform", "install", platform['repository']])


if __name__ == "__main__":
    sys.exit(main())

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

import pytest

from platformio import util
from platformio.commands.test.command import cli as cmd_test


def test_local_env():
    result = util.exec_command(
        [
            "platformio",
            "test",
            "-d",
            join("examples", "unit-testing", "calculator"),
            "-e",
            "native",
        ]
    )
    if result["returncode"] != 1:
        pytest.fail(str(result))
    assert all([s in result["err"] for s in ("PASSED", "IGNORED", "FAILED")]), result[
        "out"
    ]


def test_multiple_env_build(clirunner, validate_cliresult, tmpdir):

    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
[env:teensy31]
platform = teensy
framework = mbed
board = teensy31

[env:native]
platform = native

[env:espressif32]
platform = espressif32
framework = arduino
board = esp32dev
"""
    )

    project_dir.mkdir("test").join("test_main.cpp").write(
        """
#ifdef ARDUINO
void setup() {}
void loop() {}
#else
int main() {
    UNITY_BEGIN();
    UNITY_END();
}
#endif
"""
    )

    result = clirunner.invoke(
        cmd_test, ["-d", str(project_dir), "--without-testing", "--without-uploading"],
    )

    validate_cliresult(result)
    assert "Multiple ways to build" not in result.output

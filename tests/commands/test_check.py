# Copyright (c) 2019-present PlatformIO <contact@platformio.org>
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

from platformio import proc


def test_check_is_performed():
    result = proc.exec_command([
        "platformio", "check", "-d",
        join("examples", "static-analysis"),
        "-e", "native"
    ])

    if result['returncode'] != 1:
        pytest.fail(result)

    error, warning = 0, 0
    for l in result['err'].split("\n"):
        if "(error)" in l:
            error += 1
        elif "(style)" in l:
            warning += 1

    expected_errors, expected_warnings = 6, 4
    assert (error == expected_errors and warning == expected_warnings)


def test_defines_are_passed():
    result = proc.exec_command([
        "platformio", "check", "-d",
        join("examples", "static-analysis"),
        "-e", "nucleo_f401re", "-v"
    ])

    if result['returncode'] != 1:
        pytest.fail(result)

    assert ("PLATFORMIO=" in result['out'])
    assert ("__GNUC__" in result['out'])


def test_includes_are_passed():
    result = proc.exec_command([
        "platformio", "check", "-d",
        join("examples", "static-analysis"),
        "-e", "native", "-v"
    ])

    if result['returncode'] != 1:
        pytest.fail(result)

    inc_count = 0
    for l in result['out'].split("\n"):
        if l.startswith("Includes:"):
            inc_count = l.count("-I")

    # at least 1 include path for default mode
    assert(inc_count > 1)

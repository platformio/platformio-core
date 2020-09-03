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

import pytest

from platformio import proc
from platformio.commands.test.command import cli as cmd_test


def test_local_env():
    result = proc.exec_command(
        [
            "platformio",
            "test",
            "-d",
            os.path.join("examples", "unit-testing", "calculator"),
            "-e",
            "native",
        ]
    )
    if result["returncode"] != 1:
        pytest.fail(str(result))
    # pylint: disable=unsupported-membership-test
    assert all([s in result["err"] for s in ("PASSED", "IGNORED", "FAILED")]), result[
        "out"
    ]


def test_multiple_env_build(clirunner, validate_cliresult, tmpdir):

    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
[env:teensy31]
platform = teensy
framework = arduino
board = teensy31

[env:native]
platform = native

[env:espressif8266]
platform = espressif8266
framework = arduino
board = nodemcuv2
"""
    )

    project_dir.mkdir("test").join("test_main.cpp").write(
        """
#include <unity.h>
#ifdef ARDUINO
void setup()
#else
int main()
#endif
{
    UNITY_BEGIN();
    UNITY_END();

}
void loop() {}
"""
    )

    result = clirunner.invoke(
        cmd_test, ["-d", str(project_dir), "--without-testing", "--without-uploading"],
    )

    validate_cliresult(result)
    assert "Multiple ways to build" not in result.output


def test_setup_teardown_are_compilable(clirunner, validate_cliresult, tmpdir):

    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
[env:embedded]
platform = ststm32
framework = stm32cube
board = nucleo_f401re
test_transport = custom

[env:native]
platform = native

"""
    )

    test_dir = project_dir.mkdir("test")
    test_dir.join("test_main.c").write(
        """
#include <stdio.h>
#include <unity.h>

void setUp(){
    printf("setUp called");
}
void tearDown(){
    printf("tearDown called");
}

void dummy_test(void) {
    TEST_ASSERT_EQUAL(1, 1);
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(dummy_test);
    UNITY_END();
}
"""
    )

    native_result = clirunner.invoke(
        cmd_test, ["-d", str(project_dir), "-e", "native"],
    )

    test_dir.join("unittest_transport.h").write(
        """
#ifdef __cplusplus
extern "C" {
#endif

void unittest_uart_begin(){}
void unittest_uart_putchar(char c){}
void unittest_uart_flush(){}
void unittest_uart_end(){}

#ifdef __cplusplus
}
#endif
"""
    )

    embedded_result = clirunner.invoke(
        cmd_test,
        [
            "-d",
            str(project_dir),
            "--without-testing",
            "--without-uploading",
            "-e",
            "embedded",
        ],
    )

    validate_cliresult(native_result)
    validate_cliresult(embedded_result)

    assert all(f in native_result.output for f in ("setUp called", "tearDown called"))
    assert all(
        "[FAILED]" not in out for out in (native_result.output, embedded_result.output)
    )

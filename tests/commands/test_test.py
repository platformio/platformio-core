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
import subprocess

from platformio import proc
from platformio.unittest.command import unittest_cmd


def test_unity_calculator():
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
    assert result["returncode"] != 0
    # pylint: disable=unsupported-membership-test
    assert all(
        s in (result["err"] + result["out"]) for s in ("PASSED", "FAILED")
    ), result["out"]

    result = subprocess.run(  # pylint: disable=subprocess-run-check
        [
            "platformio",
            "test",
            "-d",
            os.path.join("examples", "unit-testing", "calculator"),
            "-e",
            "native",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert all(s in str(result) for s in ("PASSED", "FAILED"))


def test_unity_setup_teardown(clirunner, validate_cliresult, tmpdir):
    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
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
    result = clirunner.invoke(
        unittest_cmd,
        ["-d", str(project_dir), "-e", "native"],
    )
    validate_cliresult(result)
    assert all(f in result.output for f in ("setUp called", "tearDown called"))


def test_crashed_program(clirunner, tmpdir):
    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
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

int main(int argc, char *argv[]) {
    printf("Address boundary error is %s", argv[-1]);
    UNITY_BEGIN();
    RUN_TEST(dummy_test);
    UNITY_END();
    return 0;
}
"""
    )
    result = clirunner.invoke(
        unittest_cmd,
        ["-d", str(project_dir), "-e", "native"],
    )
    assert result.exit_code != 0
    assert any(
        s in result.output for s in ("Program received signal", "Program errored with")
    )


def test_legacy_unity_custom_transport(clirunner, validate_cliresult, tmpdir):
    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
[env:embedded]
platform = ststm32
framework = stm32cube
board = nucleo_f401re
test_transport = custom
"""
    )

    test_dir = project_dir.mkdir("test")
    test_dir.join("test_main.c").write(
        """
#include <unity.h>

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
    result = clirunner.invoke(
        unittest_cmd,
        [
            "-d",
            str(project_dir),
            "--without-testing",
            "--without-uploading",
        ],
    )
    validate_cliresult(result)

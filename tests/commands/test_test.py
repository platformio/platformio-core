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
import xml.etree.ElementTree as ET
from pathlib import Path

from platformio import proc
from platformio.test.command import test_cmd as pio_test_cmd


def test_calculator_example(tmp_path: Path):
    junit_output_path = tmp_path / "junit.xml"
    result = proc.exec_command(
        [
            "platformio",
            "test",
            "-d",
            os.path.join("examples", "unit-testing", "calculator"),
            "-e",
            "uno",
            "-e",
            "native",
            "--output-format=junit",
            "--output-path",
            str(junit_output_path),
        ]
    )
    assert result["returncode"] != 0
    # pylint: disable=unsupported-membership-test
    assert all(
        s in (result["err"] + result["out"]) for s in ("ERRORED", "PASSED", "FAILED")
    ), result["out"]

    # test JUnit output
    junit_testsuites = ET.parse(junit_output_path).getroot()
    assert int(junit_testsuites.get("tests")) == 11
    assert int(junit_testsuites.get("errors")) == 2
    assert int(junit_testsuites.get("failures")) == 1
    assert len(junit_testsuites.findall("testsuite")) == 6
    junit_errored_testcase = junit_testsuites.find(
        ".//testcase[@name='uno:test_embedded']"
    )
    assert junit_errored_testcase.get("status") == "ERRORED"
    assert junit_errored_testcase.find("error").get("type") == "UnitTestSuiteError"
    junit_failed_testcase = junit_testsuites.find(
        ".//testsuite[@name='native:test_desktop']"
        "/testcase[@name='test_calculator_division']"
    )
    assert junit_failed_testcase.get("status") == "FAILED"
    assert junit_failed_testcase.find("failure").get("message") == "Expected 32 Was 33"


def test_nested_suites(clirunner, validate_cliresult, tmp_path: Path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
"""
    )
    test_dir = project_dir / "test"

    # non-test folder, does not start with "test_"
    disabled_dir = test_dir / "disabled"
    disabled_dir.mkdir(parents=True)
    (disabled_dir / "main.c").write_text(
        """
#include <stdio.h>

int main() {
    printf("Disabled test suite\\n")
}
    """
    )

    # root
    (test_dir / "my_extra.h").write_text(
        """
#ifndef MY_EXTRA_H
#define MY_EXTRA_H

#include <stdio.h>

void my_extra_fun(void);
#endif
"""
    )
    (test_dir / "my_extra.c").write_text(
        """
#include "my_extra.h"

void my_extra_fun(void) {
    printf("Called from my_extra_fun\\n");
}
"""
    )

    # test suite
    test_suite_dir = test_dir / "set" / "test_nested"
    test_include_dir = test_suite_dir / "include"
    test_include_dir.mkdir(parents=True)
    (test_include_dir / "my_nested.h").write_text(
        """
#define TEST_ONE 1
"""
    )
    (test_suite_dir / "main.c").write_text(
        """
#include <unity.h>
#include <my_extra.h>
#include <include/my_nested.h>

void setUp(){
    my_extra_fun();
}

void tearDown(void) {
    // clean stuff up here
}

void dummy_test(void) {
    TEST_ASSERT_EQUAL(1, TEST_ONE);
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(dummy_test);
    UNITY_END();
}
    """
    )
    result = clirunner.invoke(
        pio_test_cmd,
        ["-d", str(project_dir), "-e", "native"],
    )
    validate_cliresult(result)
    assert "Called from my_extra_fun" in result.output
    assert "Disabled test suite" not in result.output


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
        pio_test_cmd,
        ["-d", str(project_dir), "-e", "native"],
    )
    assert result.exit_code != 0
    assert any(
        s in result.output for s in ("Program received signal", "Program errored with")
    )


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
        pio_test_cmd,
        ["-d", str(project_dir), "-e", "native"],
    )
    validate_cliresult(result)
    assert all(f in result.output for f in ("setUp called", "tearDown called"))


def test_unity_custom_config(clirunner, validate_cliresult, tmp_path: Path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
"""
    )
    test_dir = project_dir / "test" / "native" / "test_component"
    test_dir.mkdir(parents=True)
    (test_dir.parent / "unity_config.h").write_text(
        """
#include <stdio.h>

#define CUSTOM_UNITY_CONFIG

#define UNITY_OUTPUT_CHAR(c)    putchar(c)
#define UNITY_OUTPUT_FLUSH()    fflush(stdout)
"""
    )
    (test_dir / "test_main.c").write_text(
        """
#include <stdio.h>
#include <unity.h>

void setUp(){
#ifdef CUSTOM_UNITY_CONFIG
    printf("Found custom unity_config.h\\n");
#endif
}
void tearDown(){
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
        pio_test_cmd,
        ["-d", str(project_dir), "-e", "native"],
    )
    validate_cliresult(result)
    assert all(f in result.output for f in ("Found custom unity_config", "dummy_test"))


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

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
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
        pio_test_cmd,
        [
            "-d",
            str(project_dir),
            "--without-testing",
            "--without-uploading",
        ],
    )
    validate_cliresult(result)

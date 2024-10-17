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
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from platformio import proc
from platformio.fs import load_json
from platformio.test.cli import cli as pio_test_cmd


def test_calculator_example(tmp_path: Path):
    junit_output_path = tmp_path / "junit.xml"
    project_dir = tmp_path / "project"
    shutil.copytree(
        os.path.join("examples", "unit-testing", "calculator"), str(project_dir)
    )
    result = proc.exec_command(
        [
            "platformio",
            "test",
            "-d",
            str(project_dir),
            "-e",
            "uno",
            "-e",
            "native",
            "--junit-output-path",
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


def test_list_tests(clirunner, validate_cliresult, tmp_path: Path):
    json_output_path = tmp_path / "report.json"
    project_dir = tmp_path / "project"
    shutil.copytree(
        os.path.join("examples", "unit-testing", "calculator"), str(project_dir)
    )
    result = clirunner.invoke(
        pio_test_cmd,
        [
            "-d",
            str(project_dir),
            "--list-tests",
            "--json-output-path",
            str(json_output_path),
        ],
    )
    validate_cliresult(result)
    # test JSON
    json_report = load_json(str(json_output_path))
    assert json_report["testcase_nums"] == 0
    assert json_report["failure_nums"] == 0
    assert json_report["skipped_nums"] == 0
    assert len(json_report["test_suites"]) == 6


def test_group_and_custom_runner(clirunner, validate_cliresult, tmp_path: Path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
test_framework = custom
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

    # test group
    test_group = test_dir / "group"
    test_group.mkdir(parents=True)
    (test_group / "test_custom_runner.py").write_text(
        """
import click

from platformio.test.runners.unity import UnityTestRunner

class CustomTestRunner(UnityTestRunner):
    def teardown(self):
        click.echo("CustomTestRunner::TearDown called")
"""
    )

    # test suite
    test_suite_dir = test_group / "test_nested"
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
        ["-d", str(project_dir), "-e", "native", "--verbose"],
    )
    validate_cliresult(result)
    assert "1 Tests 0 Failures 0 Ignored" in result.output
    assert "Called from my_extra_fun" in result.output
    assert "CustomTestRunner::TearDown called" in result.output
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


# @pytest.mark.skipif(
#     sys.platform != "darwin", reason="runs only on macOS (issue with SimAVR)"
# )
# def test_custom_testing_command(clirunner, validate_cliresult, tmp_path: Path):
#     project_dir = tmp_path / "project"
#     project_dir.mkdir()
#     (project_dir / "platformio.ini").write_text(
#         """
# [env:uno]
# platform = atmelavr
# framework = arduino
# board = uno

# platform_packages =
#     platformio/tool-simavr @ ^1
# test_speed = 9600
# test_testing_command =
#     ${platformio.packages_dir}/tool-simavr/bin/simavr
#     -m
#     atmega328p
#     -f
#     16000000L
#     ${platformio.build_dir}/${this.__env__}/firmware.elf
# """
#     )
#     test_dir = project_dir / "test" / "test_dummy"
#     test_dir.mkdir(parents=True)
#     (test_dir / "test_main.cpp").write_text(
#         """
# #include <Arduino.h>
# #include <unity.h>

# void setUp(void) {
#     // set stuff up here
# }

# void tearDown(void) {
#     // clean stuff up here
# }

# void dummy_test(void) {
#     TEST_ASSERT_EQUAL(1, 1);
# }

# void setup() {
#     UNITY_BEGIN();
#     RUN_TEST(dummy_test);
#     UNITY_END();
# }

# void loop() {
#     delay(1000);
# }
# """
#     )
#     result = clirunner.invoke(
#         pio_test_cmd,
#         ["-d", str(project_dir), "--without-uploading"],
#     )
#     validate_cliresult(result)
#     assert "dummy_test" in result.output


def test_unity_setup_teardown(clirunner, validate_cliresult, tmpdir):
    project_dir = tmpdir.mkdir("project")
    project_dir.join("platformio.ini").write(
        """
[env:native]
platform = native
"""
    )
    test_dir = project_dir.mkdir("test")
    test_dir.join("test_main.h").write(
        """
#include <stdio.h>
#include <unity.h>
    """
    )
    test_dir.join("test_main.c").write(
        """
#include "test_main.h"

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
        ["-d", str(project_dir), "-e", "native", "--verbose"],
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


@pytest.mark.skipif(
    sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS") == "true",
    reason="skip Github Actions on Windows (MinGW issue)",
)
def test_doctest_framework(clirunner, tmp_path: Path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(
        """
[env:native]
platform = native
test_framework = doctest
"""
    )
    test_dir = project_dir / "test" / "test_dummy"
    test_dir.mkdir(parents=True)
    (test_dir / "test_main.cpp").write_text(
        """
#define DOCTEST_CONFIG_IMPLEMENT
#include <doctest.h>

TEST_CASE("[math] basic stuff")
{
	CHECK(6 > 5);
	CHECK(6 > 7);
}

TEST_CASE("should be skipped " * doctest::skip())
{
	CHECK(2 > 5);
}

TEST_CASE("vectors can be sized and resized")
{
	std::vector<int> v(5);

	REQUIRE(v.size() == 5);
	REQUIRE(v.capacity() >= 5);

	SUBCASE("adding to the vector increases it's size")
	{
		v.push_back(1);

		CHECK(v.size() == 6);
		CHECK(v.capacity() >= 6);
	}
	SUBCASE("reserving increases just the capacity")
	{
		v.reserve(6);

		CHECK(v.size() == 5);
		CHECK(v.capacity() >= 6);
	}
}

TEST_CASE("WARN level of asserts don't fail the test case")
{
	WARN(0);
	WARN_FALSE(1);
	WARN_EQ(1, 0);
}

TEST_SUITE("scoped test suite")
{
	TEST_CASE("part of scoped")
	{
		FAIL("Error message");
	}

	TEST_CASE("part of scoped 2")
	{
		FAIL("");
	}
}

int main(int argc, char **argv)
{
	doctest::Context context;
	context.setOption("success", true);
	context.setOption("no-exitcode", true);
	context.applyCommandLine(argc, argv);
	return context.run();
}
"""
    )
    junit_output_path = tmp_path / "junit.xml"
    result = clirunner.invoke(
        pio_test_cmd,
        [
            "-d",
            str(project_dir),
            "--junit-output-path",
            str(junit_output_path),
        ],
    )
    assert result.exit_code != 0
    # test JUnit output
    junit_testsuites = ET.parse(junit_output_path).getroot()
    assert int(junit_testsuites.get("tests")) == 8
    assert int(junit_testsuites.get("errors")) == 0
    assert int(junit_testsuites.get("failures")) == 3
    assert len(junit_testsuites.findall("testsuite")) == 1
    junit_failed_testcase = junit_testsuites.find(
        ".//testcase[@name='scoped test suite/part of scoped']"
    )
    assert junit_failed_testcase.get("status") == "FAILED"
    assert junit_failed_testcase.find("failure").get("message") == "Error message"
    assert "TEST SUITE: scoped test suite" in junit_failed_testcase.find("failure").text

    # test program arguments
    json_output_path = tmp_path / "report.json"
    result = clirunner.invoke(
        pio_test_cmd,
        [
            "-d",
            str(project_dir),
            "--json-output-path",
            str(json_output_path),
            "-a",
            "-aa=1",  # fail after the 1 error
        ],
    )
    assert result.exit_code != 0
    assert "1 test cases" in result.output
    # test JSON
    json_report = load_json(str(json_output_path))
    assert json_report["testcase_nums"] == 1
    assert json_report["failure_nums"] == 1


@pytest.mark.skipif(
    sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS") == "true",
    reason="skip Github Actions on Windows (MinGW issue)",
)
def test_googletest_framework(clirunner, tmp_path: Path):
    project_dir = tmp_path / "project"
    shutil.copytree(
        os.path.join("examples", "unit-testing", "googletest"), str(project_dir)
    )
    junit_output_path = tmp_path / "junit.xml"
    result = clirunner.invoke(
        pio_test_cmd,
        [
            "-d",
            str(project_dir),
            "-e",
            "native",
            "--junit-output-path",
            str(junit_output_path),
        ],
    )
    assert result.exit_code != 0
    # test JUnit output
    junit_testsuites = ET.parse(junit_output_path).getroot()
    assert int(junit_testsuites.get("tests")) == 4
    assert int(junit_testsuites.get("errors")) == 0
    assert int(junit_testsuites.get("failures")) == 1
    assert len(junit_testsuites.findall("testsuite")) == 4
    junit_failed_testcase = junit_testsuites.find(".//testcase[@name='FooTest.Bar']")
    assert junit_failed_testcase.get("status") == "FAILED"
    assert "test_main.cpp" in junit_failed_testcase.get("file")
    assert junit_failed_testcase.get("line") == "26"
    assert junit_failed_testcase.find("failure").get("message") == "Failure"
    assert "Expected equality" in junit_failed_testcase.find("failure").text

    # test program arguments
    json_output_path = tmp_path / "report.json"
    result = clirunner.invoke(
        pio_test_cmd,
        [
            "-d",
            str(project_dir),
            "-e",
            "native",
            "--json-output-path",
            str(json_output_path),
            "-a",
            "--gtest_filter=-FooTest.Bar",
        ],
    )
    assert result.exit_code == 0
    # test JSON
    json_report = load_json(str(json_output_path))
    assert json_report["testcase_nums"] == 3
    assert json_report["failure_nums"] == 0
    assert json_report["skipped_nums"] == 1
    assert len(json_report["test_suites"]) == 4

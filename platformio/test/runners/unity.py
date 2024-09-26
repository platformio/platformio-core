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
import re
import string
from pathlib import Path

import click

from platformio.test.exception import UnitTestSuiteError
from platformio.test.result import TestCase, TestCaseSource, TestStatus
from platformio.test.runners.base import TestRunnerBase
from platformio.util import strip_ansi_codes


class UnityTestRunner(TestRunnerBase):
    EXTRA_LIB_DEPS = ["throwtheswitch/Unity@^2.6.0"]

    # Examples:
    # test/test_foo.cpp:44:test_function_foo:FAIL: Expected 32 Was 33
    # test/group/test_foo/test_main.cpp:5:test::dummy:FAIL: Expression Evaluated To FALSE
    TESTCASE_PARSE_RE = re.compile(
        r"(?P<source_file>[^:]+):(?P<source_line>\d+):(?P<name>[^\s]+):"
        r"(?P<status>PASS|IGNORE|FAIL)(:\s*(?P<message>.+)$)?"
    )

    UNITY_CONFIG_H = """
#ifndef UNITY_CONFIG_H
#define UNITY_CONFIG_H

#ifndef NULL
#ifndef __cplusplus
#define NULL (void*)0
#else
#define NULL 0
#endif
#endif

#ifdef __cplusplus
extern "C"
{
#endif

void unityOutputStart(unsigned long);
void unityOutputChar(unsigned int);
void unityOutputFlush(void);
void unityOutputComplete(void);

#define UNITY_OUTPUT_START()    unityOutputStart((unsigned long) $baudrate)
#define UNITY_OUTPUT_CHAR(c)    unityOutputChar(c)
#define UNITY_OUTPUT_FLUSH()    unityOutputFlush()
#define UNITY_OUTPUT_COMPLETE() unityOutputComplete()

#ifdef __cplusplus
}
#endif /* extern "C" */

#endif /* UNITY_CONFIG_H */

"""

    UNITY_CONFIG_C = """
#include <unity_config.h>

#if !defined(UNITY_WEAK_ATTRIBUTE) && !defined(UNITY_WEAK_PRAGMA)
#   if defined(__GNUC__) || defined(__ghs__) /* __GNUC__ includes clang */
#       if !(defined(__WIN32__) && defined(__clang__)) && !defined(__TMS470__)
#           define UNITY_WEAK_ATTRIBUTE __attribute__((weak))
#       endif
#   endif
#endif

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNITY_WEAK_ATTRIBUTE
    UNITY_WEAK_ATTRIBUTE void setUp(void) { }
    UNITY_WEAK_ATTRIBUTE void tearDown(void) { }
    UNITY_WEAK_ATTRIBUTE void suiteSetUp(void) { }
    UNITY_WEAK_ATTRIBUTE int suiteTearDown(int num_failures) { return num_failures; }
#elif defined(UNITY_WEAK_PRAGMA)
    #pragma weak setUp
    void setUp(void) { }
    #pragma weak tearDown
    void tearDown(void) { }
    #pragma weak suiteSetUp
    void suiteSetUp(void) { }
    #pragma weak suiteTearDown
    int suiteTearDown(int num_failures) { return num_failures; }
#endif

#ifdef __cplusplus
}
#endif /* extern "C" */

$framework_config_code
    """

    UNITY_FRAMEWORK_CONFIG = dict(
        native=dict(
            code="""
#include <stdio.h>
void unityOutputStart(unsigned long baudrate) { (void) baudrate; }
void unityOutputChar(unsigned int c) { putchar(c); }
void unityOutputFlush(void) { fflush(stdout); }
void unityOutputComplete(void) { }
        """,
            language="c",
        ),
        arduino=dict(
            code="""
#include <Arduino.h>
void unityOutputStart(unsigned long baudrate) { Serial.begin(baudrate); }
void unityOutputChar(unsigned int c) { Serial.write(c); }
void unityOutputFlush(void) { Serial.flush(); }
void unityOutputComplete(void) { Serial.end(); }
        """,
            language="cpp",
        ),
        mbed=dict(
            code="""
#include <mbed.h>
#if MBED_MAJOR_VERSION == 6
UnbufferedSerial pc(USBTX, USBRX);
#else
RawSerial pc(USBTX, USBRX);
#endif
void unityOutputStart(unsigned long baudrate) { pc.baud(baudrate); }
void unityOutputChar(unsigned int c) {
#if MBED_MAJOR_VERSION == 6
    pc.write(&c, 1);
#else
    pc.putc(c);
#endif
}
void unityOutputFlush(void) { }
void unityOutputComplete(void) { }
        """,
            language="cpp",
        ),
        espidf=dict(
            code="""
#include <stdio.h>
void unityOutputStart(unsigned long baudrate) { (void) baudrate; }
void unityOutputChar(unsigned int c) { putchar(c); }
void unityOutputFlush(void) { fflush(stdout); }
void unityOutputComplete(void) { }
        """,
            language="c",
        ),
        zephyr=dict(
            code="""
#include <sys/printk.h>
void unityOutputStart(unsigned long baudrate) { (void) baudrate; }
void unityOutputChar(unsigned int c) { printk("%c", c); }
void unityOutputFlush(void) { }
void unityOutputComplete(void) { }
        """,
            language="c",
        ),
        legacy_custom_transport=dict(
            code="""
#include <unittest_transport.h>
void unityOutputStart(unsigned long baudrate) { unittest_uart_begin(); }
void unityOutputChar(unsigned int c) { unittest_uart_putchar(c); }
void unityOutputFlush(void) { unittest_uart_flush(); }
void unityOutputComplete(void) { unittest_uart_end(); }
        """,
            language="cpp",
        ),
    )

    def get_unity_framework_config(self):
        if not self.platform.is_embedded():
            return self.UNITY_FRAMEWORK_CONFIG["native"]
        if (
            self.project_config.get(
                f"env:{self.test_suite.env_name}", "test_transport", None
            )
            == "custom"
        ):
            framework = "legacy_custom_transport"
        else:
            framework = (
                self.project_config.get(f"env:{self.test_suite.env_name}", "framework")
                or [None]
            )[0]
        if framework and framework in self.UNITY_FRAMEWORK_CONFIG:
            return self.UNITY_FRAMEWORK_CONFIG[framework]
        raise UnitTestSuiteError(
            f"Could not find Unity configuration for the `{framework}` framework.\n"
            "Learn how to create a custom Unity configuration at"
            "https://docs.platformio.org/en/latest/advanced/"
            "unit-testing/frameworks/unity.html"
        )

    def configure_build_env(self, env):
        env.Append(CPPDEFINES=["UNITY_INCLUDE_CONFIG_H"])
        if self.custom_unity_config_exists():
            return env
        env.Replace(
            UNITY_CONFIG_DIR=os.path.join("$BUILD_DIR", "unity_config"),
            BUILD_UNITY_CONFIG_DIR=os.path.join("$BUILD_DIR", "unity_config_build"),
        )
        env.Prepend(CPPPATH=["$UNITY_CONFIG_DIR"])
        self.generate_unity_extras(env.subst("$UNITY_CONFIG_DIR"))
        env.BuildSources("$BUILD_UNITY_CONFIG_DIR", "$UNITY_CONFIG_DIR")
        return env

    def custom_unity_config_exists(self):
        test_dir = self.project_config.get("platformio", "test_dir")
        config_fname = "unity_config.h"
        if os.path.isfile(os.path.join(test_dir, config_fname)):
            return True
        test_name = (
            self.test_suite.test_name if self.test_suite.test_name != "*" else None
        )
        while test_name:
            if os.path.isfile(os.path.join(test_dir, test_name, config_fname)):
                return True
            test_name = os.path.dirname(test_name)  # parent dir
        return False

    def generate_unity_extras(self, dst_dir):
        dst_dir = Path(dst_dir)
        if not dst_dir.is_dir():
            dst_dir.mkdir(parents=True)
        unity_h = dst_dir / "unity_config.h"
        if not unity_h.is_file():
            unity_h.write_text(
                string.Template(self.UNITY_CONFIG_H)
                .substitute(baudrate=self.get_test_speed())
                .strip()
                + "\n",
                encoding="utf8",
            )
        framework_config = self.get_unity_framework_config()
        unity_c = dst_dir / ("unity_config.%s" % framework_config.get("language", "c"))
        if not unity_c.is_file():
            unity_c.write_text(
                string.Template(self.UNITY_CONFIG_C)
                .substitute(framework_config_code=framework_config["code"])
                .strip()
                + "\n",
                encoding="utf8",
            )

    def on_testing_line_output(self, line):
        if self.options.verbose:
            click.echo(line, nl=False)
        line = strip_ansi_codes(line or "").strip()
        if not line:
            return

        test_case = self.parse_test_case(line)
        if test_case:
            self.test_suite.add_case(test_case)
            if not self.options.verbose:
                click.echo(test_case.humanize())

        if all(s in line for s in ("Tests", "Failures", "Ignored")):
            self.test_suite.on_finish()

    def parse_test_case(self, line):
        if not self.TESTCASE_PARSE_RE:
            raise NotImplementedError()
        line = line.strip()
        if not line:
            return None
        match = self.TESTCASE_PARSE_RE.search(line)
        if not match:
            return None
        data = match.groupdict()
        source = None
        if "source_file" in data:
            source = TestCaseSource(
                filename=data["source_file"], line=int(data.get("source_line"))
            )
        return TestCase(
            name=data.get("name").strip(),
            status=TestStatus.from_string(data.get("status")),
            message=(data.get("message") or "").strip() or None,
            stdout=line,
            source=source,
        )

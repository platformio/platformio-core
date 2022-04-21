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

from platformio.unittest.exception import UnitTestSuiteError
from platformio.unittest.runners.base import TestRunnerBase


class UnityTestRunner(TestRunnerBase):

    EXTRA_LIB_DEPS = ["throwtheswitch/Unity@^2.5.2"]

    # example
    # test/test_foo.cpp:44:test_function_foo:FAIL: Expected 32 Was 33
    TESTCASE_PARSE_RE = re.compile(
        r"(?P<source_file>[^:]+):(?P<source_line>\d+):(?P<name>[^:]+):"
        r"(?P<status>PASS|IGNORE|FAIL)(?:(?P<message>.+)$)?"
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

void unityOutputStart(unsigned int);
void unityOutputChar(unsigned int);
void unityOutputFlush();
void unityOutputComplete();

#define UNITY_OUTPUT_START()    unityOutputStart($baudrate)
#define UNITY_OUTPUT_CHAR(a)    unityOutputChar(a)
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
#   define UNITY_WEAK_ATTRIBUTE __attribute__((weak))
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
void unityOutputStart(unsigned int baudrate) { }
void unityOutputChar(unsigned int c) { putchar(c); }
void unityOutputFlush(void) { fflush(stdout); }
void unityOutputComplete(void) { }
        """,
            language="c",
        ),
        arduino=dict(
            code="""
#include <Arduino.h>
void unityOutputStart(unsigned int baudrate) { Serial.begin(baudrate); }
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
void unityOutputStart(unsigned int baudrate) { pc.baud(baudrate); }
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
void unityOutputStart(unsigned int baudrate) { }
void unityOutputChar(unsigned int c) { putchar(c); }
void unityOutputFlush(void) { fflush(stdout); }
void unityOutputComplete(void) { }
        """,
            language="c",
        ),
        zephyr=dict(
            code="""
#include <sys/printk.h>
void unityOutputStart(unsigned int baudrate) { }
void unityOutputChar(unsigned int c) { printk("%c", c); }
void unityOutputFlush(void) { }
void unityOutputComplete(void) { }
        """,
            language="c",
        ),
        legacy_custom_transport=dict(
            code="""
#include <unittest_transport.h>
void unityOutputStart(unsigned int baudrate) { unittest_uart_begin(); }
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
            self.project_config.get(f"env:{self.test_suite.env_name}", "test_transport")
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
            "https://docs.platformio.org/page/plus/unit-testing.html"
        )

    def configure_build_env(self, env):
        env.Append(CPPDEFINES=["UNITY_INCLUDE_CONFIG_H"])
        env.Replace(
            UNITY_CONFIG_DIR=os.path.join("$BUILD_DIR", "unity_config"),
            BUILD_UNITY_CONFIG_DIR=os.path.join("$BUILD_DIR", "unity_config_build"),
        )
        env.Append(CPPPATH=["$UNITY_CONFIG_DIR"])
        self.generate_unity_extras(env.subst("$UNITY_CONFIG_DIR"))
        env.BuildSources("$BUILD_UNITY_CONFIG_DIR", "$UNITY_CONFIG_DIR")

    def generate_unity_extras(self, dst_dir):
        dst_dir = Path(dst_dir)
        dst_dir.mkdir(parents=True, exist_ok=True)
        unity_h = dst_dir / "unity_config.h"
        if not unity_h.is_file():
            unity_h.write_text(
                string.Template(self.UNITY_CONFIG_H).substitute(
                    baudrate=self.get_test_speed()
                ),
                encoding="utf8",
            )
        framework_config = self.get_unity_framework_config()
        unity_c = dst_dir / ("unity_config.%s" % framework_config.get("language", "c"))
        if not unity_c.is_file():
            unity_c.write_text(
                string.Template(self.UNITY_CONFIG_C).substitute(
                    framework_config_code=framework_config["code"]
                ),
                encoding="utf8",
            )

    def on_run_output(self, data):
        if not data.strip():
            return click.echo(data, nl=False)

        if all(s in data for s in ("Tests", "Failures", "Ignored")):
            self.test_suite.on_finish()

        # beautify output
        for line in data.strip().split("\n"):
            line = line.strip()
            if line.endswith(":PASS"):
                click.echo("%s\t[%s]" % (line[:-5], click.style("PASSED", fg="green")))
            elif line.endswith(":IGNORE"):
                click.echo(
                    "%s\t[%s]" % (line[:-7], click.style("IGNORED", fg="yellow"))
                )
            elif ":FAIL" in line:
                click.echo("%s\t[%s]" % (line, click.style("FAILED", fg="red")))
            else:
                click.echo(line)

        return self.parse_testcases(data)

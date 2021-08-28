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

import atexit
from os import listdir, remove
from os.path import isdir, isfile, join
from string import Template

import click

from platformio import exception

TRANSPORT_OPTIONS = {
    "arduino": {
        "include": "#include <Arduino.h>",
        "object": "",
        "putchar": "Serial.write(c);",
        "flush": "Serial.flush();",
        "begin": "Serial.begin($baudrate);",
        "end": "Serial.end();",
        "language": "cpp",
    },
    "mbed": {
        "include": "#include <mbed.h>",
        "object": (
            "#if MBED_MAJOR_VERSION == 6\nUnbufferedSerial pc(USBTX, USBRX);\n"
            "#else\nRawSerial pc(USBTX, USBRX);\n#endif"
        ),
        "putchar": (
            "#if MBED_MAJOR_VERSION == 6\npc.write(&c, 1);\n"
            "#else\npc.putc(c);\n#endif"
        ),
        "flush": "",
        "begin": "pc.baud($baudrate);",
        "end": "",
        "language": "cpp",
    },
    "espidf": {
        "include": "#include <stdio.h>",
        "object": "",
        "putchar": "putchar(c);",
        "flush": "fflush(stdout);",
        "begin": "",
        "end": "",
    },
    "zephyr": {
        "include": "#include <sys/printk.h>",
        "object": "",
        "putchar": 'printk("%c", c);',
        "flush": "",
        "begin": "",
        "end": "",
    },
    "native": {
        "include": "#include <stdio.h>",
        "object": "",
        "putchar": "putchar(c);",
        "flush": "fflush(stdout);",
        "begin": "",
        "end": "",
    },
    "custom": {
        "include": '#include "unittest_transport.h"',
        "object": "",
        "putchar": "unittest_uart_putchar(c);",
        "flush": "unittest_uart_flush();",
        "begin": "unittest_uart_begin();",
        "end": "unittest_uart_end();",
        "language": "cpp",
    },
}

CTX_META_TEST_IS_RUNNING = __name__ + ".test_running"
CTX_META_TEST_RUNNING_NAME = __name__ + ".test_running_name"


class TestProcessorBase(object):

    DEFAULT_BAUDRATE = 115200

    def __init__(self, cmd_ctx, testname, envname, options):
        self.cmd_ctx = cmd_ctx
        self.cmd_ctx.meta[CTX_META_TEST_IS_RUNNING] = True
        self.test_name = testname
        self.options = options
        self.env_name = envname
        self.env_options = options["project_config"].items(env=envname, as_dict=True)
        self._run_failed = False
        self._output_file_generated = False

    def get_transport(self):
        transport = None
        if self.env_options.get("platform") == "native":
            transport = "native"
        elif "framework" in self.env_options:
            transport = self.env_options.get("framework")[0]
        if "test_transport" in self.env_options:
            transport = self.env_options["test_transport"]
        if transport not in TRANSPORT_OPTIONS:
            raise exception.PlatformioException(
                "Unknown Unit Test transport `%s`. Please check a documentation how "
                "to create an own 'Test Transport':\n"
                "- https://docs.platformio.org/page/plus/unit-testing.html" % transport
            )
        return transport.lower()

    def get_baudrate(self):
        return int(self.env_options.get("test_speed", self.DEFAULT_BAUDRATE))

    def print_progress(self, text):
        click.secho(text, bold=self.options.get("verbose"))

    def build_or_upload(self, target):
        if not self._output_file_generated:
            self.generate_output_file(
                self.options["project_config"].get_optional_dir("test")
            )
            self._output_file_generated = True

        if self.test_name != "*":
            self.cmd_ctx.meta[CTX_META_TEST_RUNNING_NAME] = self.test_name

        try:
            # pylint: disable=import-outside-toplevel
            from platformio.commands.run.command import cli as cmd_run

            return self.cmd_ctx.invoke(
                cmd_run,
                project_dir=self.options["project_dir"],
                project_conf=self.options["project_config"].path,
                upload_port=self.options.get("upload_port"),
                verbose=self.options["verbose"],
                silent=self.options.get("silent"),
                environment=[self.env_name],
                disable_auto_clean="nobuild" in target,
                target=target,
            )
        except exception.ReturnErrorCode:
            return False

    def process(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def on_run_out(self, line):
        line = line.strip()
        if line.endswith(":PASS"):
            click.echo("%s\t[%s]" % (line[:-5], click.style("PASSED", fg="green")))
        elif ":FAIL" in line:
            self._run_failed = True
            click.echo("%s\t[%s]" % (line, click.style("FAILED", fg="red")))
        else:
            click.echo(line)

    def generate_output_file(self, test_dir):
        assert isdir(test_dir)

        file_tpl = "\n".join(
            [
                "$include",
                "#include <output_export.h>",
                "",
                "$object",
                "",
                "#ifdef __GNUC__",
                "void output_start(unsigned int baudrate __attribute__((unused)))",
                "#else",
                "void output_start(unsigned int baudrate)",
                "#endif",
                "{",
                "    $begin",
                "}",
                "",
                "void output_char(int c)",
                "{",
                "    $putchar",
                "}",
                "",
                "void output_flush(void)",
                "{",
                "    $flush",
                "}",
                "",
                "void output_complete(void)",
                "{",
                "   $end",
                "}",
            ]
        )

        tmp_file_prefix = "tmp_pio_test_transport"

        def delete_tmptest_files(test_dir):
            for item in listdir(test_dir):
                if item.startswith(tmp_file_prefix) and isfile(join(test_dir, item)):
                    try:
                        remove(join(test_dir, item))
                    except:  # pylint: disable=bare-except
                        click.secho(
                            "Warning: Could not remove temporary file '%s'. "
                            "Please remove it manually." % join(test_dir, item),
                            fg="yellow",
                        )

        transport_options = TRANSPORT_OPTIONS[self.get_transport()]
        tpl = Template(file_tpl).substitute(transport_options)
        data = Template(tpl).substitute(baudrate=self.get_baudrate())

        delete_tmptest_files(test_dir)
        tmp_file = join(
            test_dir,
            "%s.%s" % (tmp_file_prefix, transport_options.get("language", "c")),
        )
        with open(tmp_file, mode="w", encoding="utf8") as fp:
            fp.write(data)

        atexit.register(delete_tmptest_files, test_dir)

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

import click

from platformio.test.result import TestCase, TestCaseSource, TestStatus
from platformio.test.runners.base import TestRunnerBase


class DoctestTestCaseParser:
    def __init__(self):
        self._tmp_tc = None
        self._name_tokens = []

    def parse(self, line):
        if self.is_divider(line):
            return self._on_divider()
        if not self._tmp_tc or line.strip().startswith("[doctest]"):
            return None

        self._tmp_tc.stdout += line
        line = line.strip()

        # source
        if not self._tmp_tc.source and line:
            self._tmp_tc.source = self.parse_source(line)
            return None

        # name
        if not self._tmp_tc.name:
            if line:
                self._name_tokens.append(line)
                return None
            self._tmp_tc.name = self.parse_name(self._name_tokens)
            return None

        if self._tmp_tc.status != TestStatus.FAILED:
            self._parse_assert(line)

        return None

    @staticmethod
    def is_divider(line):
        line = line.strip()
        return line.startswith("===") and line.endswith("===")

    def _on_divider(self):
        test_case = None
        if self._tmp_tc:
            test_case = TestCase(
                name=self._tmp_tc.name.strip(),
                status=self._tmp_tc.status,
                message=(self._tmp_tc.message or "").strip() or None,
                source=self._tmp_tc.source,
                stdout=self._tmp_tc.stdout.strip(),
            )

        self._tmp_tc = TestCase("", TestStatus.PASSED, stdout="")
        self._name_tokens = []
        return test_case

    @staticmethod
    def parse_source(line):
        if not line.endswith(":"):
            return None
        filename, line = line[:-1].rsplit(":", 1)
        return TestCaseSource(filename, int(line))

    @staticmethod
    def parse_name(tokens):
        cleaned_tokens = []
        for token in tokens:
            if token.startswith("TEST ") and ":" in token:
                token = token[token.index(":") + 1 :]
            cleaned_tokens.append(token.strip())
        return "/".join(cleaned_tokens)

    def _parse_assert(self, line):
        status_tokens = [
            (TestStatus.FAILED, "ERROR"),
            (TestStatus.FAILED, "FATAL ERROR"),
            (TestStatus.WARNED, "WARNING"),
        ]
        for status, token in status_tokens:
            index = line.find(": %s:" % token)
            if index == -1:
                continue
            self._tmp_tc.status = status
            self._tmp_tc.message = line[index + len(token) + 3 :].strip() or None


class DoctestTestRunner(TestRunnerBase):
    EXTRA_LIB_DEPS = ["doctest/doctest@^2.4.11"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tc_parser = DoctestTestCaseParser()

    def on_testing_line_output(self, line):
        if self.options.verbose:
            click.echo(line, nl=False)

        test_case = self._tc_parser.parse(line)
        if test_case:
            self.test_suite.add_case(test_case)
            if not self.options.verbose:
                click.echo(test_case.humanize())

        if "[doctest] Status:" in line:
            self.test_suite.on_finish()

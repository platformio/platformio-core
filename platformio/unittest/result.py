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

import enum
import functools
import operator
import time


class TestStatus(enum.Enum):
    PASSED = enum.auto()
    FAILED = enum.auto()
    SKIPPED = enum.auto()
    ERRORED = enum.auto()

    @classmethod
    def from_string(cls, value: str):
        value = value.lower()
        if value.startswith("pass"):
            return cls.PASSED
        if value.startswith(("ignore", "skip")):
            return cls.SKIPPED
        if value.startswith("fail"):
            return cls.FAILED
        raise ValueError(f"Unknown test status `{value}`")


class TestCaseSource:
    def __init__(self, file, line=None):
        self.file = file
        self.line = line


class TestCase:
    def __init__(  # pylint: disable=too-many-arguments
        self, name, status, message=None, stdout=None, source=None
    ):
        assert isinstance(status, TestStatus)
        self.name = name.strip()
        self.status = status
        self.message = message.strip() if message else None
        self.stdout = stdout.strip() if stdout else None
        self.source = source


class TestSuite:
    def __init__(self, env_name, test_name):
        self.env_name = env_name
        self.test_name = test_name
        self.duration = 0
        self._cases = []
        self._start_timestamp = 0
        self._finished = False
        self._error = None

    @property
    def cases(self):
        return self._cases

    def get_status_nums(self, status):
        return len([True for c in self._cases if c.status == status])

    @property
    def status(self):
        if self._error:
            return TestStatus.ERRORED
        if self.get_status_nums(TestStatus.FAILED):
            return TestStatus.FAILED
        if self._cases and any(c.status == TestStatus.PASSED for c in self._cases):
            return TestStatus.PASSED
        return TestStatus.SKIPPED

    def add_case(self, case: TestCase):
        assert isinstance(case, TestCase)
        self._cases.append(case)

    def is_finished(self):
        return self._finished

    def on_start(self):
        self._start_timestamp = time.time()

    def on_error(self, exc):
        self._error = exc

    def on_finish(self):
        if self.is_finished():
            return
        self._finished = True
        self.duration = time.time() - self._start_timestamp


class TestSummary:
    def __init__(self, name):
        self.name = name
        self._suites = []

    @property
    def suites(self):
        return self._suites

    def add_suite(self, suite):
        assert isinstance(suite, TestSuite)
        self._suites.append(suite)

    @property
    def duration(self):
        return functools.reduce(operator.add, [s.duration for s in self._suites])

    @property
    def case_nums(self):
        return functools.reduce(operator.add, [len(s.cases) for s in self._suites])

    @property
    def is_errored(self):
        return any(s.status == TestStatus.ERRORED for s in self._suites)

    def get_status_nums(self, status):
        return functools.reduce(
            operator.add, [s.get_status_nums(status) for s in self._suites]
        )

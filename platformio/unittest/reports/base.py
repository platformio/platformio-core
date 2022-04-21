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

import importlib

from platformio.unittest.result import TestSummary


class TestReportBase:
    def __init__(self, test_summary):
        self.test_summary = test_summary

    def generate(self):
        raise NotImplementedError()


class TestReportFactory:
    @staticmethod
    def new(  # pylint: disable=redefined-builtin
        format, test_summary
    ) -> TestReportBase:
        assert isinstance(test_summary, TestSummary)
        mod = importlib.import_module(f"platformio.unittest.reports.{format}")
        report_cls = getattr(mod, "%sTestReport" % format.lower().capitalize())
        return report_cls(test_summary)

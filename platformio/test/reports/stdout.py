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
from tabulate import tabulate

from platformio import util
from platformio.test.reports.base import TestReportBase
from platformio.test.result import TestStatus


class StdoutTestReport(TestReportBase):
    def generate(self, verbose=False):  # pylint: disable=arguments-differ
        click.echo()

        tabular_data = []
        failed_nums = self.test_result.get_status_nums(TestStatus.FAILED)
        skipped_nums = self.test_result.get_status_nums(TestStatus.SKIPPED)
        is_error = failed_nums > 0 or self.test_result.is_errored

        for test_suite in self.test_result.suites:
            if not verbose and test_suite.status == TestStatus.SKIPPED:
                continue
            status_str = test_suite.status.name
            if test_suite.status in (TestStatus.FAILED, TestStatus.ERRORED):
                status_str = click.style(status_str, fg="red")
            elif test_suite.status == TestStatus.PASSED:
                status_str = click.style(status_str, fg="green")

            tabular_data.append(
                (
                    click.style(test_suite.env_name, fg="cyan"),
                    test_suite.test_name,
                    status_str,
                    util.humanize_duration_time(test_suite.duration or None),
                )
            )

        if tabular_data:
            util.print_labeled_bar(
                "SUMMARY",
                is_error=is_error,
                fg="red" if is_error else "green",
            )
            click.echo(
                tabulate(
                    tabular_data,
                    headers=[
                        click.style(s, bold=True)
                        for s in ("Environment", "Test", "Status", "Duration")
                    ],
                ),
                err=is_error,
            )

        if failed_nums:
            self.print_failed_test_cases()

        util.print_labeled_bar(
            "%d test cases: %s%s%d succeeded in %s"
            % (
                self.test_result.case_nums,
                ("%d failed, " % failed_nums) if failed_nums else "",
                ("%d skipped, " % skipped_nums) if skipped_nums else "",
                self.test_result.get_status_nums(TestStatus.PASSED),
                util.humanize_duration_time(self.test_result.duration),
            ),
            is_error=is_error,
            fg="red" if is_error else "green",
        )

    def print_failed_test_cases(self):
        click.echo()
        for test_suite in self.test_result.suites:
            if test_suite.status != TestStatus.FAILED:
                continue
            util.print_labeled_bar(
                click.style(
                    f"{test_suite.env_name}:{test_suite.test_name}", bold=True, fg="red"
                ),
                is_error=True,
                sep="_",
            )
            for test_case in test_suite.cases:
                if test_case.status != TestStatus.FAILED:
                    continue
                click.echo((test_case.stdout or "").strip())
                click.echo()

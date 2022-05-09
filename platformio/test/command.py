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

import fnmatch
import os
import shutil

import click

from platformio import app, exception, fs, util
from platformio.project.config import ProjectConfig
from platformio.test.exception import TestDirNotExistsError
from platformio.test.reports.base import TestReportFactory
from platformio.test.result import TestResult, TestStatus, TestSuite
from platformio.test.runners.base import TestRunnerOptions
from platformio.test.runners.factory import TestRunnerFactory


@click.command("test", short_help="Unit Testing")
@click.option("--environment", "-e", multiple=True)
@click.option(
    "--filter",
    "-f",
    multiple=True,
    metavar="PATTERN",
    help="Filter tests by a pattern",
)
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    metavar="PATTERN",
    help="Ignore tests by a pattern",
)
@click.option("--upload-port")
@click.option("--test-port")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
@click.option("--without-building", is_flag=True)
@click.option("--without-uploading", is_flag=True)
@click.option("--without-testing", is_flag=True)
@click.option("--no-reset", is_flag=True)
@click.option(
    "--monitor-rts",
    default=None,
    type=click.IntRange(0, 1),
    help="Set initial RTS line state for Serial Monitor",
)
@click.option(
    "--monitor-dtr",
    default=None,
    type=click.IntRange(0, 1),
    help="Set initial DTR line state for Serial Monitor",
)
@click.option(
    "-a",
    "--program-arg",
    "program_args",
    multiple=True,
    help="A program argument (multiple are allowed)",
)
@click.option("--output-format", type=click.Choice(["json", "junit"]))
@click.option(
    "--output-path",
    default=os.getcwd,
    type=click.Path(dir_okay=True, resolve_path=True),
)
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def test_cmd(  # pylint: disable=too-many-arguments,too-many-locals,redefined-builtin
    ctx,
    environment,
    ignore,
    filter,
    upload_port,
    test_port,
    project_dir,
    project_conf,
    without_building,
    without_uploading,
    without_testing,
    no_reset,
    monitor_rts,
    monitor_dtr,
    program_args,
    output_format,
    output_path,
    verbose,
):
    app.set_session_var("custom_project_conf", project_conf)

    with fs.cd(project_dir):
        config = ProjectConfig.get_instance(project_conf)
        config.validate(envs=environment)
        test_names = get_test_names(config)

        if not verbose:
            click.echo("Verbose mode can be enabled via `-v, --verbose` option")
        click.secho("Collected %d tests" % len(test_names), bold=True, nl=not verbose)
        if verbose:
            click.echo(" (%s)" % ", ".join(test_names))

        test_result = TestResult(project_dir)
        default_envs = config.default_envs()
        for env_name in config.envs():
            for test_name in test_names:
                test_suite = TestSuite(env_name, test_name)
                test_result.add_suite(test_suite)

                # filter and ignore patterns
                patterns = dict(filter=list(filter), ignore=list(ignore))
                for key in patterns:
                    if patterns[key]:  # overriden from CLI
                        continue
                    patterns[key].extend(
                        config.get(f"env:{env_name}", f"test_{key}", [])
                    )

                skip_conditions = [
                    environment and env_name not in environment,
                    not environment and default_envs and env_name not in default_envs,
                    test_name != "*"
                    and patterns["filter"]
                    and not any(
                        fnmatch.fnmatch(test_name, p) for p in patterns["filter"]
                    ),
                    test_name != "*"
                    and any(fnmatch.fnmatch(test_name, p) for p in patterns["ignore"]),
                ]
                if any(skip_conditions):
                    continue

                runner = TestRunnerFactory.new(
                    test_suite,
                    config,
                    TestRunnerOptions(
                        verbose=verbose,
                        without_building=without_building,
                        without_uploading=without_uploading,
                        without_testing=without_testing,
                        upload_port=upload_port,
                        test_port=test_port,
                        no_reset=no_reset,
                        monitor_rts=monitor_rts,
                        monitor_dtr=monitor_dtr,
                        program_args=program_args,
                    ),
                )
                click.echo()
                print_suite_header(test_suite)
                runner.start(ctx)
                print_suite_footer(test_suite)

    # Reset custom project config
    app.set_session_var("custom_project_conf", None)

    stdout_report = TestReportFactory.new("stdout", test_result)
    stdout_report.generate(verbose=verbose)

    if output_format:
        custom_report = TestReportFactory.new(output_format, test_result)
        custom_report.generate(output_path=output_path, verbose=True)

    if test_result.is_errored or test_result.get_status_nums(TestStatus.FAILED):
        raise exception.ReturnErrorCode(1)


def get_test_names(config):
    test_dir = config.get("platformio", "test_dir")
    if not os.path.isdir(test_dir):
        raise TestDirNotExistsError(test_dir)
    names = []
    for root, _, __ in os.walk(test_dir):
        if not os.path.basename(root).startswith("test_"):
            continue
        names.append(os.path.relpath(root, test_dir))
    if not names:
        names = ["*"]
    return names


def print_suite_header(test_suite):
    click.echo(
        "Processing %s in %s environment"
        % (
            click.style(test_suite.test_name, fg="yellow", bold=True),
            click.style(test_suite.env_name, fg="cyan", bold=True),
        )
    )
    terminal_width, _ = shutil.get_terminal_size()
    click.secho("-" * terminal_width, bold=True)


def print_suite_footer(test_suite):
    is_error = test_suite.status in (TestStatus.FAILED, TestStatus.ERRORED)
    util.print_labeled_bar(
        "%s [%s] Took %.2f seconds"
        % (
            click.style(
                "%s:%s" % (test_suite.env_name, test_suite.test_name), bold=True
            ),
            (
                click.style(test_suite.status.name, fg="red", bold=True)
                if is_error
                else click.style("PASSED", fg="green", bold=True)
            ),
            test_suite.duration,
        ),
        is_error=is_error,
        sep="-",
    )

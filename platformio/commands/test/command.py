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

# pylint: disable=too-many-arguments, too-many-locals, too-many-branches

from fnmatch import fnmatch
from os import getcwd, listdir
from os.path import isdir, join
from time import time

import click
from tabulate import tabulate

from platformio import app, exception, fs, util
from platformio.commands.test.embedded import EmbeddedTestProcessor
from platformio.commands.test.native import NativeTestProcessor
from platformio.project.config import ProjectConfig


@click.command("test", short_help="Unit Testing")
@click.option("--environment", "-e", multiple=True, metavar="<environment>")
@click.option(
    "--filter",
    "-f",
    multiple=True,
    metavar="<pattern>",
    help="Filter tests by a pattern",
)
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    metavar="<pattern>",
    help="Ignore tests by a pattern",
)
@click.option("--upload-port")
@click.option("--test-port")
@click.option(
    "-d",
    "--project-dir",
    default=getcwd,
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
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(  # pylint: disable=redefined-builtin
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
    verbose,
):
    app.set_session_var("custom_project_conf", project_conf)

    with fs.cd(project_dir):
        config = ProjectConfig.get_instance(project_conf)
        config.validate(envs=environment)

        test_dir = config.get_optional_dir("test")
        if not isdir(test_dir):
            raise exception.TestDirNotExists(test_dir)
        test_names = get_test_names(test_dir)

        if not verbose:
            click.echo("Verbose mode can be enabled via `-v, --verbose` option")
        click.secho("Collected %d items" % len(test_names), bold=True)

        results = []
        default_envs = config.default_envs()
        for testname in test_names:

            for envname in config.envs():
                section = "env:%s" % envname

                # filter and ignore patterns
                patterns = dict(filter=list(filter), ignore=list(ignore))
                for key in patterns:
                    patterns[key].extend(config.get(section, "test_%s" % key, []))

                skip_conditions = [
                    environment and envname not in environment,
                    not environment and default_envs and envname not in default_envs,
                    testname != "*"
                    and patterns["filter"]
                    and not any([fnmatch(testname, p) for p in patterns["filter"]]),
                    testname != "*"
                    and any([fnmatch(testname, p) for p in patterns["ignore"]]),
                ]
                if any(skip_conditions):
                    results.append({"env": envname, "test": testname})
                    continue

                click.echo()
                print_processing_header(testname, envname)

                cls = (
                    NativeTestProcessor
                    if config.get(section, "platform") == "native"
                    else EmbeddedTestProcessor
                )
                tp = cls(
                    ctx,
                    testname,
                    envname,
                    dict(
                        project_config=config,
                        project_dir=project_dir,
                        upload_port=upload_port,
                        test_port=test_port,
                        without_building=without_building,
                        without_uploading=without_uploading,
                        without_testing=without_testing,
                        no_reset=no_reset,
                        monitor_rts=monitor_rts,
                        monitor_dtr=monitor_dtr,
                        verbose=verbose,
                        silent=not verbose,
                    ),
                )
                result = {
                    "env": envname,
                    "test": testname,
                    "duration": time(),
                    "succeeded": tp.process(),
                }
                result["duration"] = time() - result["duration"]
                results.append(result)

                print_processing_footer(result)

    if without_testing:
        return

    print_testing_summary(results)

    command_failed = any(r.get("succeeded") is False for r in results)
    if command_failed:
        raise exception.ReturnErrorCode(1)


def get_test_names(test_dir):
    names = []
    for item in sorted(listdir(test_dir)):
        if isdir(join(test_dir, item)):
            names.append(item)
    if not names:
        names = ["*"]
    return names


def print_processing_header(test, env):
    click.echo(
        "Processing %s in %s environment"
        % (
            click.style(test, fg="yellow", bold=True),
            click.style(env, fg="cyan", bold=True),
        )
    )
    terminal_width, _ = click.get_terminal_size()
    click.secho("-" * terminal_width, bold=True)


def print_processing_footer(result):
    is_failed = not result.get("succeeded")
    util.print_labeled_bar(
        "[%s] Took %.2f seconds"
        % (
            (
                click.style("FAILED", fg="red", bold=True)
                if is_failed
                else click.style("PASSED", fg="green", bold=True)
            ),
            result["duration"],
        ),
        is_error=is_failed,
    )


def print_testing_summary(results):
    click.echo()

    tabular_data = []
    succeeded_nums = 0
    failed_nums = 0
    duration = 0

    for result in results:
        duration += result.get("duration", 0)
        if result.get("succeeded") is False:
            failed_nums += 1
            status_str = click.style("FAILED", fg="red")
        elif result.get("succeeded") is None:
            status_str = "IGNORED"
        else:
            succeeded_nums += 1
            status_str = click.style("PASSED", fg="green")

        tabular_data.append(
            (
                result["test"],
                click.style(result["env"], fg="cyan"),
                status_str,
                util.humanize_duration_time(result.get("duration")),
            )
        )

    click.echo(
        tabulate(
            tabular_data,
            headers=[
                click.style(s, bold=True)
                for s in ("Test", "Environment", "Status", "Duration")
            ],
        ),
        err=failed_nums,
    )

    util.print_labeled_bar(
        "%s%d succeeded in %s"
        % (
            "%d failed, " % failed_nums if failed_nums else "",
            succeeded_nums,
            util.humanize_duration_time(duration),
        ),
        is_error=failed_nums,
        fg="red" if failed_nums else "green",
    )

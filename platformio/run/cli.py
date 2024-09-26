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

import operator
import os
import shutil
from multiprocessing import cpu_count
from time import time

import click
from tabulate import tabulate

from platformio import app, exception, fs, util
from platformio.device.monitor.command import device_monitor_cmd
from platformio.project.config import ProjectConfig
from platformio.project.exception import ProjectError
from platformio.project.helpers import find_project_dir_above, load_build_metadata
from platformio.run.helpers import clean_build_dir
from platformio.run.processor import EnvironmentProcessor
from platformio.test.runners.base import CTX_META_TEST_IS_RUNNING

# pylint: disable=too-many-arguments,too-many-locals,too-many-branches

try:
    DEFAULT_JOB_NUMS = cpu_count()
except NotImplementedError:
    DEFAULT_JOB_NUMS = 1


@click.command("run", short_help="Run project targets (build, upload, clean, etc.)")
@click.option("-e", "--environment", multiple=True)
@click.option("-t", "--target", multiple=True)
@click.option("--upload-port")
@click.option("--monitor-port")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, writable=True),
)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=DEFAULT_JOB_NUMS,
    help=(
        "Allow N jobs at once. "
        "Default is a number of CPUs in a system (N=%d)" % DEFAULT_JOB_NUMS
    ),
)
@click.option(
    "-a",
    "--program-arg",
    "program_args",
    multiple=True,
    help="A program argument (multiple are allowed)",
)
@click.option("--disable-auto-clean", is_flag=True)
@click.option("--list-targets", is_flag=True)
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(  # pylint: disable=too-many-positional-arguments
    ctx,
    environment,
    target,
    upload_port,
    monitor_port,
    project_dir,
    project_conf,
    jobs,
    program_args,
    disable_auto_clean,
    list_targets,
    silent,
    verbose,
):
    app.set_session_var("custom_project_conf", project_conf)

    # find project directory on upper level
    if os.path.isfile(project_dir):
        project_dir = find_project_dir_above(project_dir)

    targets = list(target) if target else []
    del target
    only_monitor = targets == ["monitor"]
    is_test_running = CTX_META_TEST_IS_RUNNING in ctx.meta
    command_failed = False

    with fs.cd(project_dir):
        config = ProjectConfig.get_instance(project_conf)
        config.validate(environment)

        if list_targets:
            return print_target_list(list(environment) or config.envs())

        # clean obsolete build dir
        if not only_monitor and not disable_auto_clean:
            build_dir = config.get("platformio", "build_dir")
            try:
                clean_build_dir(build_dir, config)
            except ProjectError as exc:
                raise exc
            except:  # pylint: disable=bare-except
                click.secho(
                    "Can not remove temporary directory `%s`. Please remove "
                    "it manually to avoid build issues" % build_dir,
                    fg="yellow",
                )

        default_envs = config.default_envs()
        results = []
        for env in config.envs():
            skipenv = any(
                [
                    environment and env not in environment,
                    not environment and default_envs and env not in default_envs,
                ]
            )
            if skipenv:
                results.append({"env": env})
                continue

            # print empty line between multi environment project
            if not silent and any(r.get("succeeded") is not None for r in results):
                click.echo()

            results.append(
                process_env(
                    ctx,
                    env,
                    config,
                    targets,
                    upload_port,
                    monitor_port,
                    jobs,
                    program_args,
                    is_test_running,
                    silent,
                    verbose,
                )
            )
        command_failed = any(r.get("succeeded") is False for r in results)
        if (
            not is_test_running
            and not only_monitor
            and (command_failed or not silent)
            and len(results) > 1
        ):
            print_processing_summary(results, verbose)

    # Reset custom project config
    app.set_session_var("custom_project_conf", None)

    if command_failed:
        raise exception.ReturnErrorCode(1)

    return True


def process_env(  # pylint: disable=too-many-positional-arguments
    ctx,
    name,
    config,
    targets,
    upload_port,
    monitor_port,
    jobs,
    program_args,
    is_test_running,
    silent,
    verbose,
):
    if not is_test_running and not silent:
        print_processing_header(name, config, verbose)

    targets = targets or config.get(f"env:{name}", "targets", [])
    only_monitor = targets == ["monitor"]
    result = {"env": name, "duration": time(), "succeeded": True}

    if not only_monitor:
        result["succeeded"] = EnvironmentProcessor(
            ctx,
            name,
            config,
            [t for t in targets if t != "monitor"],
            upload_port,
            jobs,
            program_args,
            silent,
            verbose,
        ).process()

    if result["succeeded"] and "monitor" in targets and "nobuild" not in targets:
        ctx.invoke(
            device_monitor_cmd,
            port=monitor_port,
            environment=name,
        )

    result["duration"] = time() - result["duration"]

    # print footer on error or when is not unit testing
    if (
        not is_test_running
        and not only_monitor
        and (not silent or not result["succeeded"])
    ):
        print_processing_footer(result)

    return result


def print_processing_header(env, config, verbose=False):
    env_dump = []
    for k, v in config.items(env=env):
        if verbose or k in ("platform", "framework", "board"):
            env_dump.append("%s: %s" % (k, ", ".join(v) if isinstance(v, list) else v))
    click.echo(
        "Processing %s (%s)"
        % (click.style(env, fg="cyan", bold=True), "; ".join(env_dump))
    )
    terminal_width = shutil.get_terminal_size().columns
    click.secho("-" * terminal_width, bold=True)


def print_processing_footer(result):
    is_failed = not result.get("succeeded")
    util.print_labeled_bar(
        "[%s] Took %.2f seconds"
        % (
            (
                click.style("FAILED", fg="red", bold=True)
                if is_failed
                else click.style("SUCCESS", fg="green", bold=True)
            ),
            result["duration"],
        ),
        is_error=is_failed,
    )


def print_processing_summary(results, verbose=False):
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
            if not verbose:
                continue
            status_str = "IGNORED"
        else:
            succeeded_nums += 1
            status_str = click.style("SUCCESS", fg="green")

        tabular_data.append(
            (
                click.style(result["env"], fg="cyan"),
                status_str,
                util.humanize_duration_time(result.get("duration")),
            )
        )

    click.echo()
    click.echo(
        tabulate(
            tabular_data,
            headers=[
                click.style(s, bold=True) for s in ("Environment", "Status", "Duration")
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


def print_target_list(envs):
    tabular_data = []
    for env, data in load_build_metadata(os.getcwd(), envs).items():
        tabular_data.extend(
            sorted(
                [
                    (
                        click.style(env, fg="cyan"),
                        t["group"],
                        click.style(t.get("name"), fg="yellow"),
                        t["title"],
                        t.get("description"),
                    )
                    for t in data.get("targets", [])
                ],
                key=operator.itemgetter(1, 2),
            )
        )
        tabular_data.append((None, None, None, None, None))
    click.echo(
        tabulate(
            tabular_data,
            headers=[
                click.style(s, bold=True)
                for s in ("Environment", "Group", "Name", "Title", "Description")
            ],
        ),
    )

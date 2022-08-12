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

# pylint: disable=too-many-arguments,too-many-locals,too-many-branches
# pylint: disable=redefined-builtin,too-many-statements

import json
import os
import shutil
from collections import Counter
from os.path import dirname, isfile
from time import time

import click
from tabulate import tabulate

from platformio import app, exception, fs, util
from platformio.check.defect import DefectItem
from platformio.check.tools import CheckToolFactory
from platformio.project.config import ProjectConfig
from platformio.project.helpers import find_project_dir_above, get_project_dir


@click.command("check", short_help="Static Code Analysis")
@click.option("-e", "--environment", multiple=True)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
@click.option("--pattern", multiple=True)
@click.option("--flags", multiple=True)
@click.option(
    "--severity", multiple=True, type=click.Choice(DefectItem.SEVERITY_LABELS.values())
)
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("--json-output", is_flag=True)
@click.option(
    "--fail-on-defect",
    multiple=True,
    type=click.Choice(DefectItem.SEVERITY_LABELS.values()),
)
@click.option("--skip-packages", is_flag=True)
def cli(
    environment,
    project_dir,
    project_conf,
    pattern,
    flags,
    severity,
    silent,
    verbose,
    json_output,
    fail_on_defect,
    skip_packages,
):
    app.set_session_var("custom_project_conf", project_conf)

    # find project directory on upper level
    if isfile(project_dir):
        project_dir = find_project_dir_above(project_dir)

    results = []
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance(project_conf)
        config.validate(environment)

        default_envs = config.default_envs()
        for envname in config.envs():
            skipenv = any(
                [
                    environment and envname not in environment,
                    not environment and default_envs and envname not in default_envs,
                ]
            )

            env_options = config.items(env=envname, as_dict=True)
            env_dump = []
            for k, v in env_options.items():
                if k not in ("platform", "framework", "board"):
                    continue
                env_dump.append(
                    "%s: %s" % (k, ", ".join(v) if isinstance(v, list) else v)
                )

            default_patterns = [
                config.get("platformio", "src_dir"),
                config.get("platformio", "include_dir"),
            ]
            tool_options = dict(
                verbose=verbose,
                silent=silent,
                patterns=pattern or env_options.get("check_patterns", default_patterns),
                flags=flags or env_options.get("check_flags"),
                severity=[DefectItem.SEVERITY_LABELS[DefectItem.SEVERITY_HIGH]]
                if silent
                else severity or config.get("env:" + envname, "check_severity"),
                skip_packages=skip_packages or env_options.get("check_skip_packages"),
                platform_packages=env_options.get("platform_packages"),
            )

            for tool in config.get("env:" + envname, "check_tool"):
                if skipenv:
                    results.append({"env": envname, "tool": tool})
                    continue
                if not silent and not json_output:
                    print_processing_header(tool, envname, env_dump)

                ct = CheckToolFactory.new(
                    tool, project_dir, config, envname, tool_options
                )

                result = {"env": envname, "tool": tool, "duration": time()}
                rc = ct.check(
                    on_defect_callback=None
                    if (json_output or verbose)
                    else lambda defect: click.echo(repr(defect))
                )

                result["defects"] = ct.get_defects()
                result["duration"] = time() - result["duration"]

                result["succeeded"] = rc == 0
                if fail_on_defect:
                    result["succeeded"] = rc == 0 and not any(
                        DefectItem.SEVERITY_LABELS[d.severity] in fail_on_defect
                        for d in result["defects"]
                    )
                result["stats"] = collect_component_stats(result)
                results.append(result)

                if verbose:
                    click.echo("\n".join(repr(d) for d in result["defects"]))

                if not json_output and not silent:
                    if rc != 0:
                        click.echo(
                            "Error: %s failed to perform check! Please "
                            "examine tool output in verbose mode." % tool
                        )
                    elif not result["defects"]:
                        click.echo("No defects found")
                    print_processing_footer(result)

        if json_output:
            click.echo(json.dumps(results_to_json(results)))
        elif not silent:
            print_check_summary(results, verbose=verbose)

    # Reset custom project config
    app.set_session_var("custom_project_conf", None)

    command_failed = any(r.get("succeeded") is False for r in results)
    if command_failed:
        raise exception.ReturnErrorCode(1)


def results_to_json(raw):
    results = []
    for item in raw:
        if item.get("succeeded") is None:
            continue
        item.update(
            {
                "succeeded": bool(item.get("succeeded")),
                "defects": [d.as_dict() for d in item.get("defects", [])],
            }
        )
        results.append(item)

    return results


def print_processing_header(tool, envname, envdump):
    click.echo(
        "Checking %s > %s (%s)"
        % (click.style(envname, fg="cyan", bold=True), tool, "; ".join(envdump))
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
                else click.style("PASSED", fg="green", bold=True)
            ),
            result["duration"],
        ),
        is_error=is_failed,
    )


def collect_component_stats(result):
    components = {}

    def _append_defect(component, defect):
        if not components.get(component):
            components[component] = Counter()
        components[component].update({DefectItem.SEVERITY_LABELS[defect.severity]: 1})

    for defect in result.get("defects", []):
        component = dirname(defect.file) or defect.file
        _append_defect(component, defect)

        if component.lower().startswith(get_project_dir().lower()):
            while os.sep in component:
                component = dirname(component)
                _append_defect(component, defect)

    return components


def print_defects_stats(results):
    if not results:
        return

    component_stats = {}
    for r in results:
        for k, v in r.get("stats", {}).items():
            if not component_stats.get(k):
                component_stats[k] = Counter()
            component_stats[k].update(r["stats"][k])

    if not component_stats:
        return

    severity_labels = list(DefectItem.SEVERITY_LABELS.values())
    severity_labels.reverse()
    tabular_data = []
    for k, v in component_stats.items():
        tool_defect = [v.get(s, 0) for s in severity_labels]
        tabular_data.append([k] + tool_defect)

    total = ["Total"] + [sum(d) for d in list(zip(*tabular_data))[1:]]
    tabular_data.sort()
    tabular_data.append([])  # Empty line as delimiter
    tabular_data.append(total)

    headers = ["Component"]
    headers.extend([l.upper() for l in severity_labels])
    headers = [click.style(h, bold=True) for h in headers]
    click.echo(tabulate(tabular_data, headers=headers, numalign="center"))
    click.echo()


def print_check_summary(results, verbose=False):
    click.echo()

    tabular_data = []
    succeeded_nums = 0
    failed_nums = 0
    duration = 0

    print_defects_stats(results)

    for result in results:
        duration += result.get("duration", 0)
        if result.get("succeeded") is False:
            failed_nums += 1
            status_str = click.style("FAILED", fg="red")
        elif result.get("succeeded") is None:
            status_str = "IGNORED"
            if not verbose:
                continue
        else:
            succeeded_nums += 1
            status_str = click.style("PASSED", fg="green")

        tabular_data.append(
            (
                click.style(result["env"], fg="cyan"),
                result["tool"],
                status_str,
                util.humanize_duration_time(result.get("duration")),
            )
        )

    click.echo(
        tabulate(
            tabular_data,
            headers=[
                click.style(s, bold=True)
                for s in ("Environment", "Tool", "Status", "Duration")
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

# Copyright (c) 2019-present PlatformIO <contact@platformio.org>
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

# pylint: disable=too-many-locals,too-many-branches

from os import getcwd
from os.path import isfile, join
from time import time

import click

from platformio import exception, fs
from platformio.commands.check.tools import CheckToolFactory
from platformio.commands.run.helpers import print_header
from platformio.project.config import ProjectConfig
from platformio.project.helpers import find_project_dir_above


@click.command("check", short_help="Run a static analysis tool on code")
@click.option("-e", "--environment", multiple=True)
@click.option("-d",
              "--project-dir",
              default=getcwd,
              type=click.Path(exists=True,
                              file_okay=True,
                              dir_okay=True,
                              writable=True,
                              resolve_path=True))
@click.option("-c",
              "--project-conf",
              type=click.Path(exists=True,
                              file_okay=True,
                              dir_okay=False,
                              readable=True,
                              resolve_path=True))
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
def cli(environment, project_dir, project_conf, silent, verbose):
    # find project directory on upper level
    if isfile(project_dir):
        project_dir = find_project_dir_above(project_dir)

    results = []
    start_time = time()
    terminal_width, _ = click.get_terminal_size()

    with fs.cd(project_dir):
        config = ProjectConfig.get_instance(
            project_conf or join(project_dir, "platformio.ini"))
        config.validate(environment)

        default_envs = config.default_envs()
        for envname in config.envs():
            skipenv = any([
                environment and envname not in environment, not environment
                and default_envs and envname not in default_envs
            ])
            if skipenv:
                results.append((None, envname, "*"))
                continue
            if not silent and any(r[0] is not None for r in results):
                click.echo()
            env_options = config.items(env=envname, as_dict=True)
            env_dump = []
            for k, v in env_options.items():
                if k not in ("platform", "framework", "board"):
                    continue
                env_dump.append(
                    "%s: %s" % (k, ", ".join(v) if isinstance(v, list) else v))

            for tool in env_options.get("check_tool", ["cppcheck"]):
                _start_time = time()
                if not silent:
                    click.echo("Checking %s > %s (%s)" %
                               (click.style(envname, fg="cyan", bold=True),
                                tool, "; ".join(env_dump)))
                    click.secho("-" * terminal_width, bold=True)

                return_code = CheckToolFactory.new(tool, project_dir, config,
                                                   envname, verbose,
                                                   silent).check()
                is_error = return_code != 0
                results.append((not is_error, envname, tool))

                print_header(
                    "[%s] Took %.2f seconds" %
                    ((click.style("FAILED", fg="red", bold=True) if is_error
                      else click.style("SUCCESS", fg="green", bold=True)),
                     time() - _start_time),
                    is_error=is_error)

    passed_nums = 0
    failed_nums = 0
    envname_max_len = max([len(click.style(r[1], fg="cyan")) for r in results])
    tool_max_len = max([len(r[2]) for r in results])

    click.echo()
    print_header("[%s]" % click.style("SUMMARY"))

    for result in results:
        status, envname, tool = result
        if status is False:
            failed_nums += 1
            status_str = click.style("FAILED", fg="red")
        elif status is None:
            status_str = click.style("IGNORED", fg="yellow")
        else:
            passed_nums += 1
            status_str = click.style("PASSED", fg="green")

        format_str = "Environment {:<%d} > {:<%d}\t[{}]" % (envname_max_len,
                                                            tool_max_len)
        click.echo(format_str.format(click.style(envname, fg="cyan"), tool,
                                     status_str),
                   err=status is False)

    print_header("%s%d passed in %.2f seconds" %
                 ("%d failed, " % failed_nums if failed_nums else "",
                  passed_nums, time() - start_time),
                 is_error=failed_nums,
                 fg="red" if failed_nums else "green")

    if failed_nums:
        raise exception.ReturnErrorCode(1)

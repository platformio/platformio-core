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

from multiprocessing import cpu_count
from os import getcwd
from os.path import isfile, join
from time import time

import click

from platformio import exception, util
from platformio.commands.device import device_monitor as cmd_device_monitor
from platformio.commands.run.helpers import (clean_build_dir,
                                             handle_legacy_libdeps,
                                             print_summary)
from platformio.commands.run.processor import EnvironmentProcessor
from platformio.project.config import ProjectConfig
from platformio.project.helpers import (find_project_dir_above,
                                        get_project_build_dir)

# pylint: disable=too-many-arguments,too-many-locals,too-many-branches

try:
    DEFAULT_JOB_NUMS = cpu_count()
except NotImplementedError:
    DEFAULT_JOB_NUMS = 1


@click.command("run", short_help="Process project environments")
@click.option("-e", "--environment", multiple=True)
@click.option("-t", "--target", multiple=True)
@click.option("--upload-port")
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
@click.option("-j",
              "--jobs",
              type=int,
              default=DEFAULT_JOB_NUMS,
              help=("Allow N jobs at once. "
                    "Default is a number of CPUs in a system (N=%d)" %
                    DEFAULT_JOB_NUMS))
@click.option("-s", "--silent", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("--disable-auto-clean", is_flag=True)
@click.pass_context
def cli(ctx, environment, target, upload_port, project_dir, project_conf, jobs,
        silent, verbose, disable_auto_clean):
    # find project directory on upper level
    if isfile(project_dir):
        project_dir = find_project_dir_above(project_dir)

    with util.cd(project_dir):
        # clean obsolete build dir
        if not disable_auto_clean:
            try:
                clean_build_dir(get_project_build_dir())
            except:  # pylint: disable=bare-except
                click.secho(
                    "Can not remove temporary directory `%s`. Please remove "
                    "it manually to avoid build issues" %
                    get_project_build_dir(force=True),
                    fg="yellow")

        config = ProjectConfig.get_instance(
            project_conf or join(project_dir, "platformio.ini"))
        config.validate(environment)

        handle_legacy_libdeps(project_dir, config)

        results = []
        start_time = time()
        default_envs = config.default_envs()
        for envname in config.envs():
            skipenv = any([
                environment and envname not in environment, not environment
                and default_envs and envname not in default_envs
            ])
            if skipenv:
                results.append((envname, None))
                continue

            if not silent and any(status is not None
                                  for (_, status) in results):
                click.echo()

            ep = EnvironmentProcessor(ctx, envname, config, target,
                                      upload_port, silent, verbose, jobs)
            result = (envname, ep.process())
            results.append(result)

            if result[1] and "monitor" in ep.get_build_targets() and \
                    "nobuild" not in ep.get_build_targets():
                ctx.invoke(cmd_device_monitor,
                           environment=environment[0] if environment else None)

        found_error = any(status is False for (_, status) in results)

        if (found_error or not silent) and len(results) > 1:
            click.echo()
            print_summary(results, start_time)

        if found_error:
            raise exception.ReturnErrorCode(1)
        return True

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

import os

import click
from tabulate import tabulate

from platformio import fs
from platformio.project.config import ProjectConfig
from platformio.project.exception import NotPlatformIOProjectError
from platformio.project.helpers import is_platformio_project


@click.command("config", short_help="Show computed configuration")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option("--json-output", is_flag=True)
def project_config_cmd(project_dir, json_output):
    if not is_platformio_project(project_dir):
        raise NotPlatformIOProjectError(project_dir)
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
    if json_output:
        return click.echo(config.to_json())
    click.echo(
        "Computed project configuration for %s" % click.style(project_dir, fg="cyan")
    )
    for section, options in config.as_tuple():
        click.secho(section, fg="cyan")
        click.echo("-" * len(section))
        click.echo(
            tabulate(
                [
                    (name, "=", "\n".join(value) if isinstance(value, list) else value)
                    for name, value in options
                ],
                tablefmt="plain",
            )
        )
        click.echo()
    return None

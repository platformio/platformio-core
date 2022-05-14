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

import json
import os

import click
from tabulate import tabulate

from platformio import fs
from platformio.project.config import ProjectConfig
from platformio.project.exception import NotPlatformIOProjectError
from platformio.project.helpers import is_platformio_project, load_build_metadata


@click.command("data", short_help="Dump data intended for IDE extensions/plugins")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option("-e", "--environment", multiple=True)
@click.option("--json-output", is_flag=True)
def project_data_cmd(project_dir, environment, json_output):
    if not is_platformio_project(project_dir):
        raise NotPlatformIOProjectError(project_dir)
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
        config.validate(environment)
        environment = list(environment or config.envs())

    if json_output:
        return click.echo(json.dumps(load_build_metadata(project_dir, environment)))

    for envname in environment:
        click.echo("Environment: " + click.style(envname, fg="cyan", bold=True))
        click.echo("=" * (13 + len(envname)))
        click.echo(
            tabulate(
                [
                    (click.style(name, bold=True), "=", json.dumps(value, indent=2))
                    for name, value in load_build_metadata(project_dir, envname).items()
                ],
                tablefmt="plain",
            )
        )
        click.echo()

    return None

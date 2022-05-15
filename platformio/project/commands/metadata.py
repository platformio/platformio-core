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
from platformio.package.commands.install import install_project_dependencies
from platformio.project.config import ProjectConfig
from platformio.project.helpers import load_build_metadata


@click.command(
    "metadata", short_help="Dump metadata intended for IDE extensions/plugins"
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option("--json-output", is_flag=True)
@click.option("--json-output-path", type=click.Path(resolve_path=True))
def project_metadata_cmd(project_dir, environments, json_output, json_output_path):
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
        config.validate(environments)
        environments = list(environments or config.envs())
        build_metadata = load_build_metadata(project_dir, environments)

    if not json_output:
        install_project_dependencies(
            options=dict(
                project_dir=project_dir,
                environments=environments,
            )
        )
        click.echo()

    if json_output or json_output_path:
        if json_output_path:
            if os.path.isdir(json_output_path):
                json_output_path = os.path.join(json_output_path, "metadata.json")
            with open(json_output_path, mode="w", encoding="utf8") as fp:
                json.dump(build_metadata, fp)
            click.secho(f"Saved metadata to the {json_output_path}", fg="green")
        if json_output:
            click.echo(json.dumps(build_metadata))
        return

    for envname, metadata in build_metadata.items():
        click.echo("Environment: " + click.style(envname, fg="cyan", bold=True))
        click.echo("=" * (13 + len(envname)))
        click.echo(
            tabulate(
                [
                    (click.style(name, bold=True), "=", json.dumps(value, indent=2))
                    for name, value in metadata.items()
                ],
                tablefmt="plain",
            )
        )
        click.echo()

    return

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

from platformio.project.dependency_lock import LOCK_FILENAME, generate_project_lock


@click.command("lock", short_help="Record installed registry packages in a lockfile")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False),
)
@click.option("-e", "--environment", "environments", multiple=True)
def project_lock_cmd(project_dir, environments):
    lock = generate_project_lock(project_dir, environments)
    path = os.path.join(project_dir, LOCK_FILENAME)
    with click.open_file(path, mode="w", encoding="utf8", atomic=True) as stream:
        json.dump(lock, stream, indent=2, sort_keys=True)
        stream.write("\n")
    click.echo(f"Saved {path}")

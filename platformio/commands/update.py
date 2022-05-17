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

import click


@click.command(
    "update",
    short_help="Update installed platforms, packages and libraries",
    hidden=True,
)
@click.option("--core-packages", is_flag=True, help="Update only the core packages")
@click.option(
    "-c",
    "--only-check",
    is_flag=True,
    help="DEPRECATED. Please use `--dry-run` instead",
)
@click.option(
    "--dry-run", is_flag=True, help="Do not update, only check for the new versions"
)
def cli(*_, **__):
    click.secho(
        "This command is deprecated and will be removed in the next releases. \n"
        "Please use `pio pkg update` instead.",
        fg="yellow",
    )

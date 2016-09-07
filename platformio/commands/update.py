# Copyright 2014-present PlatformIO <contact@platformio.org>
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

from platformio.commands.lib import lib_update as cmd_lib_update
from platformio.commands.platform import platform_update as cmd_platform_update
from platformio.managers.lib import LibraryManager
from platformio.pioplus import pioplus_update


@click.command(
    "update", short_help="Update installed Platforms, Packages and Libraries")
@click.option(
    "-c",
    "--only-check",
    is_flag=True,
    help="Do not update, only check for new version")
@click.pass_context
def cli(ctx, only_check):
    click.echo("Platform Manager")
    click.echo("================")
    ctx.invoke(cmd_platform_update, only_check=only_check)
    pioplus_update()

    click.echo()
    click.echo("Library Manager")
    click.echo("===============")
    ctx.obj = LibraryManager()
    ctx.invoke(cmd_lib_update, only_check=only_check)

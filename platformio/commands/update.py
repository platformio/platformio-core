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

from platformio import app
from platformio.commands.lib import CTX_META_STORAGE_DIRS_KEY
from platformio.commands.lib import lib_update as cmd_lib_update
from platformio.commands.platform import platform_update as cmd_platform_update
from platformio.managers.core import update_core_packages
from platformio.managers.lib import LibraryManager


@click.command(
    "update", short_help="Update installed platforms, packages and libraries"
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
@click.pass_context
def cli(ctx, core_packages, only_check, dry_run):
    # cleanup lib search results, cached board and platform lists
    app.clean_cache()

    only_check = dry_run or only_check

    update_core_packages(only_check)

    if core_packages:
        return

    click.echo()
    click.echo("Platform Manager")
    click.echo("================")
    ctx.invoke(cmd_platform_update, only_check=only_check)

    click.echo()
    click.echo("Library Manager")
    click.echo("===============")
    ctx.meta[CTX_META_STORAGE_DIRS_KEY] = [LibraryManager().package_dir]
    ctx.invoke(cmd_lib_update, only_check=only_check)

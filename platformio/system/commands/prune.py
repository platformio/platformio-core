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

from platformio import fs
from platformio.system.prune import (
    prune_cached_data,
    prune_core_packages,
    prune_platform_packages,
)


@click.command("prune", short_help="Remove unused data")
@click.option("--force", "-f", is_flag=True, help="Do not prompt for confirmation")
@click.option(
    "--dry-run", is_flag=True, help="Do not prune, only show data that will be removed"
)
@click.option("--cache", is_flag=True, help="Prune only cached data")
@click.option(
    "--core-packages", is_flag=True, help="Prune only unnecessary core packages"
)
@click.option(
    "--platform-packages",
    is_flag=True,
    help="Prune only unnecessary development platform packages",
)
def system_prune_cmd(force, dry_run, cache, core_packages, platform_packages):
    if dry_run:
        click.secho(
            "Dry run mode (do not prune, only show data that will be removed)",
            fg="yellow",
        )
        click.echo()

    reclaimed_cache = 0
    reclaimed_core_packages = 0
    reclaimed_platform_packages = 0
    prune_all = not any([cache, core_packages, platform_packages])

    if cache or prune_all:
        reclaimed_cache = prune_cached_data(force, dry_run)
        click.echo()

    if core_packages or prune_all:
        reclaimed_core_packages = prune_core_packages(force, dry_run)
        click.echo()

    if platform_packages or prune_all:
        reclaimed_platform_packages = prune_platform_packages(force, dry_run)
        click.echo()

    click.secho(
        "Total reclaimed space: %s"
        % fs.humanize_file_size(
            reclaimed_cache + reclaimed_core_packages + reclaimed_platform_packages
        ),
        fg="green",
    )

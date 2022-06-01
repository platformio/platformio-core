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
from operator import itemgetter

import click
from tabulate import tabulate

from platformio import fs
from platformio.package.manager.core import remove_unnecessary_core_packages
from platformio.package.manager.platform import remove_unnecessary_platform_packages
from platformio.project.helpers import get_project_cache_dir


def prune_cached_data(force=False, dry_run=False, silent=False):
    reclaimed_space = 0
    if not silent:
        click.secho("Prune cached data:", bold=True)
        click.echo(" - cached API requests")
        click.echo(" - cached package downloads")
        click.echo(" - temporary data")
    cache_dir = get_project_cache_dir()
    if os.path.isdir(cache_dir):
        reclaimed_space += fs.calculate_folder_size(cache_dir)
        if not dry_run:
            if not force:
                click.confirm("Do you want to continue?", abort=True)
            fs.rmtree(cache_dir)
    if not silent:
        click.secho("Space on disk: %s" % fs.humanize_file_size(reclaimed_space))
    return reclaimed_space


def prune_core_packages(force=False, dry_run=False, silent=False):
    if not silent:
        click.secho("Prune unnecessary core packages:", bold=True)
    return _prune_packages(force, dry_run, silent, remove_unnecessary_core_packages)


def prune_platform_packages(force=False, dry_run=False, silent=False):
    if not silent:
        click.secho("Prune unnecessary development platform packages:", bold=True)
    return _prune_packages(force, dry_run, silent, remove_unnecessary_platform_packages)


def _prune_packages(force, dry_run, silent, handler):
    if not silent:
        click.echo("Calculating...")
    items = [
        (
            pkg,
            fs.calculate_folder_size(pkg.path),
        )
        for pkg in handler(dry_run=True)
    ]
    items = sorted(items, key=itemgetter(1), reverse=True)
    reclaimed_space = sum(item[1] for item in items)
    if items and not silent:
        click.echo(
            tabulate(
                [
                    (
                        pkg.metadata.spec.humanize(),
                        str(pkg.metadata.version),
                        fs.humanize_file_size(size),
                    )
                    for (pkg, size) in items
                ],
                headers=["Package", "Version", "Size"],
            )
        )
    if not dry_run:
        if not force:
            click.confirm("Do you want to continue?", abort=True)
        handler(dry_run=False)
    if not silent:
        click.secho("Space on disk: %s" % fs.humanize_file_size(reclaimed_space))
    return reclaimed_space


def calculate_unnecessary_system_data():
    return (
        prune_cached_data(force=True, dry_run=True, silent=True)
        + prune_core_packages(force=True, dry_run=True, silent=True)
        + prune_platform_packages(force=True, dry_run=True, silent=True)
    )

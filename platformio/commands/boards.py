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

import click
from tabulate import tabulate

from platformio import fs
from platformio.compat import dump_json_to_unicode
from platformio.managers.platform import PlatformManager


@click.command("boards", short_help="Embedded Board Explorer")
@click.argument("query", required=False)
@click.option("--installed", is_flag=True)
@click.option("--json-output", is_flag=True)
def cli(query, installed, json_output):  # pylint: disable=R0912
    if json_output:
        return _print_boards_json(query, installed)

    grpboards = {}
    for board in _get_boards(installed):
        if query and not any(
            query.lower() in str(board.get(k, "")).lower()
            for k in ("id", "name", "mcu", "vendor", "platform", "frameworks")
        ):
            continue
        if board["platform"] not in grpboards:
            grpboards[board["platform"]] = []
        grpboards[board["platform"]].append(board)

    terminal_width, _ = click.get_terminal_size()
    for (platform, boards) in sorted(grpboards.items()):
        click.echo("")
        click.echo("Platform: ", nl=False)
        click.secho(platform, bold=True)
        click.echo("=" * terminal_width)
        print_boards(boards)
    return True


def print_boards(boards):
    click.echo(
        tabulate(
            [
                (
                    click.style(b["id"], fg="cyan"),
                    b["mcu"],
                    "%dMHz" % (b["fcpu"] / 1000000),
                    fs.format_filesize(b["rom"]),
                    fs.format_filesize(b["ram"]),
                    b["name"],
                )
                for b in boards
            ],
            headers=["ID", "MCU", "Frequency", "Flash", "RAM", "Name"],
        )
    )


def _get_boards(installed=False):
    pm = PlatformManager()
    return pm.get_installed_boards() if installed else pm.get_all_boards()


def _print_boards_json(query, installed=False):
    result = []
    for board in _get_boards(installed):
        if query:
            search_data = "%s %s" % (board["id"], json.dumps(board).lower())
            if query.lower() not in search_data.lower():
                continue
        result.append(board)
    click.echo(dump_json_to_unicode(result))
